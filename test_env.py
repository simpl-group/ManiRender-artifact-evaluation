# -*- coding:utf-8 -*-

import os
import unittest


class Test(unittest.TestCase):
    def test_EUSovler(self):
        from baselines import DIR as BASELINES_DIR
        file = os.path.join(BASELINES_DIR, "eusolver/eusolver")
        # print(os.path.abspath(file))
        self.assertTrue(os.path.exists(file))

    def test_ImageEye(self):
        from baselines.ImageEye.synthesizer import Synthesizer
        synthesizer = Synthesizer()
        self.assertEqual(synthesizer.max_synth_depth, 5)

    def test_OpenAI(self):
        from openai import OpenAI

        client = OpenAI(api_key="")

    def test_ManiRender(self):
        from order_theory import SetLattice, LazyProductLattice
        from benchmarks import DIR as BENCHMARKS_DIR

        lattice = SetLattice.load("Color", os.path.join(BENCHMARKS_DIR, ".lattices/Vehicle"))
        self.assertEqual(len(lattice.nodes), 2 ** 10)
        plattice = LazyProductLattice.build("Color_Color", [lattice, lattice])
        self.assertEqual(plattice.num_nodes, (2 ** 10 - 1) ** 2 + 1)


if __name__ == '__main__':
    unittest.main()
