# -*- coding: utf-8 -*-

import os
from collections import defaultdict
from typing import *

from constants import LATTICE_FILE_DIR
from order_theory.lattice import Lattice
from order_theory.lazy_product_lattice import LazyProductLattice


def find_maximal_by_DFS(pos_samples: List, neg_samples: List, lattice: LazyProductLattice) -> Dict:
    if len(neg_samples) == 0:
        return {1: [pos_samples]}
    predicates = defaultdict(set)
    while len(pos_samples) > 0:
        p_sample = pos_samples[0]
        coverset = [p_sample]  # stack
        visited = set()  # cache
        visited.add(p_sample)
        while len(coverset) > 0:
            e = coverset.pop()
            irreducible = True

            for a in lattice.successors(e):
                if a in visited:
                    continue
                uncovered_by_neg = not any(lattice.coveredby(n_sample, a) for n_sample in neg_samples)
                if uncovered_by_neg:
                    coverset.append(a)
                    visited.add(a)
                    irreducible = False

            if irreducible:  # e is maximal
                S = {p for p in pos_samples if lattice.coveredby(p, e)}
                predicates[e] = S
                pos_samples = list(set(pos_samples) - S)
                break

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

    predicates = find_maximal_by_DFS(POS_INDICES, NEG_INDICES, lattice)
    for maximal, p_samples in predicates.items():
        print(f"{[lattice.show(s) for s in p_samples]} is (are) covered by {lattice.show(maximal)}")
    """
    [('{R}', '[0, 20)')] is (are) covered by ('{R}', '[0, 100]')
    [('{B}', '(20, 100]')] is (are) covered by ('{R,B}', '[20, 100]')
    """
