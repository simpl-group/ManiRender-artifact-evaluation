# -*- coding: utf-8 -*-

import itertools
from collections import defaultdict
from typing import *

from constants import NODE_LABEL_FUNCS, BOTTOM
from order_theory.lattice import Lattice


class SetLattice(Lattice):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    @classmethod
    def build(cls, name: str, baseset: List, relation: str = '⊆') -> Lattice:
        nodes, edges, joins, cmps, coverages = cls.powerset(baseset)
        type = "set"
        node_label_func = NODE_LABEL_FUNCS[type]
        lattice = cls(name, nodes=nodes, edges=edges, joins=joins, cmps=cmps, coverages=coverages,
                      relation=relation, node_label_func=node_label_func,
                      type=type)
        return lattice

    @staticmethod
    def powerset(baseset: List):
        # ⊥ ⊆ {e} for any e in S
        nodes = [BOTTOM] + [{e} for e in baseset]
        depth = {}
        prev_map = {e: idx for e, idx in zip(baseset, itertools.count(1))}
        edges = defaultdict(set)
        for idx in range(1, len(baseset) + 1):
            edges[0].add(idx)
            depth[idx] = 1
        for length in range(2, len(baseset)):
            curr_map = {}
            for fset in map(list, itertools.combinations(baseset, length)):
                nodes.append(set(fset))
                curr_map[''.join(fset)] = curr_idx = len(nodes) - 1
                for drop_i in range(len(fset)):
                    subset = ''.join(e for i, e in enumerate(fset) if i != drop_i)
                    edges[prev_map[subset]].add(curr_idx)
                    depth[curr_idx] = length
            prev_map = curr_map
        nodes.append(set(baseset))
        for prev_idx in prev_map.values():
            edges[prev_idx].add(len(nodes) - 1)
        depth[len(nodes) - 1] = len(baseset)

        # joins of two elements
        joins = {}  # e1 \/ e2
        for e1, e2 in itertools.product(range(1, len(nodes)), range(1, len(nodes))):
            # joins
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
        # cmps = {(0, 0): False}  # e1 < e2, e.g., {G} < {G, B}
        coverages = {(0, 0): True}  # e1 is covered by e2, e.g.,  {R} is covered by {G, B}
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
            if depth[e1] < depth[e2]:
                if all(e in nodes[e2] for e in nodes[e1]):
                    coverages[(e1, e2)] = True
                    # cmps[(e1, e2)] = True
                    # cmps[(e2, e1)] = False
            # else:
            #     # depth[e1] >= depth[e2]
            #     coverages[(e1, e2)] = False
        # [f"{nodes[e1]} < {nodes[e2]} = {flag}" for (e1, e2), flag in coverages.items()]
        # [coverages[(e1, e2)] for e1 in range(len(nodes)) for e2 in range(len(nodes))]
        return nodes, dict(edges), joins, cmps, coverages

    def max_incomparable_elements(self, neg_es):
        pop_es = set()
        for neg_e in neg_es:
            pop_es |= self.nodes[neg_e]
        return [self.nodes.index(self.nodes[-1] - pop_es)]

    def encode_element(self, item):
        for idx in self.base_elements:
            if self.nodes[idx] == {item}:
                return idx

    def encode(self, items):
        if isinstance(items, list):
            ids = [self.encode_element(item) for item in items]
            return self.join(ids)
        else:
            return self.encode_element(items)

    def difference(self, idx1, idx2):
        # Attention: this function is not purely a difference function for set.
        #               And self.nodes[idx2] must be a singleton
        if self.coveredby(idx2, idx1):
            for subset in self.predecessors[idx1]:
                if not self.coveredby(idx2, subset):
                    return [subset]  # (1) {R, G, B} - {B} = {R, G}
            raise ValueError
        return [idx1]  # (2) {R, G} - {B} = {R, G}


if __name__ == '__main__':
    name = "color"
    lattice = SetLattice.build(name, baseset=['R', 'G', 'B'])

    lattice.difference(lattice.top, 1)

    # {R} is covered by {G, B}
    # print(lattice.coveredby(1, 6))
    # enc_idx = lattice.encode('R')
    # print(enc_idx)
    # print(lattice.decode(enc_idx))

    # dump_dir = os.path.join(LATTICE_FILE_DIR, "example1")
    # lattice.dump(dump_dir)
    # print(lattice)
    #
    # del lattice
    #
    # lattice = Lattice.load(name, dump_dir)
    # print(lattice)
    #
    # from order_theory.canvas import Canvas
    #
    # canvas = Canvas(name)
    # out = lattice.depict()
    # canvas.update(*out)
    # canvas.plot()
