# -*- coding: utf-8 -*-

import cv2
import numpy as np
import torch.cuda

import constants
from cv_tools import configs
from cv_tools.Inpaint_Anything.utils import dilate_mask
from cv_tools.Inpaint_Anything.lama_inpaint import inpaint_img_with_lama
from cv_tools.Inpaint_Anything.stable_diffusion_inpaint import (
    fill_img_with_sd,
    replace_img_with_sd,
)
from PIL import Image


class Inpainter:
    def __init__(self, device):
        self.lama_config = configs.INPAINTING_ANYTHING_LAMA_CONFIG
        self.lama_ckpt = configs.INPAINTING_ANYTHING_LAMA_MODEL
        self.device = device

    def remove(self, img: np.ndarray, mask: np.ndarray,
               file: str = None, dilate_factor=15, **kwargs):
        mask = mask.astype(np.uint8) * 255
        mask = dilate_mask(mask, dilate_factor)
        if torch.cuda.is_available() and self.device == constants.GPU:
            torch.cuda.empty_cache()
        new_img = inpaint_img_with_lama(img, mask, self.lama_config, self.lama_ckpt, device=self.device)
        if file is not None:
            print(file)
            cv2.imwrite(file, new_img)
        return new_img

    def recolor(self, img: np.ndarray, mask: np.ndarray, color: str,
                file: str = None, vis_result=False, dilate_factor=15, **kwargs):
        mask = mask.astype(np.uint8) * 255
        mask = dilate_mask(mask, dilate_factor)
        if torch.cuda.is_available() and self.device == constants.GPU:
            torch.cuda.empty_cache()
        prompt = f"recolor in {color}"
        # print(prompt)
        new_img = fill_img_with_sd(img, mask, prompt, device=self.device)
        if file is not None:
            print(file)
            cv2.imwrite(file, new_img)
        return new_img

    def replace(self, img: np.ndarray, mask: np.ndarray, prompt: str,
                file: str = None, dilate_factor=15, **kwargs):
        mask = mask.astype(np.uint8) * 255
        mask = dilate_mask(mask, dilate_factor)
        if torch.cuda.is_available() and self.device == constants.GPU:
            torch.cuda.empty_cache()
        # print(f"image shape: {img.shape} {img.dtype}, mask shape: {mask.shape} {mask.dtype}")
        new_img = replace_img_with_sd(img, mask, prompt, device=self.device)
        new_img = Image.fromarray(new_img.astype(np.uint8))
        new_img = np.array(new_img)
        if file is not None:
            print(file)
            cv2.imwrite(file, new_img)
        return new_img

    def fill(self, img: np.ndarray, mask: np.ndarray, prompt: str,
             file: str = None, dilate_factor=50, **kwargs):
        mask = mask.astype(np.uint8) * 255
        mask = dilate_mask(mask, dilate_factor)
        if torch.cuda.is_available() and self.device == constants.GPU:
            torch.cuda.empty_cache()
        # print(f"image shape: {img.shape} {img.dtype}, mask shape: {mask.shape} {mask.dtype}")
        new_img = fill_img_with_sd(img, mask, prompt, device=self.device)
        new_img = Image.fromarray(new_img.astype(np.uint8))
        new_img = np.array(new_img)
        if file is not None:
            print(file)
            cv2.imwrite(file, new_img)
        return new_img
