#!/usr/bin/env bash

BASE_DIR=checkpoints
mkdir -p $BASE_DIR

## human attributes
#mkdir -p $BASE_DIR/human_attr
#wget -O $BASE_DIR/human_attr/PPHGNet_small_person_attribute_954_infer.tar https://bj.bcebos.com/v1/paddledet/models/pipeline/PPHGNet_small_person_attribute_954_infer.tar
#tar -xvf $BASE_DIR/human_attr/PPHGNet_small_person_attribute_954_infer.tar -C $BASE_DIR/human_attr
#
## vehicle attributes
#mkdir -p $BASE_DIR/vehicle_attr
#wget -O $BASE_DIR/vehicle_attr/vehicle_attribute_model.zip https://bj.bcebos.com/v1/paddledet/models/pipeline/vehicle_attribute_model.zip
#unzip $BASE_DIR/vehicle_attr/vehicle_attribute_model.zip -d $BASE_DIR/vehicle_attr
#
## mivolo
#mkdir -p $BASE_DIR/mivolo
#gdown https://variety.com/wp-content/uploads/2023/04/MCDNOHA_SP001.jpg -O $BASE_DIR/mivolo/jennifer_lawrence.jpg
#gdown https://drive.google.com/uc?id=1CGNCkZQNj5WkP3rLpENWAOgrBQkUWRdw -O $BASE_DIR/mivolo
#gdown https://drive.google.com/uc?id=11i8pKctxz3wVkDBlWKvhYIh7kpVFXSZ4 -O $BASE_DIR/mivolo
#
## inpaiting anything
#mkdir -p $BASE_DIR/inpaiting_anything/big-lama/models
#mkdir -p dst_dir
#gdown https://drive.google.com/uc?id=1orZY4bcSAukoo9KhdBpxRxJlkm6IORLx -O $BASE_DIR/inpaiting_anything/
#gdown https://drive.google.com/uc?id=1ZfKal2o7zZUfjCFYGmKz9w1BLwU4TYX7 -O $BASE_DIR/inpaiting_anything/
#gdown https://drive.google.com/uc?id=1F6aP4DI_FjVXG9CSBTa-Avp7CMPJM8k0 -O $BASE_DIR/inpaiting_anything/big-lama
#gdown https://drive.google.com/uc?id=1d5M-c5Ij8kMGx6aeCmnTKQhf5zWYAyi0 -O $BASE_DIR/inpaiting_anything/big-lama/models
