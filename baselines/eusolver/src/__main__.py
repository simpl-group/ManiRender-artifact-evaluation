# -*- coding:utf-8 -*-


import sys

sys.path.append("../thirdparty/libeusolver/build")

import os
import json
import time
from typing import *
from parsers.parser import stripComments, sexpParser
from benchmarks import synthesize
from collections import defaultdict
from multiprocessing import (
    Process, Manager, Queue, cpu_count,
)
from lark_parser import Parser
from tqdm import tqdm
import shutil

DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath("../../..")
INPUT_DIR = OUTPUT_DIR = os.path.join(PROJECT_DIR, "benchmarks")

PERSON = "Person"
VEHICLE = "Vehicle"
TEXT = "Text"
EUSOLVER = "eusolver"
SAVE_FLAG = False
EXECUTION_TIME = 1
TIMEOUT = 180

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--timeout', type=int, default=TIMEOUT)
parser.add_argument('--num_cores', type=int, default=cpu_count())
args = parser.parse_args()


def eusolver_synthesize(script):
    # print(script)
    bm = stripComments(script.split('\n'))
    bmExpr = sexpParser.parseString(bm, parseAll=True).asList()[0]
    out = synthesize(bmExpr)
    if out is None:
        return "No Program"
    else:
        return out[0]


class ScriptWriter:
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
            "Regex": None,  # dynamic
        }
    }
    OBJ = "OBJ"

    def __init__(self, **kwargs):
        self.functions = {}
        self.constants = {}
        for genre, functions in self.CODOMAINS.items():
            self.functions[genre] = {}
            self.constants[genre] = {}
            for func_name, codomain in functions.items():
                if codomain is None:
                    # dynamic functions which require users to define
                    if func_name == "Age":
                        # codomain = [str(i) for i in range(101)]
                        pass
                    elif func_name == "Length":
                        # codomain = [str(i) for i in range(21)]
                        pass
                    else:
                        continue
                    for suffix in ["Less", "Greater", "Eq"]:
                        func = f"{func_name}{suffix}"
                        self.functions[genre][func] = f"({func} x Start{func_name})"
                    # dynamic define codomain for Age and Length
                    # self.constants[genre][func] = f"(Start{func_name} Int ({' '.join(codomain)}))"
                elif codomain == ["True", "False"]:
                    self.register_func(genre, func_name)
                else:
                    self.register_func(genre, func_name, codomain)

    def register_func(self, genre, func, codomain=None):
        if codomain is None:
            self.functions[genre][func] = f"({func} x)"
        else:
            self.functions[genre][func] = f"({func} x Start{func})"
            codomain = " ".join([f'"{cod}"' for cod in codomain])
            self.constants[genre][func] = f"(Start{func} String ({codomain}))"

    def unregister_func(self, genre, func):
        if func in self.functions[genre]:
            self.functions[genre].pop(func)
        if func in self.constants[genre]:
            self.constants[genre].pop(func)

    def encode_data(self, file):
        data = {}
        with open(file, 'r') as reader:
            for line in reader:
                line = json.loads(line)
                data[line["id"]] = {"id": line["id"], "cls": line["cls"]}
                if line["cls"] == VEHICLE or line["cls"] == PERSON:
                    data[line["id"]].update({key: line[key] for key in self.CODOMAINS[line["cls"]].keys()})
                    if line["cls"] == PERSON:
                        data[line["id"]]["Age"] = int(data[line["id"]]["Age"])
                elif line["cls"] == TEXT:
                    attr_values = {
                        "Context": line["Context"],
                        # "Empty": "true" if len(line["Context"]) == 0 else "false",
                        # "PureNumber": "true" if str.isdigit(line["Context"]) else "false",
                        # "PureAlphabet": "true" if str.isalpha(line["Context"]) else "false",
                        "Empty": len(line["Context"]) == 0,
                        "PureNumber": str.isdigit(line["Context"]),
                        "PureAlphabet": str.isalpha(line["Context"]),
                        "Length": len(line["Context"]),
                    }
                    data[line["id"]].update(attr_values)
                else:
                    raise NotImplementedError(f'Unknown class {line["cls"]}')
        return data

    def generate_script(self, pos_samples: List, neg_samples: List, cls, parameters=None):
        functions = []
        for genre, funcs in self.functions.items():
            if genre != cls:
                continue
            functions.append(f"\t\t\t; {genre}")
            for func in funcs.values():
                functions.append("\t\t\t" + func)
            # functions.append(f"\t\t\t\n")
        functions = "\n".join(functions)
        constants = []
        for genre, consts in self.constants.items():
            if genre != cls:
                continue
            constants.append(f"\t\t;{genre}")
            for const in consts.values():
                constants.append("\t\t" + const)
            # constants.append(f"\t\t\n")
        constants = "\n".join(constants)
        declares = ["; +"] + [f"(declare-var x{pos['id']} OBJ)" for pos in pos_samples]
        declares += ["; -"] + [f"(declare-var x{pos['id']} OBJ)" for pos in neg_samples]
        declares = "\n".join(declares)
        facts = []
        if parameters is not None:
            facts.append(f"; userdefined args = {str(parameters)}")
        for pos in pos_samples:
            pos = str(pos).replace('\'', '"')
            facts.append(f"(constraint (= (Respect {pos}) true))")
        facts.append("")
        for neg in neg_samples:
            neg = str(neg).replace('\'', '"')
            facts.append(f"(constraint (= (Respect {neg}) false))")
        facts = "\n".join(facts)
        script = f"""
(set-logic OBJ)

; ∀ x ∈ POS. Respect(x) = true
; ∀ x ∈ NEG. Respect(x) = false
(synth-fun Respect ((x OBJ)) Bool
    (
        (Start Bool (
            ; Or/And/Not
            (Or Start Start)
            (And Start Start)
            (Not Start)

            ; userdefined functions
{functions}
        ))

        ; terminals
{constants}
    )
)

; I/O
{declares}

; facts
{facts}

(check-synth)
""".strip()
        return script

    def dump(self, script, file):
        with open(file, 'w') as writer:
            print(script, file=writer)


def encode_task(file):
    with open(file, 'r') as reader:
        tasks = [json.loads(line) for line in reader]
    return tasks


def update_attributes(data: Dict, parameters: Dict, swriter: ScriptWriter):
    pop_keys = defaultdict(list)

    # define Age codomain
    age_codomain = list(set(obj["Age"] for id, obj in data.items() if obj["cls"] == PERSON))
    if len(age_codomain) == 0:
        age_codomain = list(range(101))
    else:
        age_codomain = sorted(age_codomain)
    age_codomain = map(str, age_codomain)
    swriter.constants[PERSON]["Age"] = f"(StartAge Int ({' '.join(age_codomain)}))"

    # define Length codomain
    length_codomain = list(set(len(obj["Context"]) for id, obj in data.items() if obj["cls"] == TEXT))
    if len(length_codomain) == 0:
        length_codomain = list(range(101))
    else:
        length_codomain = sorted(length_codomain)
    length_codomain = map(str, length_codomain)
    swriter.constants[TEXT]["Length"] = f"(StartLength Int ({' '.join(length_codomain)}))"

    for genre, args in parameters.items():
        pop_keys[genre] = []
        if genre == VEHICLE or genre == PERSON:
            pass
        elif genre == TEXT:
            for attr, value in args.items():
                if attr in {"In", "StartsWith", "EndsWith", "Regex"}:
                    swriter.register_func(genre, attr, codomain=value)
                    # for id, obj in filter(lambda id_obj: id_obj[1]["cls"] == TEXT, data.items()):
                    #     data[id][attr] = value in obj["Context"]
                    # pop_keys[genre].append(attr)
                else:
                    raise NotImplementedError
        else:
            raise NotImplementedError(f'Unknown class {genre}')
    return data, pop_keys


def remove_attributes(data: Dict, pop_keys: Dict, swriter: ScriptWriter):
    # pop Age, Length codomains
    swriter.constants[PERSON].pop("Age")
    swriter.constants[TEXT].pop("Length")

    for genre, attrs in pop_keys.items():
        # unregister dynamic functions/constants
        for attr in attrs:
            swriter.unregister_func(genre, attr)
        # pop dynamic attributes
        for id, obj in filter(lambda id_obj: id_obj[1]["cls"] == genre, data.items()):
            for attr in attrs:
                obj.pop(attr)
        data[id] = obj
    return data


def process(data_file, task, file_prefix, parser: Parser = None, queue: Queue = None):
    start = time.time()
    # load data
    swriter = ScriptWriter()
    data = swriter.encode_data(data_file)

    # script_dir = os.path.join(OUTPUT_DIR, idx, EUSOLVER)
    # os.makedirs(script_dir, exist_ok=True)

    if task['parameters'] is not None:
        data, pop_keys = update_attributes(data, task['parameters'], swriter)

    # separate samples by class
    POS = [data[idx] for idx in task["positive"] if idx in data]
    NEG = [data[idx] for idx in task["negative"] if idx in data]

    progs = {}
    scripts = {}
    for cls in [VEHICLE, TEXT, PERSON]:
        # synthesize
        positives = [pos for pos in POS if pos["cls"] == cls]
        negatives = [neg for neg in NEG if neg["cls"] == cls]
        if len(positives) == 0 and len(negatives) == 0:
            progs[cls] = None
        elif len(positives) != 0 and len(negatives) == 0:
            progs[cls] = True
        elif len(positives) == 0 and len(negatives) != 0:
            progs[cls] = False
        else:
            scripts[cls] = swriter.generate_script(positives, negatives, cls, task['parameters'])
            # execution
            progs[cls] = eusolver_synthesize(scripts[cls])
    timecost = round(time.time() - start, 4)

    classes = []
    for cls in [VEHICLE, TEXT, PERSON]:
        if cls not in scripts:
            continue
        classes.append(cls)
        file = f"{file_prefix}.{cls}.sl"
        # save eusolver script
        os.makedirs(os.path.dirname(file), exist_ok=True)
        swriter.dump(scripts[cls], file=file)

    if parser is not None:
        info = {
            "classes": classes,
            "correct": None,
            "wrong": None,
            "#correct": None,
            "#wrong": None,
            "#groundtruth": len(task['groundtruth']),
        }
        groundtruth = set(task['groundtruth'])
        coverage = set()
        for cls in [VEHICLE, TEXT, PERSON]:
            if cls not in scripts:
                continue
            # progs[cls] = f"(Not {progs[cls]})"
            func = parser.parse(progs[cls])
            for idx, line in data.items():
                if line['cls'] != cls:
                    continue
                if func(line, cls=cls):
                    coverage.add(idx)
        info["correct"] = sorted(coverage & groundtruth)
        info["#correct"] = len(info["correct"])
        info["wrong"] = sorted(coverage - groundtruth)
        info["#wrong"] = len(info["wrong"])
    else:
        info = {}

    if queue is None:
        return progs, timecost, info
    else:
        queue.put(progs)
        queue.put(timecost)
        queue.put(info)


def execute(func, args, times=EXECUTION_TIME, timeout=TIMEOUT):
    manager = Manager()
    queue = manager.Queue()

    prog = None
    timecosts = []
    info = {}
    for _ in tqdm(range(times)):
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
            prog, timecost, info = [queue.get() for _ in range(queue.qsize())]
            timecosts.append(timecost)
        except:
            return None, [timeout] * times, {}
    return prog, timecosts, info


def run(outfile, func, parameters: List):
    with open(outfile, 'w') as writer:
        for params in parameters:
            task_file, data_file, task, file_prefix, parser, timeout = params
            prog, timecosts, info = execute(func, (data_file, task, file_prefix, parser), timeout=timeout)
            # prog, timecosts, info = func(data_file, task, file_prefix, parser)
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
    cd src
    python __main__.py
    """
    outfile = os.path.join(OUTPUT_DIR, f'results.{EUSOLVER}')
    parser = Parser()
    parameters = []
    for idx in map(str, range(1, 21)):
        task_file = os.path.join(INPUT_DIR, idx, f'image{idx}.tasks')
        tasks = encode_task(file=task_file)
        for task_idx, task in enumerate(tasks, start=1):
            data_file = os.path.join(INPUT_DIR, idx, f'image{idx}.objs')
            file_prefix = os.path.join(INPUT_DIR, idx, EUSOLVER, f"task{task_idx}")
            parameters.append([task_file, data_file, task, file_prefix, parser, args.timeout])
    # parameters = [parameters[6]]
    # NUM_CORES = 1
    parallel(outfile, process, parameters, num_workers=args.num_cores)
