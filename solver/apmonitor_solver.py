# -*- coding:utf-8 -*-

from gekko import GEKKO


class APmonitorSolver:
    __slots__ = ['solver', 'vars']

    def __init__(self):
        # Integer Programming Problem solver
        self.reset()

    def reset(self):
        self.solver = GEKKO(remote=False)
        self.vars = []

    def declare_vars(self, num: int):
        self.vars = [self.solver.Var(lb=0, ub=1, integer=True) for i in range(num)]
        return self.vars

    def minimize(self, obj, constraints):
        # object function
        self.solver.Minimize(obj)
        # constraints
        self.solver.Equations(constraints)
        # solving
        self.solver.solve(disp=False)
        obj_value = self.solver.options.OBJFCNVAL
        solutions = [var.value[0] for var in self.vars]
        return obj_value, solutions


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

    solver = APmonitorSolver()
    vars = solver.declare_vars(4)
    obj = sum(vars)
    constraints = [
        vars[0] + vars[1] + vars[2] >= 1,
        vars[1] + vars[2] + vars[3] >= 1,
    ]
    obj_value, solutions = solver.minimize(obj, constraints)
    print(obj_value)
    print(solutions)
