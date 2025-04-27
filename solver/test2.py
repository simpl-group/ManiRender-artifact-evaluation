# -*- coding: utf-8 -*-

from z3 import *

# Create Z3 integer variables
x = Int('x')
y = Int('y')

# Create a Z3 solver instance
s = Optimize()

# Add objective function to maximize profit
profit = 5 * x + 10 * y
s.minimize(profit)

# Add constraints
s.add(x >= 0)
s.add(y >= 0)
s.add(x + y <= 50)

# Check if the solver is satisfiable
if s.check() == sat:
    # Get the optimal values
    model = s.model()
    optimal_x = model[x].as_long()
    optimal_y = model[y].as_long()

    print(f"Optimal number of units of product A: {optimal_x}")
    print(f"Optimal number of units of product B: {optimal_y}")
    print(f"Maximum profit: ${5 * optimal_x + 10 * optimal_y}")
else:
    print("No feasible solution found.")
