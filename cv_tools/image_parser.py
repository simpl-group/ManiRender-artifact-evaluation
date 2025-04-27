# -*- coding: utf-8 -*-

import json
import os
from collections import defaultdict
from PIL import Image, ImageDraw
import cv2
import numpy as np
import supervision as sv

import utils
from constants import DATASET_DIR


class ImageParser:
    _color = [
        (27, 158, 119),
        (217, 95, 2),
        (117, 112, 179),
        (231, 41, 138),
        (102, 166, 30),
        (230, 171, 2),
        (166, 118, 29),
        (102, 102, 102),
    ]
    _thickness = 10
    _subdir = ".objs"

    def __init__(self, img_dir):
        self.DIR = img_dir
        self.INDEX = int(os.path.basename(img_dir))
        self.IMG_FILE = os.path.join(img_dir, f"image{self.INDEX}.jpg")
        self.HEIGHT, self.WIDTH = cv2.imread(self.IMG_FILE).shape[:2]

        # instance segmentation
        self.INST_SEG_FILE = os.path.join(DATASET_DIR, 'data.json')
        self.POLYGONS = self.read_inst_seg(self.INST_SEG_FILE, self.INDEX)
        self.POLYGON_MASKS = self._polygon_to_polygon_mask(self.POLYGONS)
        # object detection
        self.BOXES = self._polygon_mask_to_bouding_box(self.POLYGON_MASKS)
        # self.box_masks =
        self.LABELS = list(self.POLYGONS.keys())
        self.SUBFILES = defaultdict(list)
        start = 1
        for label in self.LABELS:
            os.makedirs(os.path.join(self.DIR, self._subdir, label), exist_ok=True)
            self.SUBFILES[label] = [
                os.path.join(self.DIR, self._subdir, label, f"{idx}.jpg")
                for idx in range(start, start + len(self.POLYGONS[label]))
            ]
            start += len(self.SUBFILES[label])
        self.label_func = {}
        self.DST_FILE = os.path.join(img_dir, f"image{self.INDEX}.objs")

    def _polygon_to_polygon_mask(self, polygons):
        polygon_masks = defaultdict(list)
        for label, polygon in polygons.items():
            polygon_masks[label] = [
                sv.polygon_to_mask(np.array(gon), (self.WIDTH, self.HEIGHT)).astype(np.bool_)
                for gon in polygon
            ]
        return polygon_masks

    def _polygon_mask_to_bouding_box(self, polygon_masks, extra=0.):
        boxes = defaultdict(list)
        for label, masks in polygon_masks.items():
            boxes[label] = sv.mask_to_xyxy(np.array(masks)).astype(np.int_).tolist()
        return boxes

    def read_inst_seg(self, file, index):
        with open(file, 'r') as reader:
            seg_data = json.load(reader)
        annotations = seg_data[index - 1]['annotations'][0]['result']
        out = defaultdict(list)
        for ann in annotations:
            WIDTH, HEIGHT = ann['original_width'], ann['original_height']
            ann = ann['value']
            label = str.lower(ann['polygonlabels'][0])
            polygon = ann['points']
            polygon = [(int(x * WIDTH / 100.), int(y * HEIGHT / 100.)) for (x, y) in polygon]
            out[label].append(polygon)
        return out

    def show_bounding_boxes(self, labels=None, text_config=(0.9, 4)):
        img = cv2.imread(self.IMG_FILE)
        if labels is not None:
            keys = list(self.BOXES.keys())
            for k in filter(lambda x: x not in labels, keys):
                self.BOXES.pop(k)
        count = 1
        for idx, (cls, boxes) in enumerate(self.BOXES.items(), start=1):
            for box in boxes:
                cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), self._color[idx], self._thickness)
                cv2.putText(img, f"{cls}-{count}", (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            text_config[0], (36, 255, 12), text_config[1])
                count += 1
        dst_file = os.path.join(self.DIR, f"image{self.INDEX}_box.jpg")
        cv2.imwrite(dst_file, img)

    def show_polygon_masks(self, labels=None):
        img = cv2.imread(self.IMG_FILE)
        if labels is not None:
            keys = list(self.POLYGON_MASKS.keys())
            for k in filter(lambda x: x not in labels, keys):
                self.POLYGON_MASKS.pop(k)
        for idx, (cls, masks) in enumerate(self.POLYGON_MASKS.items()):
            for mask in masks:
                masked_img = np.where(mask[..., None], self._color[idx], img).astype(np.uint8)
                img = cv2.addWeighted(img, 0.3, masked_img, 0.7, 0)
        dst_file = os.path.join(self.DIR, f"image{self.INDEX}_mask.jpg")
        cv2.imwrite(dst_file, img)

    def show_borders(self, text_config=(0.9, 4)):
        img = cv2.imread(self.IMG_FILE)
        # count = 1
        for idx, (cls, polygons) in enumerate(self.POLYGONS.items()):
            for polygon in polygons:
                polygon = np.array(polygon, np.int32)
                polygon = polygon.reshape((-1, 1, 2))
                cv2.polylines(img, [polygon], isClosed=True, color=(0, 165, 255), thickness=10)
                # cv2.putText(img, f"{cls}-{count}", (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                #             text_config[0], (36, 255, 12), text_config[1])
                # count += 1
        dst_file = os.path.join(self.DIR, f"image{self.INDEX}_border.jpg")
        cv2.imwrite(dst_file, img)

    def store_objs(self):
        img = cv2.imread(self.IMG_FILE)
        for label, boxes in self.BOXES.items():
            for idx, ((min_x, min_y, max_x, max_y), subfile) in enumerate(zip(boxes, self.SUBFILES[label])):
                subimg = img[min_y:max_y, min_x:max_x]
                cv2.imwrite(subfile, subimg)
                # resize
                file_size = os.path.getsize(subfile) / 1024
                while file_size > 100:
                    subimg = cv2.imread(subfile)
                    size = (subimg.shape[1] // 2, subimg.shape[0] // 2)
                    subimg = cv2.resize(subimg, size, interpolation=cv2.INTER_LANCZOS4)
                    cv2.imwrite(subfile, subimg)
                    file_size = os.path.getsize(subfile) / 1024

    def register_func(self, func_mapping: dict):
        for label, func in func_mapping.items():
            self.label_func[label] = func

    def dumps(self, dst_file):
        with open(dst_file, 'w') as writer:
            idx = 1
            for label in self.LABELS:
                # label = "Plate"
                for file, polygon, box in zip(self.SUBFILES[label], self.POLYGONS[label], self.BOXES[label]):
                    try:
                        # file = '/home/yang/Dropbox/codes/ImageEditor/benchmarks/1/.objs/Plate/5.jpg'
                        attrs = self.label_func[label](file)
                        if len(attrs) == 0:
                            attrs = {}
                        else:
                            attrs = attrs[0]
                            attrs = {name: getattr(attrs, name) for name in attrs._fields}
                    except Exception as err:
                        print(f"\033[1;31;40mERROR: {err}\033[0m")
                        print((file, polygon, box))
                        attrs = {}
                    attrs = {
                        'id': idx,
                        'box': box,
                        'polygons': polygon,
                        'position': ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2),
                        'file': file,
                        'cls': str.upper(label[0]) + label[1:],
                        **attrs,
                    }
                    print(json.dumps(attrs, ensure_ascii=False), file=writer)
                    idx += 1
