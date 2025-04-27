# -*- coding: utf-8 -*-


from z3 import *


class Z3ILPSolver:
    __slots__ = ['optimizer', 'vars']
    __ctx = Context()

    def __init__(self):
        # Integer Programming Problem solver
        self.reset()

    def reset(self):
        self.optimizer = Optimize(ctx=self.__ctx)
        self.vars = []

    def declare_vars(self, num: int):
        self.vars = [Int(f'v{i}', ctx=self.__ctx) for i in range(num)]
        return self.vars

    def _execute(self, obj, constraints):
        self.optimizer.minimize(obj)
        for const in constraints:
            self.optimizer.add(const)
        if self.optimizer.check() == sat:
            model = self.optimizer.model()
            obj_value = model.eval(obj).as_long()
            solution = [model[var].as_long() for var in self.vars]
            return obj_value, solution
        else:
            return None, None

    def minimize(self, obj, constraints, multi_solution: bool = True):
        constraints = [Or(var == 0, var == 1) for var in self.vars] + constraints
        obj_value, solution = self._execute(obj, constraints)
        if obj_value is None:
            # raise ValueError("Cannot find any solution.")
            return obj_value, solution
        else:
            solutions = [solution]
            self.optimizer.add(obj == obj_value)
            while multi_solution:
                self.optimizer.add(Or(*[var != v for var, v in zip(self.vars, solution)]))
                if self.optimizer.check() == sat:
                    model = self.optimizer.model()
                    solution = [model[var].as_long() for var in self.vars]
                    solutions.append(solution)
                else:
                    break
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

    solver = Z3ILPSolver()
    vars = solver.declare_vars(4)
    obj = sum(vars)
    constraints = [
        vars[0] + vars[1] + vars[2] == 1,
        vars[1] + vars[2] + vars[3] == 1,
    ]
    obj_value, solutions = solver.minimize(obj, constraints, multi_solution=True)
    print(obj_value)
    print(solutions)
