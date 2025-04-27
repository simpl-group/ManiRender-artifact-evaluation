# -*- coding:utf-8 -*-

"""
A simple experiment about scalability
"""

import os
import json
import time
import random
from prettytable import PrettyTable

random.seed(0)

from order_theory.lazy_product_lattice import LazyProductLattice
from order_theory.set_lattice import SetLattice
from search import find_maximal_by_abstraction
from multiprocessing import (
    Process,
    Queue,
    Manager,
)

NUM_LABELS = 10  # 5 pos, 5 neg
TIMEOUT = 600  # a 10 min limit as we are exploring scalability
DIR = os.path.dirname(__file__)


def execute(func, args, timeout=TIMEOUT):
    manager = Manager()
    queue = manager.Queue()
    queue.empty()

    proc = Process(target=func, args=(*args, queue))
    proc.start()

    start = time.time()
    load_time, search_time = -1, -1
    while time.time() - start <= timeout:
        if not proc.is_alive():
            break
        time.sleep(0.1)
    else:
        proc.terminate()
        proc.join()

        try:
            load_time, search_time = [queue.get() for _ in range(queue.qsize())]
        except:
            return -1, -1
    return load_time, search_time


def process(lattice_name, POS, NEG, num_lattice, queue: Queue = None):
    start = time.time()
    # a lazy way to simulate loading sub lattices
    plattice = LazyProductLattice.build("pL", [SetLattice.load(lattice_name, DIR) for _ in range(num_lattice)])
    load_time = round(time.time() - start, 4)
    start = time.time()
    _, _ = find_maximal_by_abstraction(POS, NEG, plattice, difference=True)
    search_time = round(time.time() - start, 4)
    if queue is None:
        return load_time, search_time
    else:
        queue.empty()
        queue.put(load_time)
        queue.put(search_time)
        return queue


def random_gen_labels(num_attrs, range_size, num=NUM_LABELS):
    labels = set()
    while len(labels) < num:
        label = tuple(random.choices(list(range(1, 1 + range_size)), k=num_attrs))
        labels.add(label)
    labels = list(labels)
    POS = labels[:len(labels) // 2]
    NEG = labels[len(labels) // 2:]
    return POS, NEG


def vary_attrs(NUMS):
    RANGE = 10
    lattice_name = f"scalability-range{RANGE}"
    # pre-build lattice files
    if not os.path.exists(os.path.join(DIR, f"{lattice_name}.lattice")):
        base_lattice = SetLattice.build(lattice_name, list(map(str, range(RANGE))))
        base_lattice.dump(DIR)

    FILE = os.path.join(DIR, "scalability.attr")
    nums, loads, searches = [], [], []
    with open(FILE, 'w') as writer:
        for num in NUMS:
            POS, NEG = random_gen_labels(num, RANGE)
            # each attribute corresponds to a lattice
            load_time, search_time = execute(process, args=(lattice_name, POS, NEG, num), )
            nums.append(num)
            if load_time == -1:
                loads.append("N/A")
                searches.append("N/A")
                break  # OOM errors
            else:
                loads.append(round(load_time, 2))
                searches.append(round(search_time, 2))
                print(
                    json.dumps({"#attr": num, "|range|": RANGE, "time": [load_time, search_time]}, ensure_ascii=False),
                    file=writer)


def vary_ranges(RANGES):
    NUM_ATTRS = 10
    FILE = os.path.join(DIR, "scalability.range")
    ranges, loads, searches = [], [], []
    with open(FILE, 'w') as writer:
        for size in RANGES:
            # pre-build lattice files
            lattice_name = f"scalability-range{size}"
            if not os.path.exists(os.path.join(DIR, f"{lattice_name}.lattice")):
                base_lattice = SetLattice.build(lattice_name, list(map(str, range(size))))
                base_lattice.dump(DIR)

            POS, NEG = random_gen_labels(NUM_ATTRS, size)
            # each attribute corresponds to a lattice
            load_time, search_time = execute(process, args=(lattice_name, POS, NEG, NUM_ATTRS), )
            ranges.append(size)
            if load_time == -1:
                loads.append("N/A")
                searches.append("N/A")
                break  # OOM errors
            else:
                loads.append(round(load_time, 2))
                searches.append(round(search_time, 2))
            print(
                json.dumps({"#attr": NUM_ATTRS, "|range|": size, "time": [load_time, search_time]}, ensure_ascii=False),
                file=writer)


if __name__ == '__main__':
    vary_attrs(NUMS=[1, 10, 50, 100, 120, 140, 150])  # increase the max number of attributes
    vary_ranges(RANGES=[5, 6, 7, 8, 9, 10, 11, 12])  # increase the max range
