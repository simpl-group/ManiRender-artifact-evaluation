# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import defaultdict
from functools import reduce
from operator import mul
from typing import *

from ordered_set import OrderedSet

from order_theory.lattice import Lattice
from order_theory.lazy_product_lattice import LazyProductLattice


class EnumerativeProductLattice(LazyProductLattice):
    """
    EnumerativeProductLattice is an enumerative product of lattice, i.e., containing all elements and their
    relations. This class is specifically designed to visualize the product of lattices.
    """

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    @classmethod
    def build(cls, name: str, lattices: List[Lattice], **kwargs) -> EnumerativeProductLattice:
        lazy_lattice_product = super().build(name, lattices)
        nodes, edges = list(lazy_lattice_product.base_elements), lazy_lattice_product.edges
        type: str = 'enum'

        node_label_func: Callable = lambda xs: '(' + ', '.join([sub_l.node_label_func(sub_l.nodes[x]) for (
            sub_l, x) in zip(lattices, xs)]) + ')' if isinstance(xs, Tuple) else xs
        relations: List[str] = [l.relation for l in lattices]
        sublattices: List[Lattice] = lattices
        self = EnumerativeProductLattice(
            name, sublattices=sublattices, nodes=nodes, edges=edges, relations=relations,
            type=type, node_label_func=node_label_func
        )

        # compute all edges
        finished = set()
        nodes = OrderedSet(self.nodes)
        edges = defaultdict(set)
        for k, v in self.edges.items():
            edges[k] = v
        num_elements = reduce(mul, [len(sub_l.nodes) - 1 for sub_l in lattices], 1)
        while num_elements != len(finished):
            for e in set(edges.keys()):
                if e in finished:
                    continue
                for dst in edges[e]:
                    for f_id in super(EnumerativeProductLattice, self).joins(nodes[dst]):
                        nodes.add(f_id)
                        edges[dst].add(nodes.index(f_id))
                finished.add(e)
        self.nodes = nodes.items
        self.edges = dict(edges)
        self._indices = [str(idx) for idx in range(len(self.nodes))]
        return self

    def joins(self, element: Tuple) -> List[Tuple]:
        idx = self.nodes.index(element)
        return [self.nodes[i] for i in self.edges[idx]]

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


if __name__ == '__main__':
    from order_theory import SetLattice

    color_lattice = SetLattice.build('color', baseset=['R', 'G', 'B'])
    num_lattice = SetLattice.build('num', baseset=['1', '2', '3', '4'])
    lattice = EnumerativeProductLattice.build("product", lattices=[color_lattice, num_lattice])
    lattice.dump()
    print(lattice)

    from order_theory.canvas import Canvas

    canvas = Canvas('plot')
    out = lattice.depict()
    canvas.update(*out)
    canvas.plot()
