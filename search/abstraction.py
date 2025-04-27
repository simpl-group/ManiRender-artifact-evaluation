# -*- coding: utf-8 -*-

import itertools
from collections import defaultdict
from typing import *
from ordered_set import OrderedSet
from search.util import (
    search_maximals, beautify_program, cover_any, cover_no,
    find_submaximals_by_bfs,
    find_submaximals_by_difference,
    find_one_sub_maximal_by_dfs,
)
from order_theory import *
from solver.pulp_ipp_solver import PulpILPSolver


def find_joinable_mapping(pos_samples: List[Tuple], neg_samples: List[Tuple], lattice: LazyProductLattice,
                          difference=False):
    joinable_maximal = lattice.joins(pos_samples)
    if difference:
        maximals, _ = find_submaximals_by_difference(joinable_maximal, pos_samples, neg_samples, lattice,
                                                     return_mapping=False)
    else:
        maximals, _ = find_submaximals_by_bfs(joinable_maximal, pos_samples, neg_samples, lattice,
                                              return_mapping=False)

    # print('Positives:')
    # for pos in pos_samples:
    #     print(lattice.decode(pos))
    # print('Negatives:')
    # for neg in neg_samples:
    #     print(lattice.decode(neg))
    # print('Difference:')
    # maximals1, _ = find_submaximals_by_difference(joinable_maximal, pos_samples, neg_samples, lattice,
    #                                               return_mapping=False)
    # for maximal in maximals1:
    #     print(lattice.decode(maximal))
    # print('TopDown:')
    # maximals2, _ = find_submaximals_by_bfs(joinable_maximal, pos_samples, neg_samples, lattice, return_mapping=False)
    # # assert set(maximals1).issubset(set(maximals2)), set(maximals1) - set(maximals2)
    # # assert set(maximals2).issubset(set(maximals1))
    # for maximal in set(maximals2) - set(maximals1):
    #     print(lattice.decode(maximal))
    #     assert any(lattice.coveredby(pos, maximal) for pos in pos_samples)
    #     assert all(not lattice.coveredby(neg, maximal) for neg in neg_samples)
    # exit()

    reps = []
    del_flags = []
    for maximal in maximals:
        covered_ids = set(idx for idx, pos in enumerate(pos_samples) if lattice.coveredby(pos, maximal))
        # if we find any set that is smaller than the current one, discard the smaller one
        exist_flag = False
        for idx, (rep, flag) in enumerate(zip(reps, del_flags)):
            if flag:
                continue
            if covered_ids == rep:
                exist_flag = True
                break
            if covered_ids.issuperset(rep):
                del_flags[idx] = True
        if not exist_flag:
            reps.append(covered_ids)
            del_flags.append(False)
    reps = [rep for rep, flag in zip(reps, del_flags) if not flag]

    pos2reps = defaultdict(set)
    for idx, rep in enumerate(reps):
        for i in rep:
            pos2reps[i].add(idx)

    return reps, pos2reps


def find_representative_maximals_by_dfs(reps, opt_solution, pos_samples, neg_samples, lattice):
    rep2max = {}  # rep -> maximals
    for idx, (rep_ids, value) in enumerate(zip(reps, opt_solution)):
        if value == 1.:
            if isinstance(rep_ids, Tuple):
                rep2max[idx] = rep_ids  # isolated maximal
            else:
                positives = [pos_samples[i] for i in rep_ids]
                positive_join = lattice.joins(positives)
                exclusive_pos_samples = [pos for i, pos in enumerate(pos_samples) if i not in rep_ids]
                rep2max[idx] = find_one_sub_maximal_by_dfs(
                    lattice.top, positive_join, neg_samples + exclusive_pos_samples, lattice)
    return rep2max


def find_representative_maximals_by_difference(reps, opt_solution, pos_samples, neg_samples, lattice):
    def _find_one_maximal_by_successors(maximal, neg_samples: List, lattice: LazyProductLattice):
        for succ in lattice.successors(maximal):
            # if one successor cover no negative sample,
            #   then `maximal` is not a maximal but the successor is more likely to be.
            if cover_no(succ, neg_samples, lattice):
                return _find_one_maximal_by_successors(succ, neg_samples, lattice)
        return maximal

    # DFS
    def _f(maximal, pos: Tuple, ex_pos_samples: List, neg_samples: List, lattice: LazyProductLattice,
           init_neg_samples: List):
        if len(neg_samples) == 0:
            if cover_any(maximal, ex_pos_samples, lattice):
                # cover any exclusive positive sample
                return None
            else:
                # check it's indeed maximal using successors and DFS
                return _find_one_maximal_by_successors(maximal, init_neg_samples + ex_pos_samples, lattice)

        neg = neg_samples[0]
        for new_max in lattice.difference(maximal, neg):
            if lattice.coveredby(pos, new_max):
                new_max = _f(new_max, pos, ex_pos_samples, neg_samples[1:], lattice, init_neg_samples)
                if new_max is not None:
                    return new_max

    rep2max = {}  # rep -> maximals
    for idx, (rep_ids, value) in enumerate(zip(reps, opt_solution)):
        if value == 1.:
            if isinstance(rep_ids, Tuple):
                rep2max[idx] = rep_ids  # isolated maximal
                raise ValueError
            else:
                positives = [pos_samples[i] for i in rep_ids]
                positive_join = lattice.joins(positives)
                exclusive_pos_samples = [pos for i, pos in enumerate(pos_samples) if i not in rep_ids]
                rep2max[idx] = _f(lattice.top, positive_join, exclusive_pos_samples, neg_samples, lattice,
                                  init_neg_samples=neg_samples)
    return rep2max


def find_maximal_by_abstraction(pos_samples: List, neg_samples: List, lattice: LazyProductLattice, difference=False,
                                **kwargs) -> Any:
    reps, pos2reps = find_joinable_mapping(pos_samples, neg_samples, lattice, difference=difference)

    # 2. find out maximals of isolated/joinable representatives
    solver = PulpILPSolver()
    vars = solver.declare_vars(len(reps))
    obj = sum(vars)
    constraints = []
    for _, rep in pos2reps.items():
        if len(rep) == 1:
            const = vars[list(rep)[0]] == 1
        else:
            const = sum([vars[idx] for idx in rep]) >= 1
        constraints.append(const)
    _, opt_solution = solver.minimize(obj, constraints)

    # 4. convert joinable representatives to maximals
    if difference:
        rep2max = find_representative_maximals_by_difference(reps, opt_solution, pos_samples, neg_samples, lattice)
    else:
        rep2max = find_representative_maximals_by_dfs(reps, opt_solution, pos_samples, neg_samples, lattice)

    opt_maximals = list(rep2max.values())
    # # check positives and negatives
    # for pos in pos_samples:
    #     assert any(lattice.coveredby(pos, opt_max) for opt_max in opt_maximals)
    # for neg in neg_samples:
    #     assert all(not lattice.coveredby(neg, opt_max) for opt_max in opt_maximals)
    opt_program = beautify_program(lattice.sublattices, opt_maximals)
    return opt_maximals, opt_program

# if __name__ == '__main__':
#     from test
