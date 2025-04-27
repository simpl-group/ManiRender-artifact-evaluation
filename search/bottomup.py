# -*- coding: utf-8 -*-

from typing import *
from order_theory import *
from ordered_set import OrderedSet
from search.util import cover_any, beautify_program
from solver.pulp_ipp_solver import PulpILPSolver
from itertools import chain, combinations
from collections import defaultdict


def powerset(fullset):
    return map(set, chain.from_iterable(combinations(fullset, length) for length in range(2, len(fullset))))


def find_maximals(minimal: Tuple, pos_samples: List, neg_samples: List, lattice: LazyProductLattice):
    maximals = set()
    candidates = {minimal}
    while len(candidates) != 0:
        new_candidates = set()
        # find new maximals that covers any positive and no negative samples
        for cand in candidates:
            succ_cands = lattice.successors(cand)
            cover_neg_flags = [cover_any(succ_cand, neg_samples, lattice) for succ_cand in succ_cands]
            if all(cover_neg_flags):
                # (1) cand's all successors cover negative samples and cand covers any positive sample
                if cover_any(cand, pos_samples, lattice):
                    maximals.add(cand)
            else:
                # (2) some cand's successors cover no negative samples
                for succ_cand, cover_neg_flag in zip(succ_cands, cover_neg_flags):
                    if not cover_neg_flag:
                        new_candidates.add(succ_cand)
        candidates = new_candidates
    maximals = list(set(maximals))
    maximal_mapping = defaultdict(OrderedSet)
    for pos_idx, pos in enumerate(pos_samples):
        maximal_mapping[pos_idx] |= \
            [max_idx for max_idx, maximal in enumerate(maximals) if lattice.coveredby(pos, maximal)]
    return maximals, maximal_mapping


def find_maximals_by_bottomup(pos_samples: List, neg_samples: List, lattice: LazyProductLattice, **kwargs):
    maximals, maximal_mapping = find_maximals(lattice.bot, pos_samples, neg_samples, lattice)

    solver = PulpILPSolver()
    vars = solver.declare_vars(len(maximals))
    obj = sum(vars)
    constraints = []
    for pos, max_ids in maximal_mapping.items():
        if len(max_ids) == 1:
            const = vars[max_ids[0]] == 1
        else:
            const = sum([vars[idx] for idx in max_ids]) >= 1
        constraints.append(const)
    _, opt_solution = solver.minimize(obj, constraints)

    opt_maximals = [maximals[idx] for idx, value in enumerate(opt_solution) if value == 1.]
    opt_program = beautify_program(lattice.sublattices, opt_maximals)
    return opt_maximals, opt_program


if __name__ == '__main__':
    num_lattice = SetLattice.build('fruit', baseset=['1', '2', '3', '4'])
    color_lattice = SetLattice.build('color', baseset=['R', 'G', 'B'])
    base_lattices = [num_lattice, color_lattice]
    lattice_product = LazyProductLattice.build(name="product", lattices=base_lattices)
    POS = [
        ['1', 'R'],
        ['4', 'G'],
    ]
    NEG = [
        ['4', 'R'],
        ['3', 'B'],
    ]
    POS_INDICES = [lattice_product.encode(pos) for pos in POS]
    NEG_INDICES = [lattice_product.encode(neg) for neg in NEG]
    opt_maximals, opt_program = find_maximals_by_bottomup(POS_INDICES, NEG_INDICES, base_lattices, lattice_product)
    # OR(AND(fruit ∈ {'4', '1', '2'}, color ∈ {'G', 'B'}), AND(fruit ∈ {'1', '3', '2'}, color ∈ {'G', 'R'}))
    print(opt_program)
