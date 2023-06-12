"""Custom TorchServe model handler for YOLOv5 models.
"""
from ts.torch_handler.base_handler import BaseHandler
from typing import Union, List
import numpy as np
import base64
import torch
import torchvision.transforms as tf
import torchvision
import io
from PIL import Image


def is_base64(sb: Union[str, bytearray, bytes]) -> bool:
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        if isinstance(sb, bytearray):
            sb_bytes = bytes(sb)
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False


class ModelHandler(BaseHandler):
    """
    A custom model handler implementation.
    """

    IMG_SIZE = 640
    """Image size (px). Images will be resized to this resolution before inference.
    """

    def __init__(self):
        # call superclass initializer
        super().__init__()

    def preprocess(self, data: List[torch.Tensor]) -> torch.Tensor:
        """Converts input images to float tensors.

        Args:
            data (List): Input data from the request in the form of a list of image tensors.

        Returns:
            Tensor: single Tensor of shape [BATCH_SIZE, 3, IMG_SIZE, IMG_SIZE]
        """
        images = []

        transform = tf.Compose([
            tf.ToTensor(),
            tf.Resize((self.IMG_SIZE, self.IMG_SIZE))
        ])

        # load images
        # taken from https://github.com/pytorch/serve/blob/master/ts/torch_handler/vision_handler.py

        # handle if images are given in base64, etc.
        for row in data:
            # Compat layer: normally the envelope should just return the data
            # directly, but older versions of Torchserve didn't have envelope.
            image = row.get("data") or row.get("body")
            if is_base64(image):
                # if the image is a string of bytesarray.
                image = base64.b64decode(image)

            # If the image is sent as bytesarray
            if isinstance(image, (bytearray, bytes)):
                image = Image.open(io.BytesIO(image))
            else:
                # if the image is a list
                image = torch.FloatTensor(image)

            # force convert to tensor
            # and resize to [IMG_SIZE, IMG_SIZE]
            image = transform(image)

            images.append(image)

        # convert list of equal-size tensors to single stacked tensor
        # has shape BATCH_SIZE x 3 x IMG_SIZE x IMG_SIZE
        images_tensor = torch.stack(images).to(self.device)

        return images_tensor

    def postprocess(self, inference_output: List[object]) -> List[object]:
        # perform NMS (nonmax suppression) on model outputs
        pred = non_max_suppression(inference_output[0])

        # initialize empty list of detections for each image
        detections = [[] for _ in range(len(pred))]

        for i, image_detections in enumerate(pred):  # axis 0: for each image
            for det in image_detections:  # axis 1: for each detection
                # x1,y1,x2,y2 in normalized image coordinates (i.e. 0.0-1.0)
                xyxy = det[:4] / self.IMG_SIZE
                # confidence value
                conf = det[4].item()
                # index of predicted class
                class_idx = int(det[5].item())
                # get label of predicted class
                # if missing, then just return class idx
                label = self.mapping.get(str(class_idx), class_idx)

                detections[i].append({
                    "x1": xyxy[0].item(),
                    "y1": xyxy[1].item(),
                    "x2": xyxy[2].item(),
                    "y2": xyxy[3].item(),
                    "confidence": conf,
                    "class": label
                })

        # format each detection
        return detections


def non_max_suppression(prediction, conf_thres=0.25, iou_thres=0.45, classes=None, agnostic=False, multi_label=False,
                        labels=(), max_det=300) -> List[object]:
    """
    Runs Non-Maximum Suppression (NMS) on inference results
    NMS is a computer vision method that selects a single entity out of many overlapping entities

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    number_classes = prediction.shape[2] - 5  # number of classes
    boxes_candidates = prediction[..., 4] > conf_thres  # candidates

    # Checks
    non_max_suppression_parameters_checks(conf_thres, iou_thres)

    # Settings
    # (pixels) minimum and maximum box width and height
    min_wh, max_wh = 2, 4096
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 10.0  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= number_classes > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    output = [torch.zeros((0, 6), device=prediction.device)
              ] * prediction.shape[0]
    for index, inference in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # inference[((inference[..., 2:4] < min_wh) | (inference[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        inference = inference[boxes_candidates[index]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[index]):
            label = labels[index]
            v = torch.zeros((len(label), number_classes + 5), device=inference.device)
            v[:, :4] = label[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(label)), label[:, 0].long() + 5] = 1.0  # cls
            inference = torch.cat((inference, v), 0)

        # If none remain process next image
        if not inference.shape[0]:
            continue

        # Compute conf
        inference[:, 5:] *= inference[:, 4:5]  # conf = obj_conf * cls_conf

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = convert_box_definition(inference[:, :4])

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (inference[:, 5:] > conf_thres).nonzero(as_tuple=False).T
            inference = torch.cat((box[i], inference[i, j + 5, None], j[:, None].float()), 1)
        else:  # best class only
            conf, j = inference[:, 5:].max(1, keepdim=True)
            inference = torch.cat((box, conf, j.float()), 1)[
                conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            inference = inference[(inference[:, 5:6] == torch.tensor(classes, device=inference.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(inference).all():
        #     inference = inference[torch.isfinite(inference).all(1)]

        # Check shape
        number_boxes = inference.shape[0]  # number of boxes
        if not number_boxes:  # no boxes
            continue
        elif number_boxes > max_nms:  # excess boxes
            # sort by confidence
            inference = inference[inference[:, 4].argsort(descending=True)[:max_nms]]

        # Batched NMS
        classes = inference[:, 5:6] * (0 if agnostic else max_wh)  # classes
        # boxes (offset by class), scores
        boxes, scores = inference[:, :4] + classes, inference[:, 4]
        i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        if merge and (1 < number_boxes < 3E3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,number_boxes) * boxes(number_boxes,4)
            iou = torchvision.box_iou(
                boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            inference[i, :4] = torch.mm(weights, inference[:, :4]).float(
            ) / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[index] = inference[i]

    return output


def non_max_suppression_parameters_checks(conf_thres, iou_thres):
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'


def convert_box_definition(inference):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = inference.clone() if isinstance(inference, torch.Tensor) else np.copy(inference)
    y[:, 0] = inference[:, 0] - inference[:, 2] / 2  # top left inference
    y[:, 1] = inference[:, 1] - inference[:, 3] / 2  # top left y
    y[:, 2] = inference[:, 0] + inference[:, 2] / 2  # bottom right inference
    y[:, 3] = inference[:, 1] + inference[:, 3] / 2  # bottom right y
    return y
