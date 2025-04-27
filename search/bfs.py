# -*- coding: utf-8 -*-

import os
from collections import defaultdict
from queue import Queue
from typing import *

from constants import LATTICE_FILE_DIR
from order_theory.lattice import Lattice
from order_theory.lazy_product_lattice import LazyProductLattice


def find_maximal_by_BFS(pos_samples: List, neg_samples: List, lattice: LazyProductLattice) -> Dict:
    if len(neg_samples) == 0:
        return {1: [pos_samples]}
    predicates = defaultdict(set)
    for idx, p_sample in enumerate(pos_samples, start=1):
        coverset = Queue()
        coverset.put(p_sample)
        while not coverset.empty():
            e = coverset.get()
            irreducible = True

            for a in lattice.successors(e):
                uncovered_by_neg = not any(lattice.coveredby(n_sample, a) for n_sample in neg_samples)
                if uncovered_by_neg:
                    # print(lattice.show(a))
                    coverset.put(a)
                    irreducible = False

            if irreducible:
                for p in [p_sample] + [sample for sample in pos_samples[idx:] if lattice.coveredby(sample, e)]:
                    predicates[p].add(e)

    return predicates


if __name__ == '__main__':
    dump_dir = os.path.join(LATTICE_FILE_DIR, "example1")
    color_lattice = Lattice.load('color', dump_dir)
    age_lattice = Lattice.load('age', dump_dir)
    lattice = LazyProductLattice.build(name="product", lattices=[color_lattice, age_lattice])

    POS = [
        [['R'], [0, True, False, 20]],
        [['B'], [20, False, True, 100]],
    ]
    NEG = [
        [['B'], [0, True, False, 20]],
        [['G'], [20, False, True, 100]],
    ]
    POS_INDICES = [lattice.__index__(pos) for pos in POS]
    NEG_INDICES = [lattice.__index__(neg) for neg in NEG]

    predicates = find_maximal_by_BFS(POS_INDICES, NEG_INDICES, lattice)
    for p_sample, maximals in predicates.items():
        print(f"{lattice.show(p_sample)} is covered by {[lattice.show(maximal) for maximal in maximals]}")
    """
    ('{R}', '[0, 20)') is covered by [('{R,G}', '[0, 20]'), ('{R}', '[0, 100]')]
    ('{B}', '(20, 100]') is covered by [('{R,B}', '[20, 100]')]
    """
