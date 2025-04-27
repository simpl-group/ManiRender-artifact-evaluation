# -*- coding:utf-8 -*-

import json
import shutil
import argparse
from collections import OrderedDict, defaultdict
from typing import *
from functools import partial
import re

from constants import *
from search import *
from order_theory.interval_lattice import IntervalLattice
from order_theory.lazy_product_lattice import LazyProductLattice
from order_theory.set_lattice import SetLattice
from multiprocessing import cpu_count

MAX_NUM = 100

parser = argparse.ArgumentParser()
parser.add_argument('--topdown', choices=[0, 1], type=int, default=1)
parser.add_argument('--difference', choices=[0, 1], type=int)
parser.add_argument('--abstraction', choices=[0, 1], type=int)
parser.add_argument('--timeout', type=int, default=TIMEOUT)
parser.add_argument('--num_cores', type=int, default=cpu_count())
args = parser.parse_args()


def set_environment(lattice_dir, file, required_indices):
    static_data = defaultdict(dict)
    lattice_names = defaultdict(set)
    dynamic_data = {VEHICLE: {}, PERSON: {"Age": {}}, TEXT: {"Length": {}, "Context": {}}}
    with open(file, 'r') as reader:
        for line in map(json.loads, reader):
            if line["id"] not in required_indices:
                continue

            if line["cls"] == VEHICLE:
                # color_idx = latttices[VEHICLE]["Color"].encode(line["Color"])
                # type_idx = latttices[VEHICLE]["Type"].encode(line["Type"])
                # statc_data[VEHICLE][line["id"]] = (color_idx, type_idx)
                static_data[VEHICLE][line["id"]] = [line["Color"], line["Type"]]
                lattice_names[VEHICLE] |= {"Color", "Type"}
            elif line["cls"] == PERSON:
                male_idx = line["Male"]
                age_idx = line["Age"]
                ori_idx = line["Orientation"]
                glasses_idx = line['Glasses']
                hat_idx = line['Hat']
                access_idx = access_idx
                hold_idx = line["HoldObjectsInFront"]
                bag_idx = line["Bag"]
                topstyle_idx = line["TopStyle"]
                bottomstyle_idx = line["BottomStyle"]
                upperbody_idx = []
                if line['ShortSleeve']:
                    upperbody_idx.append('ShortSleeve')
                if line['LongSleeve']:
                    upperbody_idx.append('LongSleeve')
                if line['LongCoat']:
                    upperbody_idx.append('LongCoat')
                if len(upperbody_idx) == 0:
                    upperbody_idx.append("UnkUpperBody")
                lowerbody_idx = []
                if line['Trousers']:
                    lowerbody_idx.append('Trousers')
                if line['Shorts']:
                    lowerbody_idx.append('Shorts')
                if line['SkirtDress']:
                    lowerbody_idx.append('SkirtDress')
                if len(lowerbody_idx) == 0:
                    lowerbody_idx.append("UnkLowerBody")
                boots_idx = line["Boots"]
                static_data[PERSON][line["id"]] = [
                    male_idx, age_idx, ori_idx, glasses_idx, hat_idx, hold_idx, bag_idx, topstyle_idx, bottomstyle_idx,
                    upperbody_idx, lowerbody_idx, boots_idx
                ]
                lattice_names[PERSON] |= {"Male", "Age", "Orientation", "Glasses", "Hat", "HoldObjectsInFront", "Bag",
                                          "TopStyle", "BottomStyle", "UpperBody", "LowerBody", "Boots"}

                # dynamically set Age
                dynamic_data[PERSON]["Age"][line["id"]] = int(line['Age'])
            elif line["cls"] == TEXT:
                # empty_idx = latttices[TEXT]["Empty"].encode(len(line["Context"]) == 0)
                # purenumber_idx = latttices[TEXT]["PureNumber"].encode(str.isdigit(line["Context"]))
                # purealphabet_idx = latttices[TEXT]["PureAlphabet"].encode(str.isalpha(line["Context"]))
                # length_idx = None
                # static_data[TEXT][line["id"]] = [empty_idx, purenumber_idx, purealphabet_idx, length_idx]
                static_data[TEXT][line["id"]] = [
                    len(line["Context"]) == 0, str.isdigit(line["Context"]),
                    str.isalpha(line["Context"]), len(line["Context"]),
                ]
                lattice_names[TEXT] |= {"Empty", "PureNumber", "PureAlphabet", "Length"}

                # dynamically set StartsWith/EndsWith/In
                dynamic_data[TEXT]["Length"][line["id"]] = len(line["Context"])
                dynamic_data[TEXT]["Context"][line["id"]] = line["Context"]
            else:
                raise NotImplementedError(f"Unknown class {line['cls']}")

    # build required lattice
    lattices = defaultdict(dict)
    for genre, names in lattice_names.items():
        for name in names:
            if name in {"Age", "Length"}:
                lattices[genre][name] = None  # dynamic lattices
            else:
                dump_file = os.path.join(lattice_dir, genre, f"{name}.lattice")
                if os.path.exists(dump_file):
                    lattices[genre][name] = SetLattice.load(name, os.path.join(lattice_dir, genre))
                else:
                    codomain = CODOMAINS[genre][name]
                    if codomain == ["True", "False"]:
                        codomain = [True, False]
                    lattices[genre][name] = SetLattice.build(name, codomain)
                if lattice_dir is not None:
                    genre_dump_dir = os.path.join(lattice_dir, genre)
                    os.makedirs(genre_dump_dir, exist_ok=True)
                    lattices[genre][name].dump(dump_dir=genre_dump_dir)

    # encoding objs with lattices
    for genre, obj in static_data.items():
        for id, values in obj.items():
            for i, (attr, value) in enumerate(zip(CODOMAINS[genre], values)):
                if lattices[genre][attr] is not None:
                    if isinstance(values[i], list):
                        values[i] = lattices[genre][attr].encode(*values[i])
                    else:
                        values[i] = lattices[genre][attr].encode(values[i])
            static_data[genre][id] = values
    return static_data, dynamic_data


def encode_task(file):
    tasks = []
    with open(file, 'r') as reader:
        for line in map(json.loads, reader):
            tasks.append(line)
    return tasks


def build_lattices(dump=False, dump_dir=None) -> Dict:
    lattices = defaultdict(OrderedDict)
    for genre, attrs in CODOMAINS.items():
        for attr, codomain in attrs.items():
            if codomain is None or attr in {"Age", "Length"}:
                # dynamic
                lattices[genre][attr] = None
            elif codomain is None or attr in {"In", "StartsWith", "EndsWith", "Regex"}:
                continue
            else:
                if dump_dir is not None and os.path.exists(os.path.join(dump_dir, genre, f"{attr}.lattice")):
                    lattices[genre][attr] = SetLattice.load(attr, os.path.join(dump_dir, genre))
                else:
                    lattices[genre][attr] = SetLattice.build(attr, codomain)
                if dump:
                    genre_dump_dir = os.path.join(dump_dir, genre)
                    os.makedirs(genre_dump_dir, exist_ok=True)
                    lattices[genre][attr].dump(dump_dir=genre_dump_dir)
    return lattices


def init_lattices() -> Dict:
    lattice_cache_dir = os.path.join(DATASET_DIR, ".lattices")
    lattices = build_lattices(dump=False, dump_dir=lattice_cache_dir)
    lattices[PERSON]["Age"] = None
    lattices[TEXT] = OrderedDict({
        "Empty": lattices[TEXT]["Empty"],
        "PureNumber": lattices[TEXT]["PureNumber"],
        "PureAlphabet": lattices[TEXT]["PureAlphabet"],
        "Length": None,
    })
    return lattices


def update_attributes(genre, static_data: Dict, dynamic_data: Dict, lattices: Dict[str, Dict],
                      positives: List, negatives: List,
                      parameters: Optional[Dict], **kwargs):
    def encode_interval(value, lattice):
        if value == 0:
            interval = lattice.nodes[1]
        elif value == MAX_NUM:
            interval = lattice.nodes[max(lattice.base_elements)]
        else:
            interval = [value, True, True, value]
        return lattice.encode(interval)

    # build dynamic lattices and their product
    start_time = time.time()
    if genre == VEHICLE:
        product_lattice = LazyProductLattice(name=genre, sublattices=list(lattices.values()))
    elif genre == PERSON:
        age_points = sorted(list({0, MAX_NUM} | set(dynamic_data["Age"].values())))
        lattices["Age"] = IntervalLattice.build("Age", points=age_points)
        product_lattice = LazyProductLattice(name=genre, sublattices=list(lattices.values()))
    elif genre == TEXT:
        length_points = sorted(list({0, MAX_NUM} | set(dynamic_data["Length"].values())))
        lattices["Length"] = IntervalLattice.build("Length", points=length_points)
        names = ["Empty", "PureNumber", "PureAlphabet", "Length"]
        if parameters is not None:
            names += list(parameters.keys())
        product_lattice = LazyProductLattice(name=genre, sublattices=[lattices[name] for name in names])
    else:
        raise NotImplementedError
    build_timecost = round(time.time() - start_time, 4)

    # build data
    if genre == VEHICLE:
        POS = list({static_data[idx] for idx in positives if idx in static_data})
        NEG = list({static_data[idx] for idx in negatives if idx in static_data})
    elif genre == PERSON:
        POS = set()
        for id in filter(lambda x: x in static_data, positives):
            static_data[id][1] = encode_interval(dynamic_data["Age"][id], lattices["Age"])
            POS.add(tuple(static_data[id]))
        POS = list(POS)
        NEG = set()
        for id in filter(lambda x: x in static_data, negatives):
            static_data[id][1] = encode_interval(dynamic_data["Age"][id], lattices["Age"])
            NEG.add(tuple(static_data[id]))
        NEG = list(NEG)
    elif genre == TEXT:
        POS, POS_values = {}, set()
        for id in filter(lambda x: x in static_data, positives):
            ctx = dynamic_data["Context"][id]
            if ctx not in POS_values:
                POS[id] = static_data[id][:4]
                POS[id][-1] = encode_interval(dynamic_data["Length"][id], lattices["Length"])
                POS_values.add(ctx)
        NEG, NEG_values = {}, set()
        for id in filter(lambda x: x in static_data, negatives):
            ctx = dynamic_data["Context"][id]
            if ctx not in NEG_values:
                NEG[id] = static_data[id][:4]
                NEG[id][-1] = encode_interval(dynamic_data["Length"][id], lattices["Length"])
                NEG_values.add(ctx)
        if parameters is not None:
            for i, (attr, args) in enumerate(parameters.items(), start=4):
                if attr == "In":
                    for id in POS.keys():
                        POS[id].append(product_lattice.sublattices[i].encode(args in dynamic_data["Context"][id]))
                    for id in NEG.keys():
                        NEG[id].append(product_lattice.sublattices[i].encode(args in dynamic_data["Context"][id]))
                elif attr == "StartsWith":
                    for id in POS.keys():
                        POS[id].append(
                            product_lattice.sublattices[i].encode(dynamic_data["Context"][id].startswith(args)))
                    for id in NEG.keys():
                        NEG[id].append(dynamic_data["Context"][id].startswith(args))
                elif attr == "EndsWith":
                    for id in POS.keys():
                        POS[id].append(dynamic_data["Context"][id].endswith(args))
                    for id in NEG.keys():
                        NEG[id].append(dynamic_data["Context"][id].endswith(args))
                elif attr == "Regex":
                    raise NotImplementedError
                else:
                    raise NotImplementedError
        POS = list([tuple(pos) for pos in POS.values()])
        NEG = list([tuple(neg) for neg in NEG.values()])
    else:
        raise NotImplementedError

    return product_lattice, build_timecost, POS, NEG


def encode_line(line, parameters, dynamic_data=None):
    def _encode_upperbody(obj):
        upperbody = []
        if obj['ShortSleeve']:
            upperbody.append('ShortSleeve')
        if obj['LongSleeve']:
            upperbody.append('LongSleeve')
        if obj['LongCoat']:
            upperbody.append('LongCoat')
        if len(upperbody) == 0:
            upperbody = ["UnkUpperBody"]
        return upperbody[0]

    def _encode_lowbody(obj):
        lowbody = []
        if obj['Trousers']:
            lowbody.append('Trousers')
        if obj['Shorts']:
            lowbody.append('Shorts')
        if obj['SkirtDress']:
            lowbody.append('SkirtDress')
        if len(lowbody) == 0:
            lowbody = ["UnkLowerBody"]
        return lowbody[0]

    if line["cls"] == VEHICLE:
        out = [line["Color"], line["Type"]]
    elif line["cls"] == PERSON:
        out = [
            line["Male"], int(line["Age"]), line["Orientation"], line["Glasses"], line["Hat"],
            line["HoldObjectsInFront"], line["Bag"], line["TopStyle"], line["BottomStyle"],
            _encode_upperbody(line), _encode_lowbody(line), line["Boots"]
        ]
        if dynamic_data is not None:
            dynamic_data["Age"].append(int(line['Age']))
    elif line["cls"] == TEXT:
        out = [
            len(line["Context"]) == 0, str.isdigit(line["Context"]),
            str.isalpha(line["Context"]), len(line["Context"]),
        ]
        if dynamic_data is not None:
            dynamic_data["Length"].append(len(line["Context"]))
        if line["cls"] in parameters:
            for attr, values in parameters[line["cls"]].items():
                if attr == "StartsWith":
                    func = lambda x: str.startswith(line["Context"], x)
                elif attr == "EndsWith":
                    func = lambda x: str.endswith(line["Context"], x)
                elif attr == "In":
                    func = lambda x: x in line["Context"]
                elif attr == "Regex":
                    func = lambda x: re.search(x, line["Context"]) is not None
                else:
                    raise NotImplementedError
                out += [func(v) for v in values]
    else:
        raise NotImplementedError(f"Unknown class {line['cls']}")
    return out, dynamic_data


def init_env(lattices, file, POS, NEG, parameters={}):
    POS, NEG = set(POS), set(NEG)

    def _encode_objs(file, POS, NEG, parameters):
        static_data = defaultdict(OrderedDict)
        dynamic_data = {"Age": [], "Length": [], "Context": {}}

        pos_samples, neg_samples = defaultdict(list), defaultdict(list)
        with open(file, 'r') as reader:
            for line in map(json.loads, reader):
                if line["id"] not in POS and line["id"] not in NEG:
                    continue
                elif line["id"] in POS and line["id"] in NEG:
                    raise ValueError(f"You have an object (id = {line['id']}) coexists in POS/NEG of the file {file}")

                # if line["id"] in POS and line["id"] in NEG:
                #     raise ValueError(f"You have an object (id = {line['id']}) coexists in POS/NEG of the file {file}")

                # transform data
                static_data[line["cls"]][line["id"]], dynamic_data = encode_line(line, parameters, dynamic_data)

                # classify POS/NEG by line["cls"]
                if line["id"] in POS:
                    pos_samples[line["cls"]].append(line["id"])
                if line["id"] in NEG:
                    neg_samples[line["cls"]].append(line["id"])

            return pos_samples, neg_samples, static_data, dynamic_data

    POS, NEG, static_data, dynamic_data = _encode_objs(file, POS, NEG, parameters)

    def _extend_lattices(lattices, parameters):
        # build
        for attr, values in parameters[TEXT].items():
            for v in values:
                name = f"{attr}_{v}"
                lattices[TEXT][name] = SetLattice.build(name, [True, False])
        return lattices

    start_time = time.time()
    # build dynmaic lattices: Age and Length
    if len(dynamic_data["Age"]) > 0:
        age_codomain = sorted(list(set(dynamic_data["Age"] + [0, 100])))
        lattices[PERSON]["Age"] = IntervalLattice.build("Age", age_codomain)
    if len(dynamic_data["Length"]) > 0:
        length_codomain = sorted(list(set(dynamic_data["Length"] + [0, 100])))
        lattices[TEXT]["Length"] = IntervalLattice.build("Length", length_codomain)
    if parameters is not None and len(parameters) > 0:
        lattices = _extend_lattices(lattices, parameters)
    construction_time = round(time.time() - start_time, 4)

    # encode objects
    def _encode_data(static_data, lattices):
        for genre, objs in static_data.items():
            if genre == VEHICLE:
                pass
            elif genre == PERSON:
                # Age
                for id, obj in objs.items():
                    obj[1] = [obj[1], True, True, obj[1]]
            elif genre == TEXT:
                # Text
                for id, obj in objs.items():
                    obj[3] = [obj[3], True, True, obj[3]]
            elif genre == 'default_factory':
                continue
            else:
                raise NotImplementedError
            for id, obj in objs.items():
                static_data[genre][id] = tuple(l.encode(v) for v, l in zip(obj, lattices[genre].values()))
        return static_data

    static_data = _encode_data(static_data, lattices)
    return POS, NEG, static_data, lattices, construction_time


def get_full_coverage(file, maximals, product_lattices, groundtruth, parameters=None):
    decoded_maximals = {}
    for key, value in maximals.items():
        if isinstance(value, list):
            decoded_maximals[key] = []
            for v in value:
                # bot
                if v == product_lattices[key].bot:
                    continue

                maximal = list(product_lattices[key].decode(v))
                for i, sub_max in enumerate(maximal):
                    if isinstance(sub_max, str):  # interval
                        lhs, rhs = sub_max[0] == '[', sub_max[-1] == ']'
                        min_v, max_v = list(map(int, sub_max[1:-1].split(', ')))
                        interval = list(range(min_v, max_v + 1))
                        if not lhs:
                            interval = interval[1:]
                        if not rhs:
                            interval = interval[:-1]
                        maximal[i] = set(interval)
                maximal = tuple(maximal)
                decoded_maximals[key].append(maximal)
        else:
            decoded_maximals[key] = value

    coverage = set()
    # reload full data
    with open(file, 'r') as reader:
        for line in map(json.loads, reader):
            idx = line['id']
            cls = line['cls']
            if decoded_maximals[cls] is None:
                continue
            line, _ = encode_line(line, parameters)
            if any(all(value in domain for value, domain in zip(line, maximal)) for maximal in decoded_maximals[cls]):
                coverage.add(idx)
    groundtruth = set(groundtruth)
    correct, wrong = sorted(coverage & groundtruth), sorted(coverage - groundtruth)
    return correct, wrong


def process(data_file, task, topdown, difference, abstraction, queue: Queue = None):
    start = time.time()
    lattices = init_lattices()
    # load data
    POS, NEG, data, lattices, construction_time = \
        init_env(lattices, data_file, task["positive"], task["negative"], task['parameters'])
    # classify IO examples
    if not topdown:
        func = find_maximals_by_bottomup  # bottom-up search
    elif topdown and (not difference) and (not abstraction):
        func = find_maximal_by_topdown  # top-down search
    elif topdown and difference and (not abstraction):
        func = partial(find_maximal_by_topdown, difference=True)  # top-down search + difference
    elif topdown and (not difference) and abstraction:
        func = find_maximal_by_abstraction  # top-down search + abstraction
    elif topdown and difference and abstraction:
        func = partial(find_maximal_by_abstraction, difference=True)  # top-down search + difference + abstraction
    else:
        raise NotImplementedError

    progs, maximals, product_lattices = {}, {}, {}
    num_base_lattice = num_base_lattice_node = num_product_lattice = num_product_lattice_node = 0
    for genre in [VEHICLE, PERSON, TEXT]:
        if genre not in data:
            product_lattices[genre] = progs[genre] = maximals[genre] = None
        else:
            pos_ids = list(set([data[genre][idx] for idx in POS[genre]]))
            neg_ids = list(set([data[genre][idx] for idx in NEG[genre]]))

            # # TODO: check conflicts
            # overlap = set(pos_ids) & set(neg_ids)
            # if len(overlap) > 0:
            #     pos_set = defaultdict(set)
            #     for idx in POS[genre]:
            #         pos_set[data[genre][idx]].add(idx)
            #     neg_set = defaultdict(set)
            #     for idx in NEG[genre]:
            #         neg_set[data[genre][idx]].add(idx)
            #     for obj in overlap:
            #         print(task)
            #         print(f"Conflict objs: {pos_set[obj]} {neg_set[obj]}")
            #     raise NotImplementedError

            product_lattices[genre] = product_lattice = \
                LazyProductLattice.build(name=genre, lattices=list(lattices[genre].values()))
            if len(pos_ids) == 0 and len(neg_ids) == 0:
                progs[genre] = maximals[genre] = None
                continue
            elif len(pos_ids) != 0 and len(neg_ids) == 0:
                progs[genre] = True
                maximals[genre] = [product_lattice.top]
            elif len(pos_ids) == 0 and len(neg_ids) != 0:
                progs[genre] = False
                maximals[genre] = [product_lattice.bot]
            else:
                maximals[genre], progs[genre] = func(pos_ids, neg_ids, product_lattice, abstraction=abstraction)
            num_base_lattice += len(product_lattice.sublattices)
            num_base_lattice_node += sum(len(sub_l.nodes) for sub_l in product_lattice.sublattices)
            num_product_lattice += 1
            num_product_lattice_node += product_lattice.num_nodes
    # build, search, execute
    timecost = (construction_time, round(time.time() - start - construction_time, 4), None)

    # get a synthesized program's coverage
    correct, wrong = get_full_coverage(data_file, maximals, product_lattices, task['groundtruth'],
                                       task['parameters'])
    info = {
        "classes": [genre for genre, prog in progs.items() if prog is not None],
        "#plattice": num_product_lattice,
        "#plattice_node": num_product_lattice_node,
        "#lattice": num_base_lattice,
        "#lattice_node": num_base_lattice_node,
        "correct": correct,
        "wrong": wrong,
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
            task_file, data_file, task, topdown, difference, abstraction, timeout = params
            # prog, timecosts, info = func(data_file, task, topdown, difference, abstraction)
            prog, timecosts, info = execute(func, (data_file, task, topdown, difference, abstraction), timeout=timeout)
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
    ablation study: 
        (1) top-down search,
            python __main__.py --difference 0 --abstraction 0
        (2) top-down search + difference,
            python __main__.py --difference 1 --abstraction 0
        (3) top-down search + abstraction,
            python __main__.py --difference 0 --abstraction 1
        (4) top-down search + difference + abstraction
            python __main__.py --difference 1 --abstraction 1
    """
    suffix = []
    if args.difference:
        suffix.append("diff")
    if args.abstraction:
        suffix.append("abst")
    if len(suffix) > 0:
        suffix = "-".join(suffix)
        outfile = os.path.join(DATASET_DIR, f'results.{suffix}.manirender')
    else:
        outfile = os.path.join(DATASET_DIR, f'results.manirender')

    parameters = []
    for idx in map(str, range(1, 21)):
        task_file = os.path.join(DATASET_DIR, idx, f'image{idx}.tasks')
        tasks = encode_task(task_file)
        for task_idx, task in enumerate(tasks, start=1):
            data_file = os.path.join(DATASET_DIR, idx, f'image{idx}.objs')
            parameters.append([task_file, data_file, task, args.topdown, args.difference, args.abstraction,
                               args.timeout])
    # args.num_cores = 1
    # parameters = parameters[:1]
    parallel(outfile, process, parameters, num_workers=args.num_cores)
