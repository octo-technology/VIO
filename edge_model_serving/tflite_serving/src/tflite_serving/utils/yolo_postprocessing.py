import numpy as np
from typing import List


def yolo_extract_boxes_information(outputs):
    rows = outputs.shape[0]

    boxes = []
    scores = []
    class_ids = []

    for i in range(rows):
        classes_scores = outputs[i][4:]
        max_score, max_class_id = max((v, i) for i, v in enumerate(classes_scores))

        box = [float(outputs[i][0] - (0.5 * outputs[i][2])), float(outputs[i][1] - (0.5 * outputs[i][3])),
               float(outputs[i][0] + (0.5 * outputs[i][2])), float(outputs[i][1] + (0.5 * outputs[i][3]))]
        boxes.append(box)
        scores.append(float(max_score))
        class_ids.append(float(max_class_id))

    return boxes, scores, class_ids


def compute_severities(image: np.array, boxes: List):
    severities = []
    for box in boxes:
        severities.append(compute_box_severity(image, box))
    return severities


def compute_box_severity(image: np.array, box: List):
    x1_pixel_index = int(box[0] * len(image))
    y1_pixel_index = int(box[1] * len(image[0]))
    x2_pixel_index = int(box[2] * len(image))
    y2_pixel_index = int(box[3] * len(image[0]))

    # Reshape to only the pixels in the detection box & as a list of pixels instead of a 2D array of them
    image_detection = image[x1_pixel_index:x2_pixel_index, y1_pixel_index:y2_pixel_index, :]
    image_detection = image_detection.reshape(-1, 3)
    number_of_pixels_in_box = image_detection.shape[0]

    # Filtering out light pixels
    mask_dark_pixels = np.all(image_detection < 0.5, axis=1)
    # Looking at severity as mean darkness
    dark_colors = image_detection[mask_dark_pixels].flatten()
    if dark_colors.size == 0:
        print('no pixels left')
        return 0.09
    else:
        ratio_pixel_dark_box = len(dark_colors) / 3 / number_of_pixels_in_box
        grade_dark_pixels_amount = 3 ** (ratio_pixel_dark_box - 1)
        print(f"pixel ratio = {ratio_pixel_dark_box}")
        print(f"pixel expo = {grade_dark_pixels_amount}")

        grade_mean_darkness = (0.5 - dark_colors.mean()) * 2
        print(f"mean darkness = {grade_mean_darkness}")

        severity = round(0.8 * grade_mean_darkness + 0.2 * grade_dark_pixels_amount, 2)
        print("Severity : ", severity)
        return severity


def nms(boxes, scores, class_ids, score_threshold=0.4, iou_threshold=0.45):
    non_max_suppression_parameters_checks(score_threshold, iou_threshold)

    nms_result_boxes = []
    nms_result_scores = []
    nms_result_classes = []

    # Cut values with low confidence
    scores = np.array(scores)
    mask_low_confidence = scores > score_threshold
    scores = scores[mask_low_confidence].tolist()
    boxes = np.array(boxes)[mask_low_confidence].tolist()
    class_ids = np.array(class_ids)[mask_low_confidence].tolist()

    # Performing the Non-max suppression loop
    while len(boxes) != 0:
        delete_index_list = []

        # Locating & Saving max confidence box
        highest_confidence_index = scores.index(max(scores))
        highest_confidence_box = boxes[highest_confidence_index]

        nms_result_boxes.append(highest_confidence_box)
        nms_result_scores.append(scores[highest_confidence_index])
        nms_result_classes.append(class_ids[highest_confidence_index])
        delete_index_list.append(highest_confidence_index)

        # Iterating to analyse the iou scores
        for index_box, box in enumerate(boxes):
            iou = compute_iou(highest_confidence_box, box)
            if iou > iou_threshold:
                delete_index_list.append(index_box)

        # Rebuild the box list to remove the boxes that were close to the last max score
        boxes = [box for index_box, box in enumerate(boxes) if index_box not in delete_index_list]
        scores = [score for index_score, score in enumerate(scores) if index_score not in delete_index_list]
        class_ids = [class_id for index_class, class_id in enumerate(class_ids) if index_class not in
                     delete_index_list]

    return nms_result_boxes, nms_result_scores, nms_result_classes


def non_max_suppression_parameters_checks(conf_thres, iou_thres):
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'


def compute_iou(box1, box2):
    box1_width = box1[2] - box1[0]
    box1_height = box1[3] - box1[1]
    box2_width = box2[2] - box2[0]
    box2_height = box2[3] - box2[1]

    # Check if centers of boxes are close enough to be intersected
    if ((abs((box1[0] + box1_width / 2) - (box2[0] + box2_width / 2)) < 0.5 * (box2_width + box1_width)) &
            (abs((box1[1] + box1_height / 2) - (box2[1] + box2_height / 2)) < 0.5 * (box2_height + box1_height))):
        intersection_area = ((max(box1[2], box2[2]) - min(box1[0], box2[0])) *
                             (max(box1[3], box2[3]) - min(box1[1], box2[1])))
        union_area = box1_width * box1_height + box2_width * box2_height - intersection_area
        return intersection_area / union_area
    return 0
