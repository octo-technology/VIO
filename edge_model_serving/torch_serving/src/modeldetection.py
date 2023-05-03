# -*- coding: utf-8 -*-

import torch
from torchvision import transforms
from utils import *
from PIL import Image, ImageDraw
import copy
import numpy as np


class ModelDetection:
    def __init__(self, checkpoint_pth, dev=None):
        if dev is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            if not (dev == 'cuda' or dev == 'cpu'):
                raise Exception("Niedozwolona wartosc parametru device")
            self.device = dev
        self.start_epoch = 0
        self.__forklift = False
        self.checkpoint = checkpoint_pth
        self.__storage = {  # [x_min, y_min, x_max, y_max, size_full, size_empty, last_update] storage jako klasa////
            'E623': [27, 118, 117, 184, 0, 0, None],
            'E622': [118, 108, 229, 180, 0, 0, None],
            'E621': [234, 92, 366, 176, 0, 0, None],
            'F621': [398, 84, 521, 178, 0, 0, None],
            'F622': [531, 102, 625, 189, 0, 0, None],
            'F623': [638, 119, 708, 201, 0, 0, None],
            'E613': [28, 200, 119, 282, 0, 0, None],
            'E612': [123, 191, 230, 286, 0, 0, None],
            'E611': [238, 184, 364, 289, 0, 0, None],
            'F611': [393, 192, 518, 292, 0, 0, None],
            'F612': [525, 194, 628, 288, 0, 0, None],
            'F613': [630, 205, 707, 284, 0, 0, None],
        }
        self.__spool_types = ['FULL', 'EMPTY']
        self.__picture = None
        self.model = None

    @property
    def forklift(self):
        return self.__forklift

    @property
    def storage(self):
        return copy.deepcopy(self.__storage)

    @property
    def picture(self):
        return self.__picture

    @property
    def spool_types(self):
        return self.__spool_types

    def get_field_by_xy(self, x, y):
        for item in [(k, v) for k, v in self.storage.items()]:
            box_xy = item[1]
            x1, y1, x2, y2 = box_xy[0], box_xy[1], box_xy[2], box_xy[3]
            if x1 < x < x2 and y1 < y < y2:
                return item[0]
        return None

    def storage_zeros(self):
        for key in self.__storage.keys():
            tmp = self.__storage[key]
            tmp[4] = tmp[5] = 0
            self.__storage[key] = tmp


    def load_model(self, cpu=False, model=None):
        try:
            if cpu:
                print(self.checkpoint)
                self.checkpoint = torch.load(self.checkpoint, map_location=torch.device('cpu'))
            else:
                self.checkpoint = torch.load(self.checkpoint)
        except Exception as ex:
            raise FileNotFoundError('Checkpoint not found')

        self.start_epoch = self.checkpoint['epoch'] + 1
        model = self.checkpoint['model']
        model = model.to(self.device)
        model.eval()
        print(f'Model loaded successfully. Device: {self.device}')
        self.model = model

    def detection(self, orig_frame, min_score=0.2, max_overlap=0.5, top_k=50, suppress=None):

        orig_frame = np.asarray(orig_frame)
        # orig_frame = cv2.cvtColor(np.asarray(orig_frame), cv2.COLOR_BGR2RGB)
        orig_frame = orig_frame[:, :, ::-1]
        orig_frame = Image.fromarray(orig_frame, 'RGB')

        res = transforms.Resize((300, 300))
        to_tensor = transforms.ToTensor()
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])

        frame = normalize(to_tensor(res(orig_frame)))
        frame = frame.to(self.device)

        predicted_locs, predicted_scores = self.model(frame.unsqueeze(0))
        
        print(f"Entering postprocess {list(predicted_locs.size())} {list(predicted_scores.size())}")
        
        det_boxes, det_labels, det_scores = self.model.detect_objects(predicted_locs, predicted_scores,
                                                                      min_score=min_score, max_overlap=max_overlap,
                                                                      top_k=top_k)
        
        
        det_boxes = det_boxes[0].to('cpu')
        
        print(det_boxes)

        original_dims = torch.FloatTensor(
            [orig_frame.width, orig_frame.height, orig_frame.width, orig_frame.height]).unsqueeze(0)
        det_boxes = det_boxes * original_dims

        det_labels = [rev_label_map[l] for l in det_labels[0].to('cpu').tolist()]

        if det_labels == ['background']:
            return orig_frame

        annotated_image = orig_frame
        draw = ImageDraw.Draw(annotated_image)
        # font = ImageFont.truetype("./calibril.ttf", 16)
        # font_small = ImageFont.truetype("./calibril.ttf", 10)

        self.storage_zeros()

        # for xy in self.storage:

        for i in range(det_boxes.size(0)):
            if suppress is not None:
                if det_labels[i] in suppress:
                    continue

            box_location = det_boxes[i].tolist()
            x_center = ((box_location[2] - box_location[0]) / 2) + box_location[0]
            y_center = ((box_location[3] - box_location[1]) / 2) + box_location[1]
            draw.rectangle(xy=box_location, outline=label_color_map[det_labels[i]])
            draw.rectangle(xy=[l + 1. for l in box_location], outline=label_color_map[det_labels[i]])

            if "forklift" in det_labels:
                self.__forklift = True
            else:
                self.__forklift = False

            field = self.get_field_by_xy(x_center, y_center)
            if field is not None:
                tmp_list = self.__storage[field]
                if "EMPTY" in det_labels[i].upper():
                    tmp_list[5] += 1
                    self.__storage[field] = tmp_list
                elif "FULL" in det_labels[i].upper():
                    tmp_list[4] += 1
                    self.__storage[field] = tmp_list

            text_location = [box_location[0] + 2., box_location[1] - 1]
            textbox_location = [box_location[0], box_location[1] - 1, box_location[0] + 1 + 4.,
                                box_location[1]]
            # draw.rectangle(xy=textbox_location, fill=label_color_map[det_labels[i]])
            draw.text(xy=text_location, text=det_labels[i].upper(), fill=label_color_map[det_labels[i]])
            draw.text(xy=[x_center, y_center], text='x', fill=label_color_map[det_labels[i]])

        for item in [(k, v) for k, v in self.storage.items()]:
            item = list(item)
            xy = item[1][:4]
            draw.rectangle(xy, outline='#b803ff')
            draw.rectangle(xy=[l + 1. for l in xy], outline="#b803ff")
            draw.rectangle(xy=[l + 2. for l in xy], outline="#b803ff")
            coord = xy
            text_location = [coord[0] + 2., coord[1]-1]#  - text_size[1]]
            textbox_location = [coord[0], coord[1] - 1, coord[0] + 1 + 4.,
                                coord[1]]
            draw.rectangle(xy=textbox_location, fill='#b803ff')
            draw.text(xy=text_location, text=item[0], fill='white')

        del draw
        self.__picture = annotated_image
        return annotated_image


if __name__ == "__main__":
    im = Image.open(r"example_images_OLS/MicrosoftTeams-image_1.png")
    modelDetection = ModelDetection(checkpoint_pth = r"./trained_models/checkpoint_ssd300.pth.tar")
    modelDetection.load_model(cpu=True)
    modelDetection.detection(im).show()
