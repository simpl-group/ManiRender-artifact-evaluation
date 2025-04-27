# -*- coding: utf-8 -*-

import heapq
from typing import Set, List, Tuple
from collections import defaultdict
from ordered_set import OrderedSet
from order_theory import LazyProductLattice, SetLattice
import itertools


def is_valid(sample: Tuple, neg_samples: List[Tuple], product_lattice) -> bool:
    return all(not product_lattice.coveredby(neg, sample) for neg in neg_samples)


def cover_any(sample: Tuple, pos_samples: List[Tuple], product_lattice) -> bool:
    return any(product_lattice.coveredby(pos, sample) for pos in pos_samples)


def cover_all(sample: Tuple, pos_samples: List[Tuple], product_lattice) -> bool:
    return all(product_lattice.coveredby(pos, sample) for pos in pos_samples)


def cover_no(sample: Tuple, neg_samples: List[Tuple], product_lattice) -> bool:
    return all(not product_lattice.coveredby(neg, sample) for neg in neg_samples)


def find_submaximals_by_bfs(maximal: Tuple, pos_samples: List, neg_samples: List, lattice: LazyProductLattice,
                            return_mapping=True):
    if cover_no(maximal, neg_samples, lattice):
        maximals = [maximal]
    else:
        maximals = set()
        candidates = {maximal}
        while len(candidates) != 0:
            new_candidates = set()
            # (1) find out all predecessors covering any positive samples
            predecessors = set()
            for cand in candidates:
                predecessors |= set(lattice.predecessors(cand))
            # (2) split predecessors into two parts: 1. maximals candidates if covering no negative samples
            #                                        2. predecessors covering both positive and negative samples.
            for pre_cand in predecessors:
                if cover_no(pre_cand, pos_samples, lattice):
                    continue
                if cover_no(pre_cand, neg_samples, lattice):
                    # check it's indeed a valid maximal
                    if all(not lattice.coveredby(pre_cand, maximal) for maximal in maximals):
                        maximals.add(pre_cand)
                else:
                    new_candidates.add(pre_cand)
            candidates = new_candidates
        maximals = list(maximals)
    if return_mapping:
        maximal_mapping = defaultdict(OrderedSet)
        for pos_idx, pos in enumerate(pos_samples):
            maximal_mapping[pos_idx] |= \
                [max_idx for max_idx, maximal in enumerate(maximals) if lattice.coveredby(pos, maximal)]
        return maximals, maximal_mapping
    else:
        return maximals, None


def find_one_sub_maximal_by_dfs(maximal: Tuple, pos: Tuple, neg_samples: List, lattice: LazyProductLattice):
    if cover_no(maximal, neg_samples, lattice):
        return maximal
    else:
        candidates = {maximal}
        while len(candidates) != 0:
            new_candidates = set()
            # (1) find out all predecessors covering any positive samples
            predecessors = set()
            for cand in candidates:
                predecessors |= set(lattice.predecessors(cand))
            # (2) split predecessors into two parts: 1. maximals candidates if covering no negative samples
            #                                        2. predecessors covering both positive and negative samples.
            for pre_cand in predecessors:
                if not lattice.coveredby(pos, pre_cand):
                    continue
                if cover_no(pre_cand, neg_samples, lattice):
                    return pre_cand
                else:
                    new_candidates.add(pre_cand)
            candidates = new_candidates
    raise ValueError


def remove_nonmaximals(candidates, lattice, maximals: Set = None):
    full_maximals = []
    for i, cand_i in enumerate(candidates):
        if maximals is None:
            if all(not lattice.coveredby(cand_i, cand_j) for j, cand_j in enumerate(candidates) if i != j):
                full_maximals.append(cand_i)
        else:
            if all(not lattice.coveredby(cand_i, maximal) for maximal in maximals) and \
                    all(not lattice.coveredby(cand_i, cand_j) for j, cand_j in enumerate(candidates) if i != j):
                full_maximals.append(cand_i)
    if maximals is None:
        return full_maximals
    else:
        return list(maximals) + full_maximals


def find_submaximals_by_difference(maximal: Tuple, pos_samples: List, neg_samples: List, lattice: LazyProductLattice,
                                   return_mapping=True):
    if cover_no(maximal, neg_samples, lattice):
        maximals = [maximal]
    else:
        maximals = [maximal]
        for idx, neg in enumerate(neg_samples):
            new_maximals = []
            for maximal in maximals:
                if lattice.coveredby(neg, maximal):
                    new_maxs = lattice.difference(maximal, neg)
                    new_maximals += [new_max for new_max in new_maxs if cover_any(new_max, pos_samples, lattice)]
                else:
                    new_maximals += [maximal]
            maximals = new_maximals
        maximals = list(set(maximals))
        maximals = remove_nonmaximals(maximals, lattice)
    if return_mapping:
        maximal_mapping = defaultdict(OrderedSet)
        for pos_idx, pos in enumerate(pos_samples):
            maximal_mapping[pos_idx] |= \
                [max_idx for max_idx, maximal in enumerate(maximals) if lattice.coveredby(pos, maximal)]
        return maximals, maximal_mapping
    else:
        return maximals, None


def search_maximals(pos, neg_samples, lattice):
    # print("========= MAXIMAL =========")
    # print(tuple(sub_l.decode(id) for id, sub_l in zip(pos, lattice.sublattices)))
    # print([tuple(sub_l.decode(id) for id, sub_l in zip(ids, lattice.sublattices)) for ids in neg_samples])
    # only find one maximal
    maximal = pos
    for e in lattice.base_elements:
        # the 2 following code lines make it slower
        # if any(e == neg for neg in neg_samples):
        #     continue
        new_maximal = lattice.join(maximal, e)
        if is_valid(new_maximal, neg_samples, lattice):
            maximal = new_maximal
    # print(lattice.decode(maximal))
    # assert is_valid(maximal, neg_samples, lattice)
    return maximal


def beautify_program(sublattices: List, maximals: List):
    program = []
    for opt_max in maximals:
        sub_program = []
        for sub_l, sub_m in zip(sublattices, opt_max):
            if len(sub_l.nodes) - 1 == sub_m:
                continue
            # if the maximal is {1, 2, 3} and the full set is {1, 2, 3, 4}, then rewrite it as ∉ {4}
            sub_m = sub_l.decode(sub_m)
            if isinstance(sub_l, SetLattice) and len(sub_m) > len(sub_l.nodes[-1]) / 2:
                sub_program.append(f"{sub_l.name} ∉ {sub_l.nodes[-1] - sub_m}")
            else:
                sub_program.append(f"{sub_l.name} ∈ {sub_m}")
        if len(sub_program) > 1:
            sub_program = ", ".join(sub_program)
            program.append(f"AND({sub_program})")
        else:
            program.append(sub_program[0])
    if len(program) > 1:
        program = ", ".join(program)
        program = f"OR({program})"
    else:
        program = program[0]
    return program
