# -*- coding: utf-8 -*-

from pulp import *


class PulpILPSolver:
    __slots__ = ['optimizer', 'vars']

    def __init__(self):
        # Integer Programming Problem solver
        self.reset()

    def reset(self):
        self.optimizer = LpProblem("Find_a_minimized_set_of_maximals", LpMinimize)
        self.vars = []

    def declare_vars(self, num: int):
        self.vars = [pulp.LpVariable(f'm{i:03d}', lowBound=0, upBound=1, cat=LpInteger) for i in range(num)]
        self.optimizer.addVariables(self.vars)
        return self.vars

    def minimize(self, obj, constraints, multi_solution: bool = True):
        # object function
        self.optimizer += obj
        # constraints
        for constraint in constraints:
            self.optimizer += constraint
        # solving
        # self.optimizer.solve()
        self.optimizer.solve(PULP_CBC_CMD(msg=0))
        if LpStatus[self.optimizer.status] == "Optimal":
            solution = [var.varValue for var in self.optimizer.variables()]
            obj_value = value(self.optimizer.objective)
            # print(f"Solution: {solution}")
            # print(f"Object value: {obj_value}")
            return obj_value, solution
        else:
            raise ValueError("Not an optimal solution")


if __name__ == '__main__':
    """
    This is an integer programming problem.

    P = {p1, p2}
    M = {p1 ↦ {m1, m2, m3}, p2 ↦ {m2, m3, m4}}

    min m1 + m2 + m3 + m4
    subject to
        (1) forall m_i. m_i \in {0, 1}
        (2) m1 + m2 + m3 = 1
        (3) m2 + m3 + m4 = 1
    """

    solver = PulpILPSolver()
    vars = solver.declare_vars(4)
    obj = sum(vars)
    constraints = [
        vars[0] + vars[1] + vars[2] == 1,
        vars[1] + vars[2] + vars[3] == 1,
    ]
    obj_value, solutions = solver.minimize(obj, constraints, multi_solution=True)
    print(obj_value)
    print(solutions)
