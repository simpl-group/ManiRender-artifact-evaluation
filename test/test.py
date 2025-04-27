# -*- coding: utf-8 -*-

import time
import unittest
from functools import wraps

from order_theory.interval_lattice import IntervalLattice
from order_theory.lazy_product_lattice import LazyProductLattice
from order_theory.set_lattice import SetLattice
from search.bfs import find_maximal_by_BFS
from search.dfs import find_maximal_by_DFS


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


class TestLattice(unittest.TestCase):

    @timeit
    def test_create_set_lattice(self):
        # 21.8201
        baseset = [f"s{idx}" for idx in range(1, 21)]
        lattice = SetLattice.build("color", baseset=baseset)
        self.assertEqual(len(lattice.nodes), 1048576)

    @timeit
    def test_create_interval_lattice(self):
        # 23.7384
        points = list(range(1500))
        lattice = IntervalLattice.build("age", points=points)
        self.assertEqual(len(lattice.nodes), 4492504)

    @timeit
    def test_bfs(self):
        # num_color, num_interval = 5, 10 # 2.22s
        num_color, num_interval = 5, 20  # 10.85s
        mid_color = f"s{num_color // 2}"
        max_color = f"s{num_color}"
        max_point = num_interval * 10

        baseset = [f"s{idx}" for idx in range(1, num_color + 1)]
        slattice = SetLattice.build("color", baseset=baseset)

        points = [i * 10 for i in range(num_interval + 1)]
        ilattice = IntervalLattice.build("age", points=points)

        lattice = LazyProductLattice.build("product_of_color_age", [slattice, ilattice])
        POS = [
            [['s1'], [0, True, False, 10]],
            [[mid_color], [max_point - 10, False, True, max_point]],
        ]
        NEG = [
            [[mid_color], [0, True, False, 10]],
            [[max_color], [max_point - 10, False, True, max_point]],
        ]
        POS_INDICES = [lattice.__index__(pos) for pos in POS]
        NEG_INDICES = [lattice.__index__(neg) for neg in NEG]
        predicates = find_maximal_by_BFS(POS_INDICES, NEG_INDICES, lattice)
        for p_sample, maximals in predicates.items():
            print(f"{lattice.show(p_sample)} is covered by {[lattice.show(maximal) for maximal in maximals]}")

    @timeit
    def test_abstraction_case1(self):
        # free lunch
        from search import find_maximal_by_abstraction

        color_lattice = SetLattice.build('color', baseset=['R', 'G', 'B', 'Y'])
        genre_lattice = SetLattice.build('vehicle', baseset=['Sedan', 'MPV', 'SUV'])
        age_lattice = IntervalLattice.build('age', points=[0, 20, 40, 60, 80, 100])
        base_lattices = [color_lattice, genre_lattice, age_lattice]
        product_lattice = LazyProductLattice.build(name="product", lattices=base_lattices)
        POS = [
            ['R', 'Sedan', [0, True, True, 0]],
            ['B', 'MPV', [60, True, True, 60]],
        ]
        NEG = [
            ['G', 'MPV', [20, True, True, 20]],
            ['G', 'SUV', [80, True, True, 80]],
        ]
        POS_INDICES = [product_lattice.encode(pos) for pos in POS]
        NEG_INDICES = [product_lattice.encode(neg) for neg in NEG]
        predicates = find_maximal_by_abstraction(POS_INDICES, NEG_INDICES, base_lattices, product_lattice,
                                                 optimal=True, acceleration=True)
        for pred in predicates:
            print([product_lattice.decode(node) for node in pred])

    @timeit
    def test_abstraction_case1_variant(self):
        # free lunch variant
        # ({'R', 'B', 'Y'}, {'Sedan', 'SUV', 'MPV'})
        # -: ['G', 'MPV'], ['G', 'SUV']
        from search import find_maximal_by_abstraction

        color_lattice = SetLattice.build('color', baseset=['R', 'G', 'B', 'Y'])
        genre_lattice = SetLattice.build('vehicle', baseset=['Sedan', 'MPV', 'SUV'])
        age_lattice = IntervalLattice.build('age', points=[0, 20, 40, 60, 80, 100])
        base_lattices = [color_lattice, genre_lattice, age_lattice]
        product_lattice = LazyProductLattice.build(name="product", lattices=base_lattices)
        POS = [
            ['R', 'Sedan', [0, True, True, 0]],
            ['B', 'Sedan', [60, True, True, 60]],
        ]
        NEG = [
            ['G', 'MPV', [20, True, True, 20]],
            ['G', 'SUV', [80, True, True, 80]],
        ]
        POS_INDICES = [product_lattice.encode(pos) for pos in POS]
        NEG_INDICES = [product_lattice.encode(neg) for neg in NEG]
        predicates = find_maximal_by_abstraction(POS_INDICES, NEG_INDICES, base_lattices, product_lattice,
                                                 optimal=True, acceleration=True)
        for pred in predicates:
            print([product_lattice.decode(node) for node in pred])

    @timeit
    def test_abstraction_case2(self):
        # free lunch
        from search import find_maximal_by_abstraction

        color_lattice = SetLattice.build('color', baseset=['R', 'G', 'B', 'Y'])
        genre_lattice = SetLattice.build('vehicle', baseset=['Sedan', 'MPV', 'SUV'])
        age_lattice = IntervalLattice.build('age', points=[0, 20, 40, 60, 80, 100])
        base_lattices = [color_lattice, genre_lattice, age_lattice]
        product_lattice = LazyProductLattice.build(name="product", lattices=base_lattices)
        POS = [
            ['R', 'MPV', [0, True, True, 0]],
            ['B', 'MPV', [60, True, True, 60]],
        ]
        NEG = [
            ['G', 'MPV', [20, True, True, 20]],
            ['G', 'SUV', [80, True, True, 80]],
        ]
        POS_INDICES = [product_lattice.encode(pos) for pos in POS]
        NEG_INDICES = [product_lattice.encode(neg) for neg in NEG]
        predicates = find_maximal_by_abstraction(POS_INDICES, NEG_INDICES, base_lattices, product_lattice,
                                                 optimal=True, acceleration=True)
        for pred in predicates:
            print([product_lattice.decode(node) for node in pred])

    @timeit
    def test_dfs(self):
        # num_color, num_interval = 10, 1500 # 21.61s
        # num_color, num_interval = 15, 1500  # 23.38s
        num_color, num_interval = 20, 1500  # 54.52s
        mid_color = f"s{num_color // 2}"
        max_color = f"s{num_color}"
        max_point = num_interval * 10

        baseset = [f"s{idx}" for idx in range(1, num_color + 1)]
        slattice = SetLattice.build("color", baseset=baseset)

        points = [i * 10 for i in range(num_interval + 1)]
        ilattice = IntervalLattice.build("age", points=points)

        lattice = LazyProductLattice.build("product_of_color_age", [slattice, ilattice])
        POS = [
            [['s1'], [0, True, False, 10]],
            [[mid_color], [max_point - 10, False, True, max_point]],
        ]
        NEG = [
            [[mid_color], [0, True, False, 10]],
            [[max_color], [max_point - 10, False, True, max_point]],
        ]
        POS_INDICES = [lattice.__index__(pos) for pos in POS]
        NEG_INDICES = [lattice.__index__(neg) for neg in NEG]
        predicates = find_maximal_by_DFS(POS_INDICES, NEG_INDICES, lattice)
        for maximal, p_samples in predicates.items():
            print(f"{[lattice.show(s) for s in p_samples]} is (are) covered by {lattice.show(maximal)}")


if __name__ == '__main__':
    unittest.main()
