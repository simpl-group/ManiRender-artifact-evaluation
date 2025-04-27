# -*- coding:utf-8 -*-

"""
This file to zoom in our segmented objects such that they can be used to finetune GPT-4o.

"""

import os
import glob
from constants import DATASET_DIR
from utils import resize_image
import shutil
import cv2

SRC_DIR = ".objs"
DST_DIR = ".sobjs"


def get_file_size(file):
    return os.path.getsize(file) // 1024


sizes = []
for idx in map(str, range(1, 21)):
    print(idx)
    src_files = glob.glob(os.path.join(DATASET_DIR, idx, SRC_DIR, "*", "*.jpg"))
    for sfile in src_files:
        dfile = sfile.replace(SRC_DIR, DST_DIR)
        os.makedirs(os.path.dirname(dfile), exist_ok=True)
        shutil.copy(sfile, dfile)

        img = cv2.imread(dfile)
        w, h = img.shape[:2]

        file_size = get_file_size(dfile)
        while file_size > 20:
            img = resize_image(dfile, dfile, size=(int(h * 0.9), int(w * 0.9)))
            w, h = img.shape[:2]
            file_size = get_file_size(dfile)
