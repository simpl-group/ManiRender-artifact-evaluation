# -*- coding: utf-8 -*-

from __future__ import annotations

import itertools
import os
import pickle
from typing import *

from constants import LATTICE_FILE_DIR
from order_theory.lattice import Lattice
from utils import foldl_mul
from functools import reduce
from operator import mul


class LazyProductLattice(Lattice):
    """
    LazyProductLattice is a lazy evaluation version of the product of lattice. It efficiently works for searching
    elements satisfying positive samples but rejecting negative samples.
    """

    def __init__(self, name: str, **kwargs):
        self.sublattices: Optional[List[Lattice]] = kwargs["sublattices"]
        self.subl_nodes = [range(1, len(l.nodes)) for l in self.sublattices]
        self.num_base_nodes = foldl_mul([len(l.successors[0]) for l in self.sublattices])
        self.num_nodes = foldl_mul([len(l.nodes) - 1 for l in self.sublattices]) + 1
        # self._BLOCK_NUM is used to compute indices
        self._BLOCK_NUM = [len(self.sublattices[-1].nodes) - 1]
        for sub_l in self.sublattices[:-1][::-1]:
            self._BLOCK_NUM.append(self._BLOCK_NUM[-1] * (len(sub_l.nodes) - 1))
        self._BLOCK_NUM = self._BLOCK_NUM[::-1]

        self.relations: Optional[List[str]] = kwargs.get("relations", None)
        self.name: str = name
        self.type: Optional[str] = kwargs.get("type", None)
        self.node_label_func: Optional[Callable] = kwargs.get("node_label_func", None)
        self._indices = None

    @property
    def top(self):
        return tuple(sub_l.top for sub_l in self.sublattices)

    @property
    def bot(self):
        return tuple(sub_l.bot for sub_l in self.sublattices)

    @classmethod
    def build(cls, name: str, lattices: List[Lattice], **kwargs) -> LazyProductLattice:
        lattice = cls(name, sublattices=lattices, relations=[l.relation for l in lattices], type='lazy')
        # print(lattice.nodes(2))
        # print(lattice.successors(0))
        # print(lattice.successors(2))
        return lattice

    @property
    def base_elements(self):
        return itertools.product(*[sub_l.base_elements for sub_l in self.sublattices])

    def _index2indices(self, idx):
        index = []
        i = 0
        remainder = idx - 1
        for _ in range(len(self.sublattices) - 1):
            quotient, remainder = remainder // self._BLOCK_NUM[i], remainder % self._BLOCK_NUM[i]
            index.append(quotient)
        index.append(remainder)
        return index

    def idx2coord(self, idx):
        # convert i-th node to an indices of sub-lattices
        # assert idx < self.num_nodes
        if idx == 0:
            return self.bot
        else:
            return [subl_nodes[idx] for subl_nodes, idx in zip(self.subl_nodes, self._index2indices(idx))]

    def coord2idx(self, coord):
        # the reversed function of `idx2coord`
        index = 1
        for idx, c in enumerate(coord[:-1], start=1):
            index += (idx - 1) * self._BLOCK_NUM[idx]
        index += coord[-1] - 1
        return index

    def join(self, lhs: Tuple, rhs: Tuple) -> Tuple:
        return tuple(sub_l.joins[(e1, e2)] for sub_l, e1, e2 in zip(self.sublattices, lhs, rhs))

    def joins(self, elements: List) -> Tuple:
        join = elements[0]
        for e in elements[1:]:
            join = self.join(join, e)
        return join

    def dump(self, dump_dir: str = None):
        dump_dir = dump_dir or LATTICE_FILE_DIR
        os.makedirs(dump_dir, exist_ok=True)
        file = os.path.join(dump_dir, f"{self.name}.lattice")
        dump_data = {
            '_indices': self._indices, 'relations': self.relations,
            'name': self.name, 'type': self.type, 'sublattices': [sub_l.name for sub_l in self.sublattices],
        }
        with open(file, 'wb') as writer:
            pickle.dump(dump_data, writer)

    @staticmethod
    def load(name: str, dump_dir: str = None) -> LazyProductLattice:
        dump_dir = dump_dir or LATTICE_FILE_DIR
        file = os.path.join(dump_dir, f"{name}.lattice")
        with open(file, 'rb') as reader:
            dump_data: Dict = pickle.load(reader)
        dump_data['sublattices'] = [Lattice.load(sub_l) for sub_l in dump_data['sublattices']]

        from order_theory.enum_product_lattice import EnumerativeProductLattice

        self = {'lazy': LazyProductLattice, 'enum': EnumerativeProductLattice}[dump_data['type']] \
            (name)
        for k, v in dump_data.items():
            setattr(self, k, v)
        if dump_data['type'] == 'enum':
            self.node_label_func: Callable = lambda xs: '(' + ', '.join([sub_l.node_label_func(sub_l.nodes[x]) for (
                sub_l, x) in zip(dump_data['sublattices'], xs)]) + ')' if isinstance(xs, Tuple) else xs
        return self

    def predecessors(self, element: Tuple) -> List[Tuple]:
        # predecessors ≼ node ≼ successors
        """
        :param element: a node presenting in an indices in sub-lattices
        :return: return the nodes' predecessors
        """
        pred = []
        for l_idx, (sub_l, e_idx) in enumerate(zip(self.sublattices, element)):
            if e_idx not in sub_l.predecessors:
                continue
            template = list(element)
            for f_idx in sub_l.predecessors[e_idx]:
                template[l_idx] = f_idx
                if f_idx == 0:
                    pred.append(self.bot)
                else:
                    pred.append(tuple(template))
        return pred

    def successors(self, element: Tuple) -> List[Tuple]:
        # predecessors ≼ node ≼ successors
        """
        :param element: a node presenting in an indices in sub-lattices
        :return: return the nodes' successors
        """
        # assert len(element) == len(self.sublattices) and \
        #        all((e < len(sub_l.nodes)) for sub_l, e in zip(self.sublattices, element))
        # print([sub_l.nodes[idx] for sub_l, idx in zip(self.sublattices, element)])

        succ = []
        for l_idx, (sub_l, e_idx) in enumerate(zip(self.sublattices, element)):
            if e_idx not in sub_l.successors:
                continue
            template = list(element)
            for f_idx in sub_l.successors[e_idx]:
                template[l_idx] = f_idx
                succ.append(tuple(template))
                # print([sub_l.nodes[idx] for sub_l, idx in zip(self.sublattices, template)])

        # e_string = [l.node_label_func(l.nodes[idx]) for l, idx in zip(self.sublattices, element)]
        # fathers_string = [[l.node_label_func(l.nodes[idx]) for l, idx in zip(self.sublattices, e)] for e in fathers]
        # print(f'{e_string} -> {fathers_string}')
        return succ

    # def less(self, lhs, rhs) -> bool:
    #     return all(l.less(left, right) for l, left, right in zip(self.sublattices, lhs, rhs))
    #
    # def leq(self, lhs, rhs) -> bool:
    #     return all(l.leq(left, right) for l, left, right in zip(self.sublattices, lhs, rhs))

    def coveredby(self, lhs, rhs) -> bool:
        return all(l.coveredby(left, right) for l, left, right in zip(self.sublattices, lhs, rhs))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{' × '.join(l._string for l in self.sublattices)}, ({', '.join(self.relations)})>"

    def encode(self, items) -> Tuple:
        """
        :param items: (e1, e2, ...) where e_i is the element of i-th sub-lattice
        :return: return (idx1, idx2, ...)
        e.g. ('R', [0, 20)) -> (1, 1)
        """
        return tuple(sub_l.encode(itm) for itm, sub_l in zip(items, self.sublattices))

    def decode(self, element: Tuple) -> Tuple:
        return tuple(l.node_label_func(l.nodes[idx]) for l, idx in zip(self.sublattices, element))

    def depict(self):
        raise NotImplementedError(
            'Lazy Product Lattice does not support visualization, please refer to Enumerative Product Lattice')

    def difference(self, ids1, ids2):
        for i, (idx1, idx2, sub_l) in enumerate(zip(ids1, ids2, self.sublattices)):
            if idx1 == idx2:
                continue
            for compl in sub_l.difference(idx1, idx2):
                new_subset = list(ids1)
                new_subset[i] = compl
                yield tuple(new_subset)


if __name__ == '__main__':
    from order_theory import SetLattice, IntervalLattice

    color_lattice = SetLattice.build('color', ['R', 'G', 'B'])
    num_lattice = IntervalLattice.build('num', [0, 10, 20, 40])
    lattice = LazyProductLattice.build("product", lattices=[color_lattice, num_lattice])
    print(lattice)

    node = ('R', '1')
    element = lattice.encode(node)
    succs = lattice.successors(element)
    print(f"Successors of {node}: {[lattice.decode(s) for s in succs]}")
    preds = lattice.predecessors(succs[0])
    print(f"Predecessors of {lattice.decode(succs[0])}: {[lattice.decode(p) for p in preds]}")

    POS = [('R', [0, True, True, 0]), ('G', [40, True, True, 40])]
    NEG = [('B', [10, True, True, 10]), ('G', [20, True, True, 20])]
    POS, NEG = map(lambda xs: [lattice.encode(x) for x in xs], (POS, NEG))
    print(POS)
    print(NEG)

    from search.util import cover_positives, is_valid

    maximals = [lattice.top]
    for neg in NEG:
        new_maximals = []
        for maximal in maximals:
            new_maxs = lattice.difference(maximal, neg)
            print([lattice.decode(new_max) for new_max in new_maxs])
            new_maxs = [new_max for new_max in new_maxs if cover_positives(new_max, POS, lattice)]
            new_maximals += new_maxs
        maximals = new_maximals
    print(maximals)
    for maximal in maximals:
        assert is_valid(maximal, NEG, lattice)
    print([lattice.decode(maximal) for maximal in maximals])
