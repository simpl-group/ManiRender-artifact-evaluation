# -*- coding:utf-8 -*-
# Author: Yang He
# Data: 2024/05/20

"""
Program adapted from https://github.com/celestebarnaby/ImageEye.
Thank Celeste Barnaby's opensource codes!
"""

from semantics import semantics_types
from semantics import semantics_lia
from semantics.semantics_types import InterpretedFunctionBase
from exprs import exprtypes
from utils import utils
import re


class Or(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Or', 2,
                         (exprtypes.BoolType(), exprtypes.BoolType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a or b


class And(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('And', 2,
                         (exprtypes.BoolType(), exprtypes.BoolType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a and b


class Not(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Not', 1,
                         (exprtypes.BoolType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda x: not x


class Color(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Color', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Color', None) == b


class Type(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Type', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Type', None) == b


class Male(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Male', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('Male', False)


class AgeLess(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('AgeLess', 2,
                         (exprtypes.ObjType(), exprtypes.IntType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Age', 99999) < b


class AgeGreater(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('AgeGreater', 2,
                         (exprtypes.ObjType(), exprtypes.IntType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Age', -99999) > b


class AgeEq(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('AgeEq', 2,
                         (exprtypes.ObjType(), exprtypes.IntType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Age', None) == b


class Orientation(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Orientation', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Orientation', None) == b


class Glasses(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Glasses', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('Glasses', False)


class Hat(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Hat', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('Hat', False)


class HoldObjectsInFront(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('HoldObjectsInFront', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('HoldObjectsInFront', False)


class Bag(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Bag', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Bag', None) == b


class TopStyle(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('TopStyle', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('TopStyle', None) == b


class BottomStyle(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('BottomStyle', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('BottomStyle', None) == b


class ShortSleeve(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('ShortSleeve', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('ShortSleeve', False)


class LongSleeve(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('LongSleeve', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('LongSleeve', False)


class LongCoat(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('LongCoat', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('LongCoat', False)


class Trousers(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Trousers', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('Trousers', False)


class Shorts(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Shorts', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('Shorts', False)


class SkirtDress(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('SkirtDress', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('SkirtDress', False)


class Boots(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Boots', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('Boots', False)


class Empty(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Empty', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('Empty', False)


class PureNumber(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('PureNumber', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('PureNumber', False)


class PureAlphabet(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('PureAlphabet', 1,
                         (exprtypes.ObjType(),),
                         exprtypes.BoolType())
        self.eval_children = lambda a: a.get('PureAlphabet', False)


class LengthLess(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('LengthLess', 2,
                         (exprtypes.ObjType(), exprtypes.IntType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Length', 99999) < b


class LengthEq(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('LengthEq', 2,
                         (exprtypes.ObjType(), exprtypes.IntType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Length', None) == b


class LengthGreater(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('LengthGreater', 2,
                         (exprtypes.ObjType(), exprtypes.IntType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: a.get('Length', -99999) > b


class StartsWith(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('StartsWith', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: str.startswith(a.get('Context', ''), b)


class EndsWith(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('EndsWith', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: str.endswith(a.get('Context', ''), b)


class In(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('In', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: b in a.get('Context', '')


class Regex(InterpretedFunctionBase):
    def __init__(self):
        super().__init__('Regex', 2,
                         (exprtypes.ObjType(), exprtypes.StringType()),
                         exprtypes.BoolType())
        self.eval_children = lambda a, b: re.search(b, a.get('Context', '')) is not None


class OBJInstantiator(semantics_types.InstantiatorBase):
    def __init__(self):
        super().__init__('obj')
        self.lia_instantiator = semantics_lia.LIAInstantiator()
        self.function_types = {
            'Or': (exprtypes.BoolType(), exprtypes.BoolType()),
            'And': (exprtypes.BoolType(), exprtypes.BoolType()),
            'Not': (exprtypes.BoolType(),),
            # userdefined functions
            # vehicle
            'Color': (exprtypes.ObjType(), exprtypes.StringType()),
            'Type': (exprtypes.ObjType(), exprtypes.StringType()),
            # person
            'Male': (exprtypes.ObjType(),),
            'AgeLess': (exprtypes.ObjType(), exprtypes.IntType()),
            'AgeGreater': (exprtypes.ObjType(), exprtypes.IntType()),
            'AgeEq': (exprtypes.ObjType(), exprtypes.IntType()),
            'Orientation': (exprtypes.ObjType(), exprtypes.StringType()),
            'Glasses': (exprtypes.ObjType(),),
            'Hat': (exprtypes.ObjType(),),
            'HoldObjectsInFront': (exprtypes.ObjType(),),
            'Bag': (exprtypes.ObjType(), exprtypes.StringType()),
            'TopStyle': (exprtypes.ObjType(), exprtypes.StringType()),
            'BottomStyle': (exprtypes.ObjType(), exprtypes.StringType()),
            'ShortSleeve': (exprtypes.ObjType(),),
            'LongSleeve': (exprtypes.ObjType(),),
            'LongCoat': (exprtypes.ObjType(),),
            'Trousers': (exprtypes.ObjType(),),
            'Shorts': (exprtypes.ObjType(),),
            'SkirtDress': (exprtypes.ObjType(),),
            'Boots': (exprtypes.ObjType(),),
            # text
            'Empty': (exprtypes.ObjType(),),
            'PureNumber': (exprtypes.ObjType(),),
            'PureAlphabet': (exprtypes.ObjType(),),
            'LengthLess': (exprtypes.ObjType(), exprtypes.IntType()),
            'LengthEq': (exprtypes.ObjType(), exprtypes.IntType()),
            'LengthGreater': (exprtypes.ObjType(), exprtypes.IntType()),
            'StartsWith': (exprtypes.ObjType(), exprtypes.StringType()),
            'EndsWith': (exprtypes.ObjType(), exprtypes.StringType()),
            'In': (exprtypes.ObjType(), exprtypes.StringType()),
            'Regex': (exprtypes.ObjType(), exprtypes.StringType()),
        }
        self.function_instances = {
            'Or': Or(),
            'And': And(),
            'Not': Not(),
            # userdefined functions
            # vehicle
            'Color': Color(),
            'Type': Type(),
            # person
            'Male': Male(),
            'AgeLess': AgeLess(),
            'AgeGreater': AgeGreater(),
            'AgeEq': AgeEq(),
            'Orientation': Orientation(),
            'Glasses': Glasses(),
            'Hat': Hat(),
            'HoldObjectsInFront': HoldObjectsInFront(),
            'Bag': Bag(),
            'TopStyle': TopStyle(),
            'BottomStyle': BottomStyle(),
            'ShortSleeve': ShortSleeve(),
            'LongSleeve': LongSleeve(),
            'LongCoat': LongCoat(),
            'Trousers': Trousers(),
            'Shorts': Shorts(),
            'SkirtDress': SkirtDress(),
            'Boots': Boots(),
            # text
            'Empty': Empty(),
            'PureNumber': PureNumber(),
            'PureAlphabet': PureAlphabet(),
            'LengthLess': LengthLess(),
            'LengthEq': LengthEq(),
            'LengthGreater': LengthGreater(),
            'StartsWith': StartsWith(),
            'EndsWith': EndsWith(),
            'In': In(),
            'Regex': Regex(),
        }

    def _get_canonical_function_name(self, function_name):
        return function_name

    def _do_instantiation(self, function_name, mangled_name, arg_types):
        if function_name not in self.function_types:
            return None

        assert arg_types == self.function_types[function_name]
        return self.function_instances[function_name]
