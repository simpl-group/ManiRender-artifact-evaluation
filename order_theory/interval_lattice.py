# -*- coding: utf-8 -*-

import itertools
from collections import defaultdict
from typing import *

from constants import NODE_LABEL_FUNCS, BOTTOM
from order_theory.lattice import Lattice


class IntervalLattice(Lattice):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    @classmethod
    def build(cls, name: str, points: List, relation: str = "⊑") -> Lattice:
        nodes, edges, joins, cmps, coverages = cls.powerset(points)
        type = 'interval'
        node_label_func = NODE_LABEL_FUNCS[type]
        lattice = IntervalLattice(name, nodes=nodes, edges=edges, joins=joins, cmps=cmps, coverages=coverages,
                                  relation=relation, node_label_func=node_label_func, type=type)
        return lattice

    @staticmethod
    def powerset(points: List):
        assert len(points) > 2
        nodes = [BOTTOM, [points[0], True, True, points[0]], [points[0], False, False, points[1]]]
        depth = {}
        for idx in range(1, len(points) - 1):
            nodes.append([points[idx], True, True, points[idx]])
            nodes.append([points[idx], False, False, points[idx + 1]])
        nodes.append([points[-1], True, True, points[-1]])
        edges = defaultdict(set)
        for idx in range(1, len(nodes)):
            edges[0].add(idx)
            depth[idx] = 1
        start_idx = 1
        prev_layer = nodes[1:]
        curr_depth = 1
        while len(prev_layer) > 1:
            curr_layer = []
            for offset, idx in enumerate(range(len(prev_layer) - 1), start=start_idx):
                curr_layer.append(
                    [prev_layer[idx][0], prev_layer[idx][1], prev_layer[idx + 1][2], prev_layer[idx + 1][-1]])
                nodes.append(curr_layer[-1])
                # edges += [(offset, len(nodes) - 1), (offset + 1, len(nodes) - 1)]
                edges[offset].add(len(nodes) - 1)
                edges[offset + 1].add(len(nodes) - 1)
                depth[offset] = depth[offset + 1] = curr_depth
            prev_layer = curr_layer
            curr_depth += 1
            start_idx = len(nodes) - len(prev_layer)
        depth[len(edges)] = curr_depth

        # joins of two elements
        joins = {}  # e1 \/ e2
        for e1, e2 in itertools.product(range(1, len(nodes)), range(1, len(nodes))):
            if e1 == e2:
                joins[(e1, e2)] = e1
                continue

            e1_set, e2_set = {e1}, {e2}
            depth1, depth2 = depth[e1], depth[e2]
            while depth1 != depth2:
                if depth1 < depth2:
                    e1_set = {succ for e in e1_set for succ in edges[e]}
                    depth1 += 1
                else:
                    e2_set = {succ for e in e2_set for succ in edges[e]}
                    depth2 += 1

            itersect_e = e1_set & e2_set
            while len(itersect_e) == 0:
                e1_set = {succ for e in e1_set for succ in edges[e]}
                e2_set = {succ for e in e2_set for succ in edges[e]}
                depth1 += 1
                depth2 += 1
                itersect_e = e1_set & e2_set

            assert len(itersect_e) == 1
            joins[(e1, e2)] = joins[(e2, e1)] = itersect_e.pop()

        # partial order and coverage of two element
        cmps = None
        # cmps = {(0, 0): False}  # e1 < e2, e.g., [20, 20] < [0, 20]
        coverages = {(0, 0): True}  # e1 is covered by e2, e.g.,  [20, 20] is covered by [0, 20]
        for e1 in range(1, len(nodes)):
            # bot is less than or covered by any other elements
            coverages[(0, e1)] = True
            # cmps[(0, e1)] = True
            # cmps[(e1, 0)] = False

        for e1, e2 in itertools.product(range(1, len(nodes)), range(1, len(nodes))):
            if e1 == e2:
                coverages[(e1, e1)] = True
                # cmps[(e1, e1)] = False
                continue

            # partial order
            if depth[e1] < depth[e2]:  # (1) LHS is lower then RHS
                lhs, rhs = nodes[e1], nodes[e2]
                if (rhs[0] < lhs[0] or (rhs[0] == lhs[0] and (rhs[1] or not lhs[1]))) and \
                        (lhs[-1] < rhs[-1] or (lhs[-1] == rhs[-1] and (rhs[2] or not lhs[2]))):
                    # and (rhs[1] or not lhs[1]) and (rhs[2] or not lhs[2])
                    coverages[(e1, e2)] = True
                    # cmps[(e1, e2)] = True
                    # cmps[(e2, e1)] = False

        # [f"{nodes[e1]} < {nodes[e2]} = {flag}" for (e1, e2), flag in coverages.items()]
        # [coverages[(e1, e2)] for e1 in range(len(nodes)) for e2 in range(len(nodes))]
        return nodes, dict(edges), joins, cmps, coverages

    def decode(self, idx):
        min_v, lhs, rhs, max_v = self.nodes[idx]
        return ("[" if lhs else "(") + f"{min_v}, {max_v}" + ("]" if rhs else ")")

    def encode(self, *items):
        if len(items) == 1:
            return self.encode_element(items[0])
        else:
            ids = [self.encode_element(item) for item in items]
            join = ids[0]
            for i in ids[1:]:
                join = self.joins[(join, i)]
            return join

    def difference(self, idx1, idx2):
        def _find(interval):
            for idx, element in enumerate(self.nodes):
                if element == interval:
                    return idx
            return None

        # Attention: this function is not purely a difference function for interval.
        #               And self.nodes[idx2] must be a min interval
        if self.coveredby(idx2, idx1):
            # (1) [0, 10] - [5, 5] = [[0, 5), (5, 10]]
            interval1 = self.nodes[idx1].copy()
            interval2 = self.nodes[idx2].copy()
            if interval2[0] == interval2[-1] and interval2[1]:  # and interval2[2]:
                # interval2 is a point
                if interval2[0] == interval1[0]:
                    interval1[1] = False
                    # [0, 10] - [0, 0] = [(0, 10]]
                    for idx in self.predecessors[idx1]:
                        if interval1 == self.nodes[idx]:
                            return [idx]
                    raise ValueError(idx1, idx2)
                elif interval2[0] == interval1[-1]:
                    interval1[2] = False
                    # [0, 10] - [10, 10] = [[0, 10)]
                    for idx in self.predecessors[idx1]:
                        if interval1 == self.nodes[idx]:
                            return [idx]
                    raise ValueError(idx1, idx2)

            # [0, 10] - [5, 5] = [[0, 5), (5, 10]]
            # [0, 10] - (2, 5) = [[0, 2], [5, 10]]
            lhs_interval1 = [interval1[0], interval1[1], not interval2[1], interval2[0]]
            rhs_interval1 = [interval2[-1], not interval2[2], interval1[2], interval1[3]]
            return [_find(lhs_interval1), _find(rhs_interval1)]

        return [idx1]  # (2) [0, 10] - [20, 20] = [0, 10]


if __name__ == '__main__':
    name = "age"
    lattice = IntervalLattice.build(name, points=[0, 11, 12, 14, 25, 29, 100])

    lattice.difference(lattice.top, 1)
    lattice.difference(lattice.top, 6)

    # [0, 5) is covered by (27, 35)
    # print(lattice.coveredby(1, 5))
    # enc_idx = lattice.encode([27, False, False, 35])
    # print(enc_idx)
    # print(lattice.decode(enc_idx))

    # dump_dir = os.path.join(LATTICE_FILE_DIR, "example1")
    # lattice.dump(dump_dir)
    # print(lattice)
    #
    # del lattice
    #
    # lattice = IntervalLattice.load(name, dump_dir)
    # print(lattice)
    #
    # from order_theory.canvas import Canvas
    #
    # canvas = Canvas(name)
    # out = lattice.depict()
    # canvas.update(*out)
    # canvas.plot()
