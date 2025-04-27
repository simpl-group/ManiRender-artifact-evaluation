# -*- coding:utf-8 -*-

import json

from .dsl import Extractor
from constants import (
    PERSON, VEHICLE, TEXT
)
from typing import Dict, Any, Sequence
from collections import defaultdict


def dynamic_class(class_name: str, kwargs: Dict[str, Any] = None):
    def _func(self) -> str:
        # return self.key
        return class_name

    def duplicate(self):
        return self.__class__(self.val, self.output_under, self.output_over)

    kwargs["__str__"] = kwargs["__repr__"] = _func
    kwargs["duplicate"] = duplicate
    cls = type(class_name, (Extractor,), kwargs)
    return cls


class Configuration:
    # a shared Configuration for a synthesis program

    CODOMAINS = {
        VEHICLE: {
            'Color': ["Yellow", "Orange", "Green", "Gray", "Red", "Blue", "White", "Golden", "Brown", "Black"],
            "Type": ["Sedan", "Suv", "Van", "Hatchback", "MPV", "Pickup", "Bus", "Truck", "Estate", "Motor"]
        },
        PERSON: {
            "Male": ["True", "False"],
            "Age": None,  # dynamic 0~100
            "Orientation": ["Front", "Back", "Side"],
            "Glasses": ["True", "False"],
            "Hat": ["True", "False"],
            "HoldObjectsInFront": ["True", "False"],
            "Bag": ["BackPack", "ShoulderBag", "HandBag", "NoBag"],
            "TopStyle": ["UpperStride", "UpperLogo", "UpperPlaid", "UpperSplice", "NoTopStyle"],
            "BottomStyle": ["BottomStripe", "BottomPattern", "NoBottomStyle"],
            "ShortSleeve": ["True", "False"],
            "LongSleeve": ["True", "False"],
            "LongCoat": ["True", "False"],
            "Trousers": ["True", "False"],
            "Shorts": ["True", "False"],
            "SkirtDress": ["True", "False"],
            "Boots": ["True", "False"],
        },
        TEXT: {
            "Empty": ["True", "False"],
            "PureNumber": ["True", "False"],
            "PureAlphabet": ["True", "False"],
            "Length": None,  # dynamic 0~20
            "StartsWith": None,  # dynamic
            "EndsWith": None,  # dynamic
            "In": None,  # dynamic
        }
    }

    def __init__(self):
        self.parameters = None
        self.TERMINALS = set()
        for genre, obj in self.CODOMAINS.items():
            for attr, codomain in obj.items():
                if codomain is not None and codomain != ["True", "False"]:
                    self.TERMINALS.add(attr)
        self.CLASS = None

    def encode_data(self, file):
        data = {}
        with open(file, 'r') as reader:
            for line in reader:
                line = json.loads(line)
                data[line["id"]] = {"id": line["id"], "cls": line["cls"]}
                if line["cls"] == VEHICLE or line["cls"] == PERSON:
                    data[line["id"]].update({key: line[key] for key in self.CODOMAINS[line["cls"]].keys()})
                elif line["cls"] == TEXT:
                    attr_values = {
                        "Context": line["Context"],
                        "Empty": len(line["Context"]),
                        "PureNumber": str.isdigit(line["Context"]),
                        "PureAlphabet": str.isalpha(line["Context"]),
                        "Length": len(line["Context"]),
                    }
                    data[line["id"]].update(attr_values)
                else:
                    raise NotImplementedError(f'Unknown class {line["cls"]}')

                if line["cls"] == PERSON:
                    data[line["id"]]["Age"] = int(data[line["id"]]["Age"])
        return data
