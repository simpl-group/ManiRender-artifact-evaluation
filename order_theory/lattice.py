# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import pickle
from collections import defaultdict
from typing import *

from constants import LATTICE_FILE_DIR, NODE_LABEL_FUNCS


class Lattice:
    def __init__(self, name: str, **kwargs):
        self.nodes: Optional[List] = kwargs.get("nodes", None)
        if self.nodes is not None:
            self._indices = [str(i) for i in range(len(self.nodes))]
        self.edges: Optional[Dict] = kwargs.get("edges", None)
        self.joins: Optional[Dict] = kwargs.get("joins", None)
        self.cmps: Optional[Dict] = kwargs.get("cmps", None)
        self.coverages: Optional[Dict] = kwargs.get("coverages", None)

        # predecessors ≼ node ≼ successors
        if self.edges is not None:
            self.successors = self.edges
            self.predecessors = defaultdict(set)
            for src, dsts in self.edges.items():
                for dst in dsts:
                    self.predecessors[dst].add(src)
            self.predecessors = dict(self.predecessors)

        self.relation: Optional[str] = kwargs.get("relation", None)
        self.name: str = name
        self.type: str = kwargs.get("type", "default")
        self.node_label_func: Callable = kwargs.get("node_label_func", NODE_LABEL_FUNCS[self.type])
        self._string = None
        if self.nodes is not None and self.successors is not None:
            # base elements
            self.base_elements = set(self.successors[0])
            # self.top = len(self.nodes) - 1
            if self.type == 'set':
                self._string = str(self.nodes[-1])
            elif self.type == 'interval':
                self._string = '{' + ', '.join(
                    [self.node_label_func(self.nodes[idx]) for idx in self.base_elements]) + '}'
            else:
                raise NotImplementedError(self.type)
        # self.top = len(self.nodes) - 1
        # self.bot = 0

    @property
    def top(self):
        return len(self.nodes) - 1

    @property
    def bot(self):
        return 0

    @staticmethod
    def powerset(*args, **kwargs):
        raise NotImplementedError

    @classmethod
    def build(cls, *args, **kwargs) -> Lattice:
        raise NotImplementedError

    def dump(self, dump_dir: str = None):
        dump_dir = dump_dir or LATTICE_FILE_DIR
        os.makedirs(dump_dir, exist_ok=True)
        file = os.path.join(dump_dir, f"{self.name}.lattice")
        dump_data = {
            'nodes': self.nodes, '_indices': self._indices, 'edges': self.edges, 'joins': self.joins,
            'cmps': self.cmps, 'coverages': self.coverages, 'successors': self.successors, 'top': self.top,
            'predecessors': self.predecessors, 'relation': self.relation, 'name': self.name, 'type': self.type,
            'base_elements': self.base_elements, '_string': self._string
        }
        with open(file, 'wb') as writer:
            pickle.dump(dump_data, writer)

    @staticmethod
    def load(name: str, dump_dir: str = None) -> Lattice:
        dump_dir = dump_dir or LATTICE_FILE_DIR
        file = os.path.join(dump_dir, f"{name}.lattice")
        with open(file, 'rb') as reader:
            dump_data: Dict = pickle.load(reader)

        from order_theory.set_lattice import SetLattice
        from order_theory.interval_lattice import IntervalLattice

        self = {'default': Lattice, 'set': SetLattice, 'interval': IntervalLattice}[dump_data['type']](name)
        for k, v in dump_data.items():
            if k in {'top', 'bot'}:
                continue
            else:
                setattr(self, k, v)
        self.node_label_func = NODE_LABEL_FUNCS[self.type]
        return self

    def coveredby(self, lhs, rhs):
        return (lhs, rhs) in self.coverages

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.name} = {self._string}, {self.relation}>"

    def encode_element(self, item):
        for idx in self.base_elements:
            if self.nodes[idx] == item:
                return idx

    def encode(self, *items):
        raise NotImplementedError

    def decode(self, idx):
        return self.nodes[idx]

    def difference(self, idx1, idx2):
        raise NotImplementedError

    @staticmethod
    def from_name(name, **kwargs) -> Lattice:
        from order_theory.set_lattice import SetLattice
        from order_theory.interval_lattice import IntervalLattice
        type = kwargs.get('type', 'default')
        lattice = {
            'default': Lattice,
            'set': SetLattice,
            'interval': IntervalLattice,
        }[type](name)
        lattice.node_label_func = NODE_LABEL_FUNCS[type]
        lattice.load()
        return lattice

    def depict(self):
        nodes = [
            {
                'data': {'id': idx, 'label': self.node_label_func(n)},
                'classes': f'{self.name}-node'
            }
            for idx, n in zip(self._indices, self.nodes)
        ]
        edges = [
            {'data': {'source': self._indices[src], 'target': self._indices[dst]}, 'classes': f'{self.name}-edge'}
            for idx, (src, dsts) in enumerate(self.edges.items())
            for dst in dsts
        ]
        styles = [
            {
                'selector': f'{self.name}-node',
                'style': {
                    'content': 'data(label)',
                    'background-color': '#000000',
                }
            },
            # {
            #     'selector': f'{self.name}-edge',
            #     'style': {
            #     }
            # },
        ]
        return nodes, edges, styles

    def join(self, ids):
        join = ids[0]
        for i in ids[1:]:
            join = self.joins[(join, i)]
        return join
