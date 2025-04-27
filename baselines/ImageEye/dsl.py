# -*- coding:utf-8 -*-

"""
Program adapted from https://github.com/celestebarnaby/ImageEye.
Thank Celeste Barnaby's opensource codes!
"""

import copy
from typing import List, Dict, Any
from constants import CODOMAINS, PERSON, VEHICLE, TEXT
from enum import Enum


class Node:
    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Node)

    def __lt__(self, other):
        self_str = str(self)
        other_str = str(other)
        if self_str == "Hole" and other_str == "Hole":
            return self_str < other_str
        elif self_str == "Hole":
            return False
        elif other_str == "Hole":
            return True
        elif "Hole" in self_str and "Hole" in other_str:
            return self_str < other_str
        elif "Hole" in other_str:
            return True
        elif "Hole" in self_str:
            return False
        return self_str < other_str


class Program(Node):
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return str([str(statement) + "; " for statement in self.statements])

    def duplicate(self):
        new_statements = copy.copy(self.statements)
        return Program(new_statements)


class Statement(Program):
    pass


class ApplyAction(Statement):
    def __init__(self, action, extractor):
        self.action = action
        self.extractor = extractor

    def __str__(self):
        return (
                type(self).__name__
                + "("
                + str(self.action)
                + ", "
                + str(self.extractor)
                + ")"
        )


# ========================================================= #
#                         Action
# ========================================================= #

class Action(Node):
    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


# ========================================================= #
#                         Extractor
# ========================================================= #

class Extractor(Node):
    def __init__(self, val=None, output_under=None, output_over=None):
        self.val = val
        self.output_under = output_under  # I-
        self.output_over = output_over  # I+

    def __eq__(self, other):
        return str(self) == str(other)

    def duplicate(self):
        return self.__class__(self.val, self.output_under, self.output_over)

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()


class Or(Extractor):
    def __init__(
            self, extractors: List[Extractor], val=None, output_under=None, output_over=None
    ):
        super().__init__(val, output_under, output_over)
        self.extractors = extractors

    def __str__(self):
        extractor_strs = [str(extr) for extr in self.extractors]
        return type(self).__name__ + "[" + ", ".join(extractor_strs) + "]"

    def duplicate(self):
        return Or(self.extractors, self.val, self.output_under, self.output_over)

    def __eq__(self, other):
        if isinstance(other, Or):
            return self.extractors == other.extractors
        return False


class And(Extractor):
    def __init__(
            self, extractors: List[Extractor], val=None, output_under=None, output_over=None
    ):
        super().__init__(val, output_under, output_over)
        self.extractors = extractors

    def __str__(self):
        extractor_strs = [str(extr) for extr in self.extractors]
        return type(self).__name__ + "[" + ", ".join(extractor_strs) + "]"

    def duplicate(self):
        return And(
            self.extractors, self.val, self.output_under, self.output_over
        )

    def __eq__(self, other):
        if isinstance(other, And):
            return self.extractors == other.extractors
        return False


class Not(Extractor):
    def __init__(
            self, extractor: Extractor, val=None, output_under=None, output_over=None
    ):
        super().__init__(val, output_under, output_over)
        self.extractor = extractor

    def __str__(self):
        return type(self).__name__ + "(" + str(self.extractor) + ")"

    def duplicate(self):
        return Not(self.extractor, self.val, self.output_under, self.output_over)

    def __eq__(self, other):
        if isinstance(other, Not):
            return self.extractor == other.extractor
        return False


# ========================================================= #
#                         Attribute
# ========================================================= #

class Attribute(Extractor):
    pass


class IsVehicle(Attribute):
    pass


class GetColor(Attribute):
    def __init__(self, color, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.color = color

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.color == other.color

    def duplicate(self):
        return self.__class__(self.color, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.color})"


class GetType(Attribute):
    def __init__(self, type, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.type = type

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.type == other.type

    def duplicate(self):
        return self.__class__(self.type, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.type})"


class IsPerson(Attribute):
    pass


class IsMale(Attribute):
    pass


class IsAgeLess(Attribute):
    def __init__(self, age, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.age = age

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.age == other.age

    def duplicate(self):
        return self.__class__(self.age, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.age})"


class IsAgeEq(Attribute):
    def __init__(self, age, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.age = age

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.age == other.age

    def duplicate(self):
        return self.__class__(self.age, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.age})"


class IsAgeGreater(Attribute):
    def __init__(self, age, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.age = age

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.age == other.age

    def duplicate(self):
        return self.__class__(self.age, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.age})"


class GetOrientation(Attribute):
    def __init__(self, orientation, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.orientation = orientation

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.orientation == other.orientation

    def duplicate(self):
        return self.__class__(self.orientation, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.orientation})"


class IsGlasses(Attribute):
    pass


class IsHat(Attribute):
    pass


class IsHoldObjectsInFront(Attribute):
    pass


class GetBag(Attribute):
    def __init__(self, bag, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.bag = bag

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.bag == other.bag

    def duplicate(self):
        return self.__class__(self.bag, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.bag})"


class GetTopStyle(Attribute):
    def __init__(self, topstyle, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.topstyle = topstyle

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.topstyle == other.topstyle

    def duplicate(self):
        return self.__class__(self.topstyle, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.topstyle})"


class GetBottomStyle(Attribute):
    def __init__(self, bottomstyle, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.bottomstyle = bottomstyle

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.bottomstyle == other.bottomstyle

    def duplicate(self):
        return self.__class__(self.bottomstyle, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.bottomstyle})"


class IsShortSleeve(Attribute):
    pass


class IsLongSleeve(Attribute):
    pass


class IsLongCoat(Attribute):
    pass


class IsTrousers(Attribute):
    pass


class IsShorts(Attribute):
    pass


class IsSkirtDress(Attribute):
    pass


class IsBoots(Attribute):
    pass


class IsText(Attribute):
    pass


class IsEmpty(Attribute):
    pass


class IsPureNumber(Attribute):
    pass


class IsPureAlphabet(Attribute):
    pass


class IsLengthLess(Attribute):
    def __init__(self, length, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.length = length

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.length == other.length

    def duplicate(self):
        return self.__class__(self.length, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.length})"


class IsLengthEq(Attribute):
    def __init__(self, length, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.length = length

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.length == other.length

    def duplicate(self):
        return self.__class__(self.length, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.length})"


class IsLengthGreater(Attribute):
    def __init__(self, length, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.length = length

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.length == other.length

    def duplicate(self):
        return self.__class__(self.length, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.length})"


class IsStartsWith(Attribute):
    def __init__(self, substr, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.substr = substr

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.substr == other.substr

    def duplicate(self):
        return self.__class__(self.substr, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.substr})"


class IsEndsWith(Attribute):
    def __init__(self, substr, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.substr = substr

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.substr == other.substr

    def duplicate(self):
        return self.__class__(self.substr, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.substr})"


class IsIn(Attribute):
    def __init__(self, substr, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.substr = substr

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.substr == other.substr

    def duplicate(self):
        return self.__class__(self.substr, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.substr})"


class IsRegexMatch(Attribute):
    def __init__(self, substr, val=None, output_under=None, output_over=None):
        super().__init__(val, output_under, output_over)
        self.substr = substr

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.substr == other.substr

    def duplicate(self):
        return self.__class__(self.substr, self.val, self.output_under, self.output_over)

    def __str__(self):
        return f"{self.__class__.__name__}({self.substr})"
