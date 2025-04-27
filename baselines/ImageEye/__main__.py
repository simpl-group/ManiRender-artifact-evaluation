# -*- coding:utf-8 -*-

import json
import os
import time
import itertools
import re
from typing import *
from constants import (
    VEHICLE, PERSON, TEXT,
    DATASET_DIR,
    EXECUTION_TIME, TIMEOUT,
    Queue, execute,
)
import shutil
from baselines.ImageEye.synthesizer import Synthesizer
# from baselines.ImageEye.dsl import register_numeric_func, set_domain
from baselines.ImageEye.config import Configuration
from constants import PROJECT_DIR
from multiprocessing import (
    Process, cpu_count,
)
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--timeout', type=int, default=TIMEOUT)
parser.add_argument('--num_cores', type=int, default=cpu_count())
args = parser.parse_args()

INPUT_DIR = OUTPUT_DIR = DATASET_DIR
IMAGEEYE = "imageeye"


def update_attributes(data: Dict, parameters: Dict, config: Configuration):
    pop_keys = {}
    if len(parameters) > 0:
        config.parameters = parameters
    for genre, args in parameters.items():
        pop_keys[genre] = set()
        for attr, values in args.items():
            if attr == "In":
                func = lambda x: x in obj["Context"]
            elif attr == "StartsWith":
                func = lambda x: str.startswith(obj["Context"], x)
            elif attr == "EndsWith":
                func = lambda x: str.endswith(obj["Context"], x)
            elif attr == "Regex":
                func = lambda x: re.search(x, obj["Context"]) is not None
            else:
                raise NotImplementedError
            for v in values:
                name = f"{attr}({v})"
                pop_keys[genre].add(name)
                for id, obj in filter(lambda id_obj: id_obj[1]["cls"] == TEXT, data.items()):
                    data[id][name] = func(v)
    return data, pop_keys


def remove_attributes(data: Dict, pop_keys: Dict):
    for genre, attrs in pop_keys.items():
        for id, obj in filter(lambda id_obj: id_obj[1]["cls"] == genre, data.items()):
            for attr in attrs:
                if attr == "In":
                    global IN_SUBSTR
                    IN_SUBSTR = ""
                data[id].pop(attr)
    return data


def process(config, data_file, task, queue: Queue = None):
    start = time.time()
    synthesizer = Synthesizer()
    # load data
    data = config.encode_data(data_file)
    if task['parameters'] is not None:
        data, pop_keys = update_attributes(data, task['parameters'], config)
    all_indices = set(data.keys())
    pos_indices = {idx for idx in task["positive"] if idx in data}
    neg_indices = {idx for idx in task["negative"] if idx in data}
    groundtruth = set(task['groundtruth'])
    # synthesis
    progs = {}
    correct, wrong = [], []
    for cls in [VEHICLE, TEXT, PERSON]:
        config.CLASS = cls
        all_cls_indices = {idx for idx in all_indices if data[idx]["cls"] == cls}
        positives = {idx for idx in pos_indices if data[idx]["cls"] == cls}
        negatives = {idx for idx in neg_indices if data[idx]["cls"] == cls}
        cls_data = {idx: obj for idx, obj in data.items() if obj["cls"] == cls}
        if len(positives) == 0 and len(negatives) == 0:
            progs[cls] = None
        elif len(positives) != 0 and len(negatives) == 0:
            progs[cls] = True
            correct += [idx for idx, line in data.items() if line['cls'] == cls]
        elif len(positives) == 0 and len(negatives) != 0:
            progs[cls] = False
            wrong += [idx for idx, line in data.items() if line['cls'] == cls]
        else:
            prog, _ = synthesizer.synthesize_top_down(
                env=cls_data, eval_cache={},
                output_over=positives, output_under=all_cls_indices - negatives, output_refuted=negatives,
                config=config,
            )
            progs[cls] = str(prog)
            coverage = eval(prog.val)
            correct += sorted(coverage & groundtruth)
            wrong += sorted(coverage - groundtruth)
    config.parameters = None
    timecost = round(time.time() - start, 4)
    info = {
        "correct": sorted(correct),
        "wrong": sorted(wrong),
        "#correct": len(correct),
        "#wrong": len(wrong),
        "#groundtruth": len(task['groundtruth']),
    }
    if queue is None:
        return progs, timecost, info
    else:
        queue.put(progs)
        queue.put(timecost)
        queue.put(info)


def run(outfile, func, parameters: List):
    with open(outfile, 'w') as writer:
        for params in parameters:
            task_file, data_file, task, timeout = params
            config = Configuration()
            # prog, timecosts, info = func(config, data_file, task)
            prog, timecosts, info = execute(func, (config, data_file, task), timeout=timeout)
            log = {"file": task_file[len(PROJECT_DIR) + 1:], **task, "program": prog, "time": timecosts, **info}
            print(json.dumps(log, ensure_ascii=False), file=writer)


def parallel(outfile, func, parameters, num_workers):
    import math
    def divide(lst, partitions):
        chunk_size = math.ceil(len(lst) / partitions)
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    if num_workers == 1:
        run(outfile, process, parameters)
    else:
        parameters = list(divide(parameters, num_workers))
        procs = []
        for worker_idx in range(len(parameters)):
            proc = Process(
                target=run,
                args=(outfile + str(worker_idx), func, parameters[worker_idx]),
            )
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()

        with open(outfile, 'w') as writer:
            for worker_idx in range(len(parameters)):
                infile = outfile + str(worker_idx)
                with open(infile, 'r') as reader:
                    shutil.copyfileobj(reader, writer)
                os.remove(infile)


if __name__ == '__main__':
    """
    cd baseline/ImageEye
    python __main__.py
    """

    outfile = os.path.join(OUTPUT_DIR, f'results.{IMAGEEYE}')
    parameters = []
    for idx in map(str, range(1, 21)):
        task_file = os.path.join(INPUT_DIR, idx, f'image{idx}.tasks')
        with open(task_file, 'r') as reader:
            tasks = [json.loads(line) for line in reader]
        for task_idx, task in enumerate(tasks, start=1):
            data_file = os.path.join(DATASET_DIR, idx, f'image{idx}.objs')
            parameters.append([task_file, data_file, task, args.timeout])
    # parameters = [parameters[31]]
    parallel(outfile, process, parameters, num_workers=args.num_cores)
