# -*- coding: utf-8 -*-

import argparse
import sys
import os
from typing import (
    NamedTuple,
    List,
    Optional,
)

import cv2
from paddleocr import PaddleOCR

import constants
from cv_tools import configs
from cv_tools.PaddleDetection.deploy.pipeline.pipeline import Pipeline


class MiVolo:

    def __init__(self):
        cv_tools_path = os.path.dirname(os.path.abspath(__file__))

        mivolo_path = os.path.join(cv_tools_path, "mivolo")
        if mivolo_path not in sys.path:
            sys.path.append(mivolo_path)

        from mivolo.predictor import Predictor

        parser = self.get_parser()
        args = parser.parse_args()
        args.detector_weights = configs.MIVOLO_DETECTOR_MODEL
        args.checkpoint = configs.MIVOLO_CHECKPOINT_MODEL
        args.device = constants.device
        # args.draw = True
        self.predictor = Predictor(args, verbose=False)

    def get_parser(self):
        parser = argparse.ArgumentParser(description="PyTorch MiVOLO Inference")
        parser.add_argument("--input", type=str, default=None, required=False, help="image file or folder with images")
        parser.add_argument("--output", type=str, default=None, required=False, help="folder for output results")
        parser.add_argument("--detector-weights", type=str, default=None, required=False,
                            help="Detector weights (YOLOv8).")
        parser.add_argument("--checkpoint", default="", type=str, required=False, help="path to mivolo checkpoint")
        parser.add_argument(
            "--with-persons", action="store_true", default=True,
            help="If set model will run with persons, if available"
        )
        parser.add_argument(
            "--disable-faces", action="store_true", default=False,
            help="If set model will use only persons if available"
        )
        parser.add_argument("--draw", action="store_true", default=False, help="If set, resulted images will be drawn")
        parser.add_argument("--device", default="cuda", type=str, help="Device (accelerator) to use.")
        return parser

    def run(self, image):
        if isinstance(image, str):
            image = cv2.imread(image)
        detected_objects, _ = self.predictor.recognize(image)
        cls = detected_objects.yolo_results.names

        results = []
        for idx, (box, age, gender, gender_score) in enumerate(
                zip(detected_objects.yolo_results.boxes, detected_objects.ages, detected_objects.genders,
                    detected_objects.gender_scores)):
            label = cls[box.cls.item()]
            box = list(map(int, box.xyxy.squeeze(dim=0).tolist()))
            gender = gender == 'male'
            if len(results) > 0 and results[-1][-3:] == [age, gender, gender_score] and label == 'face':
                results[-1][2] = label
                results[-1][3] = box
            else:
                results.append([label, box, None, None, age, gender, gender_score])
        return results


"""
# TODO:
#  - image inpainting , https://github.com/search?q=Image+inpainting&type=repositories, controlnet
#  - pose estimate
#  - Emotion recognition
#  - facial expressions

if Orientation = Back, then Glasses, FaceBox, (Face)Emotion, FaicalExpr are unknown 
[ShortSleeve; LongSleeve] mutual exclusive
[UpperStride; UpperLogo; UpperPlaid; UpperSplice] mutual exclusive
at least 1 attribute from ['LowerStripe', 'LowerPattern', 'LongCoat', 'Trousers', 'Shorts', 'Skirt&Dress'] is True
['Trousers', 'Shorts', 'Skirt&Dress'] mutual exclusive 

attributes:
    - Gender
    - Age: Less than 18; 18-60; Over 60
    - Orientation: Front; Back; Side
    - Accessories: Glasses; Hat; None
    - HoldObjectsInFront: Yes; No
    - Bag: BackPack; ShoulderBag; HandBag; No Bag
    - TopStyle: UpperStride; UpperLogo; UpperPlaid; UpperSplice; Unknown
    - BottomStyle: LowerStripe; LowerPattern; Unknown
    - ShortSleeve: Yes; No
    - LongSleeve: Yes; No
    - LongCoat: Yes; No
    - Trousers: Yes; No
    - Shorts: Yes; No
    - Skirt&Dress: Yes; No
    - Boots: Yes; No
    - 性别：男、女
    - 年龄：小于18、18-60、大于60
    - 朝向：朝前、朝后、侧面
    - 配饰：眼镜、帽子、无
    - 正面持物：是、否
    - 包：双肩包、单肩包、手提包
    - 上衣风格：带条纹、带logo、带格子、拼接风格
    - 下装风格：带条纹、带图案
    - 短袖上衣：是、否
    - 长袖上衣：是、否
    - 长外套：是、否
    - 长裤：是、否
    - 短裤：是、否
    - 短裙&裙子：是、否
    - 穿靴：是、否
    
"""
HumanAttribute = NamedTuple("HumanAttribute", [
    # ('PersonBox', List[int]),
    # ('PersonConfidence', float),
    ('FaceBox', Optional[List[int]]),
    ('Male', bool),
    # ('GenderConfidence', float),
    ('Age', float),
    ('Orientation', str),
    ('Glasses', bool),
    ('Hat', bool),
    ('HoldObjectsInFront', bool),
    ('Bag', str),
    ('TopStyle', Optional[str]),
    ('BottomStyle', Optional[str]),
    ('ShortSleeve', bool),
    ('LongSleeve', bool),
    ('LongCoat', bool),
    ('Trousers', bool),
    ('Shorts', bool),
    ('SkirtDress', bool),
    ('Boots', bool),
])


class HumanAttr:
    """
    ref: https://github.com/PaddlePaddle/cv_tools.PaddleDetection/blob/release/2.6/deploy/pipeline/docs/tutorials/pphuman_attribute_en.md
    """

    def __init__(self, device):
        from cv_tools.PaddleDetection.deploy.pipeline.cfg_utils import argsparser, merge_cfg

        parser = argsparser()
        FLAGS = parser.parse_args([
            "--config", configs.HUMAN_ATTR_CONFIG,
            "--device", str(device),
        ])
        FLAGS.image_file = None
        cfg = merge_cfg(FLAGS)
        cfg['ATTR']['model_dir'] = configs.HUMAN_ATTR_MODEL
        self.model = Pipeline(FLAGS, cfg)
        self.mivolo_model = MiVolo()

    def run(self, file: str, vis_result=False, **kwargs) -> List[HumanAttribute]:

        def shift_box(box, xmin, ymin):
            box[1], box[3] = box[1] + ymin, box[3] + ymin
            box[0], box[2] = box[0] + xmin, box[2] + xmin
            return box

        self.model.predictor.cfg['visual'] = vis_result
        self.model.predictor.run([file])
        raw_image = cv2.imread(file)
        # person_num = self.model.predictor.pipeline_res.res_dict['det']['boxes_num']
        boxes = self.model.predictor.pipeline_res.res_dict['det']['boxes']
        attributes = self.model.predictor.pipeline_res.res_dict['attr']['output']

        out = []
        for box, attrs in zip(boxes, attributes):
            # images[ymin:ymax, xmin:xmax, :], [xmin, ymin, xmax, ymax], org_rect
            new_box = box
            crop_image = raw_image
            # cv2.imshow("", crop_image)
            # cv2.waitKey(0)
            persons = self.mivolo_model.run(crop_image)
            if len(persons) == 0:
                # cv2.imshow("", crop_image)
                # cv2.waitKey(0)
                # assert ValueError()
                person_box = new_box
                gender = attrs[0] == "Male"
                gender_score = 0.99
                face_box = age = None
            else:
                # if too many persons, only consider the 1st one
                _, person_box, _, face_box, age, gender, gender_score = persons[0]
                person_box = shift_box(person_box, new_box[0], new_box[1])
                if face_box is not None:
                    face_box = shift_box(face_box, new_box[0], new_box[1])

                # crop_image = raw_image[person_box[1]:person_box[3], person_box[0]:person_box[2], :]
                # cv2.imshow("", crop_image)
                # cv2.waitKey(0)

            upper = attrs[7][len('Upper: '):].strip().split(' ')
            if len(upper) == 1:
                top_style = None
            else:
                top_style = upper[1]
            long_sleeve = upper[0] == "LongSleeve"
            short_sleeve = upper[0] == "ShortSleeve"
            lowers = attrs[8][len("Lower: "):].strip().split()
            bottom_style = None
            long_coat = trousers = shorts = skirtdress = False
            for lower in lowers:
                if lower in ['LowerStripe', 'LowerPattern']:
                    bottom_style = lower
                else:
                    long_coat = lower == 'LongCoat'
                    trousers = lower == 'Trousers'
                    shorts = lower == 'Shorts'
                    skirtdress = lower == 'Skirt&Dress'

            out.append(
                HumanAttribute(
                    # PersonBox=person_box,PersonConfidence=float(box[1]),GenderConfidence=gender_score,
                    FaceBox=face_box, Age=age, Male=gender, Orientation=attrs[2],
                    Glasses=attrs[3][len("Glasses: "):] == "True", Hat=attrs[4][len("Hat: "):] == "True",
                    HoldObjectsInFront=attrs[5][len("HoldObjectsInFront: "):] == "True", Bag=attrs[6],
                    TopStyle=top_style, LongSleeve=long_sleeve, ShortSleeve=short_sleeve, BottomStyle=bottom_style,
                    LongCoat=long_coat, Trousers=trousers, Shorts=shorts, SkirtDress=skirtdress,
                    Boots=not (attrs[9] == 'No boots')
                )
            )
        return out


"""
# color - 车辆颜色
- "yellow"
- "orange"
- "green"
- "gray"
- "red"
- "blue"
- "white"
- "golden"
- "brown"
- "black"

# car type - 车型
- "sedan" 三厢车
- "suv" 
- "van" 面包车
- "hatchback" 两厢车
- "mpv"
- "pickup" 皮卡
- "bus"
- "truck"
- "estate" 大篷车
- "motor"
- "UNKNOWN"
"""

VehicleAttribute = NamedTuple("VehicleAttribute", [
    # ('Confidence', float),
    # ('Box', List[int]),
    ('Color', Optional[str]),
    ('Genre', Optional[str]),
])


class VehicleAttr:
    """
    ref: https://github.com/PaddlePaddle/cv_tools.PaddleDetection/blob/release/2.6/deploy/pipeline/docs/tutorials/ppvehicle_attribute_en.md
    """

    def __init__(self, device):
        from cv_tools.PaddleDetection.deploy.pipeline.cfg_utils import argsparser, merge_cfg

        parser = argsparser()
        FLAGS = parser.parse_args([
            "--config", configs.VEHICLE_ATTR_CONFIG,
            "--device", device,
        ])
        FLAGS.image_file = None
        cfg = merge_cfg(FLAGS)
        cfg['VEHICLE_ATTR']['model_dir'] = configs.VEHICLE_ATTR_MODEL
        self.model = Pipeline(FLAGS, cfg)

    def run(self, file: str, vis_result=False, **kwargs) -> List[VehicleAttribute]:
        self.model.predictor.cfg['visual'] = vis_result
        self.model.predictor.run([file])
        # raw_image = cv2.imread(file)
        boxes = self.model.predictor.pipeline_res.res_dict['det']['boxes']
        attributes = self.model.predictor.pipeline_res.res_dict['vehicle_attr']['output']
        results = []
        for box, attrs in zip(boxes, attributes):
            # confidence = float(box[1])
            # new_box = list(map(int, box[2:].tolist()))
            color = attrs[0][len("Color: "):]
            color = str.upper(color[0]) + color[1:]
            genre = attrs[1][len("Type: "):]
            genre = str.upper(genre[0]) + genre[1:]
            if genre == "Unknown":
                genre = None
            # results.append(VehicleAttribute(Confidence=confidence, Box=new_box, Color=color, Genre=genre))
            results.append(VehicleAttribute(Color=color, Genre=genre))
        return results


TextAttribute = NamedTuple("TextAttribute", [
    # ('Confidence', float),
    # ('Border', List[List[int]]),
    ('Context', str),
    # ('Color', Optional[str]),
    # ('Genre', Optional[str]),
])


class OCRer:
    def __init__(self, device):
        self.models = {
            "en": PaddleOCR(lang="en", use_gpu=device == constants.GPU),
            "zh": PaddleOCR(lang="ch", use_gpu=device == constants.GPU),
            "kr": PaddleOCR(lang="korean", use_gpu=device == constants.GPU),
            "jp": PaddleOCR(lang="japan", use_gpu=device == constants.GPU),
        }

    def run(self, file: str, vis_result=False, **kwargs) -> List[TextAttribute]:
        image = cv2.imread(file)
        langs = kwargs.get("langs", ["en"])
        results = []
        for lang in langs:
            boards = self.models[lang].ocr(image, cls=True)
            if boards[0] is None:
                results.append(TextAttribute(Context=""))
            else:
                for border, (context, confidence) in boards[0]:
                    # border = [list(map(int, point)) for point in border]
                    # results.append(TextAttribute(Confidence=confidence, Border=border, Context=context))
                    results.append(TextAttribute(Context=context))
        return results


class Extractor:
    def __init__(self):
        self.human_attr_model: Optional[HumanAttr] = None
        self.vehicle_attr_model: Optional[VehicleAttr] = None
        self.text_attr_model: Optional[OCRer] = None

    def init_human_attr(self, device=constants.CPU):
        self.human_attr_model = HumanAttr(str(device))

    def init_vehicle_attr(self, device=constants.CPU):
        self.vehicle_attr_model = VehicleAttr(str(device))

    def init_text_attr(self, device=constants.CPU):
        self.text_attr_model = OCRer(str(device))


def annotate_image(image, info, box, draw_line=False):
    if draw_line:
        border = box + [box[0]]
        for start, end in zip(border[:-1], border[1:]):
            cv2.line(image, start, end, (36, 255, 12), 2)
        cv2.putText(image, info, (border[0][0], border[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.1, (36, 255, 12), 2)
    else:
        # images[ymin:ymax, xmin:xmax, :], [xmin, ymin, xmax, ymax], org_rect
        xmin, ymin, xmax, ymax = box
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (36, 255, 12), 2)
        cv2.putText(image, info, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.1, (36, 255, 12), 2)


if __name__ == '__main__':
    src_file = "/benchmarks/batch/realworld/1/image1.jpg"
    sep_index = src_file.rfind(os.path.sep)
    dst_file = os.path.join(src_file[:sep_index], f"ann_{src_file[sep_index + 1:]}")
    dst_info_file = src_file[:src_file.rfind(".")] + ".info"

    image_extractor = Extractor()

    # image_extractor.init_human_attr()
    # persons = image_extractor.human_attr_model.run(src_file)
    # print(f"#person: {len(persons)}")
    # # print(persons)
    #
    image_extractor.init_vehicle_attr()
    # vehicles = image_extractor.vehicle_attr_model.run(src_file)
    # print(f"#car: {len(vehicles)}")
    # # print(vehicles)
    #
    # image_extractor.init_text_attr()
    # texts = image_extractor.text_attr_model.run(src_file)
    # print(f"#text: {len(texts)}")
    # # print(vehicles)
