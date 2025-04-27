# -*- coding: utf-8 -*-

"""
This is an integer programming problem.

U = {p1, p2}
Mapping = {p1 ↦ {m1, m2 ... m1000}, p2 ↦ {m2 ... m1000, m1001}

min \sum m_i
subject to
    (1) \forall m_i. m_i \in {0, 1}
    (2) m1 + ... + m1000 >= 1
    (3) m2 + ... + m1001 >= 1

+ Refinement

U = {p1, p2}
Mapping = {p1 ↦ {m1, [m2 ... m_k]}, p2 ↦ {[m2 ... m_k], m_{k+1}}
Mapping' = {p1 ↦ {m1, r}, p2 ↦ {r, m_{k+1}}

p1 \/ p2, r1
p1 \/ p2 \/ p3, r2
Mapping' = {p1 ↦ {m1, r2}, p2 ↦ {r2, m_{k+1}}, p3 ↦ {r2}}

(1)
[p1, ..., p_10]
=> isolated [p1, p2, p3, p4]
=> joinable [(p5, p6, p10), (p7, p8, p9) (p5, p8)]

# (2) isolated refinement
negative <= p1 \/ p_i,  for i > 1
e.g.,
Mapping = {p1 ↦ {im_1}, p2 ↦ {im_2, jm_2}, p3 ↦ {jm_2}}
S: im_1, jm_2

# (2) joinable refinement
negative </= p2 \/ p_i,  exists i != 2
e.g.,
Mapping = {p1 ↦ {im_1}, p2 ↦ {im_2, jm_2}, p3 ↦ {jm_2}}
S: im_1, jm_2

refinement => maximal
"""

from pulp import *

problem = LpProblem("Find a minimized set of maximals", LpMinimize)

m1 = pulp.LpVariable('m1', lowBound=0, upBound=1, cat=LpInteger)
m2 = pulp.LpVariable('m2', lowBound=0, upBound=1, cat=LpInteger)
m3 = pulp.LpVariable('m3', lowBound=0, upBound=1, cat=LpInteger)
m4 = pulp.LpVariable('m4', lowBound=0, upBound=1, cat=LpInteger)
problem.addVariables([m1, m2, m3, m4])

# object function
problem += m1 + m2 + m3 + m4

# constraints
problem += m1 + m2 + m3 >= 1
problem += m2 + m3 + m4 >= 1

# solving
problem.solve()

if LpStatus[problem.status] == "Optimal":
    solution = [var.varValue for var in problem.variables()]
    obj_value = value(problem.objective)
    print(f"Solution: {solution}")
    print(f"Object value: {obj_value}")
else:
    raise ValueError("Not an optimal solution")
