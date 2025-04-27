# -*- coding: utf-8 -*-

from typing import *
from order_theory import *
from search.util import (
    find_submaximals_by_bfs, find_submaximals_by_difference, beautify_program,
)
from solver.pulp_ipp_solver import PulpILPSolver


def find_maximal_by_topdown(pos_samples: List, neg_samples: List, lattice: LazyProductLattice, difference=False,
                            **kwargs) -> Any:
    if difference:
        maximals, maximal_mapping = find_submaximals_by_difference(lattice.top, pos_samples, neg_samples, lattice)
    else:
        maximals, maximal_mapping = find_submaximals_by_bfs(lattice.top, pos_samples, neg_samples, lattice)

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
    opt_maximals, opt_program = find_maximal_by_topdown(POS_INDICES, NEG_INDICES, base_lattices, lattice_product)
    print(opt_program)
