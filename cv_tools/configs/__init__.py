# -*- coding: utf-8 -*-

import os

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "checkpoints")

HUMAN_ATTR_DIR = os.path.join(CONFIG_DIR, "human_attr")
HUMAN_ATTR_CONFIG = os.path.join(HUMAN_ATTR_DIR, "infer_cfg_pphuman.yml")
HUMAN_ATTR_MODEL = os.path.join(HUMAN_ATTR_DIR, "PPHGNet_small_person_attribute_954_infer")

MIVOLO_DIR = os.path.join(CONFIG_DIR, "mivolo")
MIVOLO_IMAGE_FILE = os.path.join(MIVOLO_DIR, "jennifer_lawrence.jpg")
MIVOLO_CHECKPOINT_MODEL = os.path.join(MIVOLO_DIR, "model_imdb_cross_person_4.22_99.46.pth.tar")
MIVOLO_DETECTOR_MODEL = os.path.join(MIVOLO_DIR, "yolov8x_person_face.pt")

VEHICLE_ATTR_DIR = os.path.join(CONFIG_DIR, "vehicle_attr")
VEHICLE_ATTR_CONFIG = os.path.join(VEHICLE_ATTR_DIR, "infer_cfg_ppvehicle.yml")
VEHICLE_ATTR_MODEL = os.path.join(VEHICLE_ATTR_DIR, "vehicle_attribute_model")

INPAINTING_ANYTHING_DIR = os.path.join(CONFIG_DIR, "inpainting_anything")
INPAINTING_ANYTHING_LAMA_CONFIG = os.path.join(INPAINTING_ANYTHING_DIR, "default.yaml")
INPAINTING_ANYTHING_LAMA_MODEL = os.path.join(INPAINTING_ANYTHING_DIR, "big-lama")

SAM_CHECKPOINT_MODEL = os.path.join(INPAINTING_ANYTHING_DIR, "sam_vit_h_4b8939.pth")
