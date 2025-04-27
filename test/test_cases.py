# -*- coding: utf-8 -*-

"""
Test cases:

we have two base lattices:
    - Color lattice (set): R, G, B
    - Age lattice (interval): <20, =20, >20
and their product.
"""

from order_theory import *


class TestCase:
    @staticmethod
    def testcase1():
        PERSON_RANGE = {
            "Gender": ["True", "False"],
            "Age": [0, 100],
            "Orientation": ["Front", "Back", "Side"],
            "Accessories": ["Glasses", "Hat", "UNK"],
            "HoldObjectsInFront": ["True", "False"],
            "Bag": ["BackPack", "ShoulderBag", "HandBag", "No bag"],
            "TopStyle": ["UpperStride", "UpperLogo", "UpperPlaid", "UpperSplice", "UNK"],
            "BottomStyle": ["BottomStripe", "BottomPattern", "UNK"],
            "UpperBody": ["ShortSleeve", "LongSleeve", "LongCoat", "UNK"],
            "LowerBody": ["Trousers", "Shorts", "SkirtDress", "UNK"],
            "Boots": ["True", "False"],
        }

    @staticmethod
    def testcase2():
        """
        POS: {R<, B=, R>, G=}
        NEG: {B<, G>}
        M = {R< ↦ {RG<=, R<=>}, B= ↦ {RGB=, RB>=}, R> ↦ {RB>=, R<=>}, G= ↦ {RGB=, RG<=}}
        R = {R< ↦ {RG<=, R<=>}, B= ↦ {GB=, RB>=}, R> ↦ {RB>=, R<=>}, G= ↦ {GB=, RG<=}}
        R2M = {R<=> ↦ R<=>, RG<= ↦ RG<=, RB>= ↦ RB>=, GB= ↦ RGB=}
        """
        POS = [
            [{'R'}, [0, True, False, 20]],
            [{'B'}, [20, True, True, 20]],
            [{'R'}, [20, False, True, 100]],
            [{'G'}, [20, True, True, 20]],
        ]
        maximals = [
            [
                [{'R', 'G'}, [0, True, True, 20]],
                [{'R'}, [0, True, True, 100]],
            ],
            [
                [{'R', 'G', 'B'}, [20, True, True, 20]],
                [{'R', 'B'}, [20, True, True, 100]],
            ],
            [
                [{'R', 'B'}, [20, True, True, 100]],
                [{'R'}, [0, True, True, 100]],
            ],
            [
                [{'R', 'G', 'B'}, [20, True, True, 20]],
                [{'R', 'G'}, [0, True, True, 20]],
            ],
        ]
        NEG = [
            [{'B'}, [0, True, False, 20]],
            [{'G'}, [20, False, True, 100]],
        ]

        COLOR_LATTICE = SetLattice.build('color', baseset=['R', 'G', 'B'])
        AGE_LATTICE = IntervalLattice.build('age', points=[0, 20, 100])
        LATTICE_PRODUCT = LazyProductLattice.build('product', [COLOR_LATTICE, AGE_LATTICE])

        base_lattices = [COLOR_LATTICE, AGE_LATTICE]
        lattice_product = LATTICE_PRODUCT
        POS = [lattice_product.encode(pos) for pos in POS]
        NEG = [lattice_product.encode(neg) for neg in NEG]
        maximals = [
            [lattice_product.encode(m) for m in maxes]
            for maxes in maximals
        ]
        return base_lattices, lattice_product, POS, NEG, maximals

    @staticmethod
    def testcase3():
        """
        POS: {R<, G<, G=, B=, R>, G>, B>}
        NEG: {B<, R=}
        M = {R< ↦ {RG<}, G< ↦ {RG<, GB<=>}, G= ↦ {GB<=>}, B= ↦ {GB=, RB>=}, R> ↦ {RG>, RB>=}, G> ↦ {RG>, GB>, G>=}, B> ↦ {GB>, RB>=}}
        R = {R< ↦ {RG<}, G< ↦ {RG<, G<=>}, G= ↦ {G<=>, GB>=}, B= ↦ {GB>=}, R> ↦ {RGB>}, G> ↦ {G=, GB>=, RGB>}, B> ↦ {GB>=, RBG>}}
        R2M = {}
        """
        POS = [
            [{'R'}, [0, True, False, 20]],
            [{'G'}, [0, True, False, 20]],
            [{'G'}, [20, True, True, 20]],
            [{'B'}, [20, True, True, 20]],
            [{'R'}, [20, False, True, 100]],
            [{'G'}, [20, False, True, 100]],
            [{'B'}, [20, False, True, 100]],
        ]
        NEG = [
            [{'B'}, [0, True, False, 20]],
            [{'R'}, [20, True, True, 20]],
        ]
        maximals = [
            [
                [{'R', 'G'}, [0, True, True, 20]],
            ],
            [
                [{'R', 'G'}, [0, True, True, 20]],
            ],
            [
                [{'R', 'G'}, [0, True, True, 20]],
                [{'G'}, [20, True, True, 100]],
            ],
            [
                [{'G', 'B'}, [20, True, True, 20]],
                [{'R', 'B'}, [20, True, True, 100]],
            ],
            [
                [{'R', 'G'}, [20, False, True, 100]],
                [{'R', 'B'}, [20, True, True, 100]],
            ],
            [
                [{'R', 'G'}, [20, False, True, 100]],
                [{'G', 'B'}, [20, False, True, 100]],
                [{'G'}, [20, True, True, 100]],
            ],
            [
                [{'G', 'B'}, [20, False, True, 100]],
                [{'R', 'B'}, [20, True, True, 100]],
            ]
        ]

        COLOR_LATTICE = SetLattice.build('color', baseset=['R', 'G', 'B'])
        AGE_LATTICE = IntervalLattice.build('age', points=[0, 20, 100])
        LATTICE_PRODUCT = LazyProductLattice.build('product', [COLOR_LATTICE, AGE_LATTICE])

        base_lattices = [COLOR_LATTICE, AGE_LATTICE]
        lattice_product = LATTICE_PRODUCT
        POS = [lattice_product.encode(pos) for pos in POS]
        NEG = [lattice_product.encode(neg) for neg in NEG]
        maximals = [
            [lattice_product.encode(m) for m in maxes]
            for maxes in maximals
        ]
        return base_lattices, lattice_product, POS, NEG, maximals

    @staticmethod
    def testcase4():
        color_lattice = SetLattice.build('color', baseset=['R', 'G', 'B'])
        genre_lattice = SetLattice.build('fruit', baseset=['a', 'p'])
        base_lattices = [color_lattice, genre_lattice]
        lattice_product = LazyProductLattice.build(name="product", lattices=base_lattices)
        POS = [
            [{'G'}, {'a'}],
            [{'R'}, {'p'}],
            [{'G'}, {'p'}],
            [{'B'}, {'p'}],
        ]
        NEG = [
            [{'R'}, {'a'}],
            [{'B'}, {'a'}],
        ]
        POS = [lattice_product.encode(pos) for pos in POS]
        NEG = [lattice_product.encode(neg) for neg in NEG]
        maximals = [
            [
                [{'G'}, {'a', 'p'}],
                [{'B', 'R', 'G'}, {'p'}],
            ]
        ]
        return base_lattices, lattice_product, POS, NEG, maximals

    @staticmethod
    def testcase5():
        color_lattice = SetLattice.build('color', baseset=['R', 'G', 'B'])
        genre_lattice = SetLattice.build('fruit', baseset=['a', 'p'])
        base_lattices = [color_lattice, genre_lattice]
        lattice_product = LazyProductLattice.build(name="product", lattices=base_lattices)
        POS = [
            [{'G'}, {'a'}],
            [{'R'}, {'p'}],
            [{'B'}, {'p'}],
        ]
        NEG = [
            [{'R'}, {'a'}],
            [{'B'}, {'a'}],
            [{'G'}, {'p'}],
        ]
        POS = [lattice_product.encode(pos) for pos in POS]
        NEG = [lattice_product.encode(neg) for neg in NEG]
        maximals = [
            [
                [{'G'}, {'a'}],
                [{'B', 'R'}, {'p'}],
            ]
        ]
        return base_lattices, lattice_product, POS, NEG, maximals
