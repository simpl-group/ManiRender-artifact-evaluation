# -*- coding:utf-8 -*-

import functools
import math
import operator
import os
import random
import cv2

import numpy as np
from PIL import Image, ImageDraw

np.random.seed(1)
random.seed(1)

import constants

makedir = lambda x: os.makedirs(x, exist_ok=True)

foldl_mul = lambda x: functools.reduce(operator.mul, x, 1)


def show_img(data, N=100):
    data = np.asarray(data, dtype=np.uint8)
    data = np.kron(data, np.ones((N, N, 1)))
    # data = np.repeat(data[:, :, None], 3, axis=-1)

    img = Image.fromarray(data, 'RGB')
    img.show()


def polygon_to_mask(width, height, polygon):
    # polygon = [[int(x), int(y)] for (x, y) in polygon]
    polygon = [tuple(xy) for xy in polygon]
    img = Image.new('L', (width, height), 0)
    ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
    mask = np.array(img).astype(np.bool_)
    return mask


def resize_image(infile, outfile=None, size=(1920, 1080)):
    img = cv2.imread(infile)
    w, h = img.shape[:2]
    if not (w <= size[0] and h <= size[1]):
        ratio = min(size[0] / h, size[1] / w)
        size = (int(h * ratio), int(w * ratio))
        # print(size)
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    if outfile is not None:
        cv2.imwrite(outfile, img)
    return img


def put_mosaic(img, bbox, mask):
    def do_mosaic(img, x, y, w, h, neighbor=9):
        for i in range(0, h, neighbor):
            for j in range(0, w, neighbor):
                rect = [j + x, i + y]
                color = img[i + y][j + x].tolist()
                left_up = (rect[0], rect[1])
                x2 = rect[0] + neighbor - 1
                y2 = rect[1] + neighbor - 1
                if x2 > x + w:
                    x2 = x + w
                if y2 > y + h:
                    y2 = y + h
                right_down = (x2, y2)
                cv2.rectangle(img, left_up, right_down, color, -1)
        return img

    # h, w = img.shape[:-2]
    x_min, y_min, x_max, y_max = bbox
    w = x_max - x_min
    h = y_max - y_min
    out_img = do_mosaic(img.copy(), x_min, y_min, w, h)
    img[mask, ...] = out_img[mask, ...]
    return img


def blur_image(img, mask, kernel=(20, 20)):
    out_img = cv2.blur(img.copy(), kernel)
    img[mask, ...] = out_img[mask, ...]
    return img


if __name__ == '__main__':
    src_img = "/home/yang/Downloads/image25.jpg"
    dst_img = "/home/yang/Documents/GitHub/ManiRender/benchmarks/25/image25.jpg"
    resize_image(src_img, dst_img)
