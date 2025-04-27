# -*- coding:utf-8 -*-

import os
import json
from benchmarks import DIR
import time


def load_data():
    objs = {}
    obj_file = os.path.join(DIR, "8/image8.objs")
    with open(obj_file, 'r') as reader:
        for line in map(json.loads, reader):
            objs[line["id"]] = [line["Color"], line["Type"]]

    positives = [1, 7, 9, 23]
    negatives = [2, 4, 6, 10, 15, 22]
    action = ["recolor", "white"]
    return objs, positives, negatives, action


def construct_lattices():
    from order_theory import SetLattice, LazyProductLattice

    start = time.time()
    LATTICE_DIR = os.path.join(DIR, ".lattices", "Vehicle")
    # (1) load from pre-built files, fast
    color_lattice = SetLattice.load("Color", LATTICE_DIR)
    type_lattice = SetLattice.load("Type", LATTICE_DIR)
    # # (2) build from scratch, slow
    # color_lattice = SetLattice.build(
    #     "Color",
    #     ['Green', 'White', 'Red', 'Brown', 'Yellow', 'Blue', 'Orange', 'Black', 'Golden', 'Gray'])
    # type_lattice = SetLattice.build(
    #     "Type",
    #     ['Suv', 'Bus', 'MPV', 'Sedan', 'Pickup', 'Van', 'Motor', 'Hatchback', 'Truck', 'Estate'])
    vehicle_lattice = LazyProductLattice.build("Vehicle", [color_lattice, type_lattice])
    timecost = round(time.time() - start, 2)
    return vehicle_lattice, timecost


def encode_objs(objs, plattice):
    nodes = {}
    for idx, obj in objs.items():
        nodes[idx] = plattice.encode(obj)
    return nodes


def search(nodes, positives, negatives, plattice):
    # 3 efficient search algorithms for lattice search.
    # also, DFS and BFS were implememted in `search/`
    from search import (
        find_maximals_by_bottomup,
        find_maximal_by_topdown,
        find_maximal_by_abstraction,
    )

    pos_samples = [nodes[idx] for idx in positives]
    neg_samples = [nodes[idx] for idx in negatives]

    start = time.time()
    opt_maximals, opt_predicate = find_maximal_by_abstraction(pos_samples, neg_samples, plattice, difference=True)
    timecost = round(time.time() - start, 2)
    return opt_predicate, timecost


if __name__ == '__main__':
    objs, positives, negatives, action = load_data()
    print(f"#objs: {len(objs)}, #+: {len(positives)}, #-: {len(negatives)}, action: {action}")
    # #objs: 23, #+: 4, #-: 6, action: ['recolor', 'white']
    print(f"+: {set(tuple(objs[pos]) for pos in positives)}")
    print(f"-: {set(tuple(objs[neg]) for neg in negatives)}")

    # Step 1. construct base lattices and their production
    vehicle_lattice, const_time = construct_lattices()
    print(f"{vehicle_lattice.name} lattice = {' X '.join(subl.name for subl in vehicle_lattice.sublattices)}")
    # Vehicle lattice = Color X Type
    print(f"|{vehicle_lattice.name}| = {vehicle_lattice.num_nodes}")
    # |Vehicle| = 1046530
    print(f"Construction time: {const_time}")
    # Construction time: 0.47

    # Step 2. encode objects
    nodes = encode_objs(objs, vehicle_lattice)
    print(f"Car: {objs[1]} -> {nodes[1]}")
    # Car: ['Red', 'Hatchback'] -> (5, 4)

    # Step 3. search on the product lattice
    opt_predicate, search_time = search(nodes, positives, negatives, vehicle_lattice)
    print(f"Optimal predicate: {opt_predicate}")
    # Optimal predicate: OR(AND(Color ∉ {'Gray', 'Blue', 'White'}, Type ∉ {'MPV', 'Hatchback'}), AND(Color ∉ {'Gray', 'Black'}, Type ∉ {'Sedan'}))
    print(f"Search time: {search_time}")
    # Search time: 0.03
