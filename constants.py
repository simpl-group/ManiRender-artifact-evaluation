# -*- coding:utf-8 -*-

import sys
import os
import warnings
from typing import List
from functools import wraps
import time
from multiprocessing import (
    Process,
    Queue,
    Manager,
)
from tqdm import tqdm

try:
    import torch

    warnings.filterwarnings('ignore')

    device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
    GPU = torch.device('cuda:0') if torch.cuda.is_available() else None
    CPU = torch.device('cpu')
    torch.manual_seed(1)
except:
    # warnings.warn("No torch library!")
    device = 'cpu'
    CPU = 'cpu'
    GPU = None

INF = 9999999999
BOTTOM = "⊥"
sys.setrecursionlimit(99999)

PROJECT_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(PROJECT_DIR, "benchmarks")
ARC_DIR = os.path.join(DATASET_DIR, "arc")
LATTICE_FILE_DIR = os.path.join(PROJECT_DIR, "order_theory", "dump_lattice")  # lattice dump directory
# lattice type
PERSON = "Person"
VEHICLE = "Vehicle"
TEXT = "Text"
MIX = "Mix"
TERM_NUM = 5  # for ImageEye's union/intersection
EXECUTION_TIME = 1
TIMEOUT = 180

NODE_LABEL_FUNCS = {
    'default': lambda x: x,
    'set': lambda x: '{' + ','.join(map(str, x)) + '}' if isinstance(x, list) else x,
    'interval': lambda x: ('[' if x[1] else '(') + str(x[0]) + ', ' + str(x[-1]) + (']' if x[2] else ')') \
        if isinstance(x, List) else x,
}

CODOMAINS = {
    VEHICLE: {
        'Color': ["Yellow", "Orange", "Green", "Gray", "Red", "Blue", "White", "Golden", "Brown", "Black"],
        "Type": ["Sedan", "Suv", "Van", "Hatchback", "MPV", "Pickup", "Bus", "Truck", "Estate", "Motor"]
    },
    PERSON: {
        "Male": [True, False],
        "Age": [0, 100],  # dynamic
        "Orientation": ["Front", "Back", "Side"],
        "Glasses": [True, False],
        "Hat": [True, False],
        "HoldObjectsInFront": [True, False],
        "Bag": ["BackPack", "ShoulderBag", "HandBag", "NoBag"],
        "TopStyle": ["UpperStride", "UpperLogo", "UpperPlaid", "UpperSplice", "NoTopStyle"],
        "BottomStyle": ["BottomStripe", "BottomPattern", "NoBottomStyle"],
        "UpperBody": ["ShortSleeve", "LongSleeve", "LongCoat", "UnkUpperBody"],
        "LowerBody": ["Trousers", "Shorts", "SkirtDress", "UnkLowerBody"],
        "Boots": [True, False],
    },
    TEXT: {
        "Empty": [True, False],
        "PureNumber": [True, False],
        "PureAlphabet": [True, False],
        "Length": [0, 100],  # dynamic
        "StartsWith": [True, False],  # dynamic
        "EndsWith": [True, False],  # dynamic
        "In": [True, False],  # dynamic
        "Regex": [True, False],  # dynamic
    }
}

CLS2IDS = {
    'Text': [6, 7, 17, 33, 34, 35, 36, 37, 38, 39],
    'Vehicle': [0, 1, 2, 3, 4, 5, 40, 41, 42, 43, 53, 54, 55, 80, 81, 82, 83, 84, 85, 86],
    'Person': [8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 44, 45, 46,
               47, 48, 49, 50, 51, 52, 56, 57, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 71, 73, 74, 75, 87, 88, 89, 90,
               91, 92, 93, 94, 95, 96, 97, 98, 99],
    'Mix': [20, 21, 58, 59, 70, 72, 76, 77, 78, 79],
}


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time

        print(f'\033[1;32;40mFunction `{func.__name__}` took {total_time:.2f} (s).\033[0m')
        return result

    return timeit_wrapper


def execute(func, args, times=EXECUTION_TIME, timeout=TIMEOUT):
    manager = Manager()
    queue = manager.Queue()

    prog = None
    timecosts = []
    others = {}
    for _ in range(times):
        queue.empty()

        proc = Process(target=func, args=(*args, queue))
        proc.start()

        start = time.time()
        while time.time() - start <= timeout:
            if not proc.is_alive():
                break
            time.sleep(0.1)
        else:
            proc.terminate()
            proc.join()

        try:
            prog, timecost, others = [queue.get() for _ in range(queue.qsize())]
            timecosts.append(timecost)
        except:
            return None, [timeout] * times, others
    return prog, timecosts, others
