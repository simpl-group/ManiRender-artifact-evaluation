# -*- coding:utf-8 -*-

"""
Program adapted from https://github.com/celestebarnaby/ImageEye.
Thank Celeste Barnaby's opensource codes!
"""

from .dsl import *
from .interpreter import *
from constants import (
    PERSON, VEHICLE, TEXT,
    TERM_NUM
)
from .config import Configuration


class Hole:
    def __init__(self, depth, node_type, output_over=None, output_under=None, val=None):
        self.depth = depth
        self.node_type = node_type
        self.output_over = output_over
        self.output_under = output_under
        self.val = None

    def __str__(self):
        return self.__class__.__name__

    def duplicate(self):
        return Hole(
            self.depth, self.node_type, self.output_over, self.output_under, self.val
        )

    def __lt__(self, other):
        if not isinstance(other, Hole):
            return False
        return str(self) < str(other)


def get_output_objs(env, action):
    # get positive samples
    objs = set()
    for obj_id, details_map in env.items():
        if "ActionApplied" in details_map and details_map["ActionApplied"] == action:
            objs.add(obj_id)
    return ",".join(sorted(objs))


# ========================================================= #
#                     Expand program's holes
# ========================================================= #

# def get_dynamic_f

def get_attributes(output_over, output_under, config: Configuration):
    # func, args, I-, I+, node size
    if config.CLASS == VEHICLE:
        extensions = [
            (GetColor(None), ["Color"], [output_over], [output_under], 1),
            (GetType(None), ["Type"], [output_over], [output_under], 1),
        ]
    elif config.CLASS == PERSON:
        extensions = [
            (IsMale(), [], [], [], 0),
            (IsAgeLess(None), ["Age"], [output_over], [output_under], 1),
            (IsAgeEq(None), ["Age"], [output_over], [output_under], 1),
            (IsAgeGreater(None), ["Age"], [output_over], [output_under], 1),
            (GetOrientation(None), ["Orientation"], [output_over], [output_under], 1),
            (IsGlasses(), [], [], [], 0),
            (IsHat(), [], [], [], 0),
            (IsHoldObjectsInFront(), [], [], [], 0),
            (GetBag(None), ["Bag"], [output_over], [output_under], 1),
            (GetTopStyle(None), ["TopStyle"], [output_over], [output_under], 1),
            (GetBottomStyle(None), ["BottomStyle"], [output_over], [output_under], 1),
            (IsShortSleeve(), [], [], [], 0),
            (IsLongSleeve(), [], [], [], 0),
            (IsLongCoat(), [], [], [], 0),
            (IsTrousers(), [], [], [], 0),
            (IsShorts(), [], [], [], 0),
            (IsSkirtDress(), [], [], [], 0),
            (IsBoots(), [], [], [], 0),
        ]
    elif config.CLASS == TEXT:
        extensions = [
            (IsEmpty(), [], [], [], 0),
            (IsPureNumber(), [], [], [], 0),
            (IsPureAlphabet(), [], [], [], 0),
            (IsLengthLess(None), ["Length"], [output_over], [output_under], 1),
            (IsLengthEq(None), ["Length"], [output_over], [output_under], 1),
            (IsLengthGreater(None), ["Length"], [output_over], [output_under], 1),
        ]
        if config.parameters is not None:
            for genre, attrs in config.parameters.items():
                for attr, values in attrs.items():
                    if attr == "In":
                        func = IsIn
                    elif attr == "StartsWith":
                        func = IsStartsWith
                    elif attr == "EndsWith":
                        func = IsEndsWith
                    elif attr == "Regex":
                        func = IsRegexMatch
                    else:
                        raise NotImplementedError
                    extensions += [(func(v), [], [], [], 0) for v in values]
    else:
        raise NotImplementedError

    return extensions


def get_extractors(
        parent_extr: Extractor, output_over, output_under, env, config: Configuration
) -> List:
    # expand holes
    # compute approximations (I+/I-) for program tree nodes
    # output_over: I+, output_under: I-
    extrs = get_attributes(output_over, output_under, config)  # basic production
    # extrs=[]
    extrs += (
        (  # complement
            Not(None),
            ["extr"],
            [set(env.keys()) - output_under],
            [set(env.keys()) - output_over],
            1,
        ),  # (I\I-, I\I+)
    )
    # Or[Or] <=> Or[], And[And] <=> And[]
    if not isinstance(parent_extr, Or):  # union
        for i in range(2, TERM_NUM):
            extrs.append(
                (Or([None] * i), ["extr"] * i, [output_over] * i, [set()] * i, i)  # (I+, {})
            ),
    if not isinstance(parent_extr, And):  # intersection
        for i in range(2, TERM_NUM):
            extrs.append(
                (
                    And([None] * i),
                    ["extr"] * i,
                    [set(env.keys())] * i,
                    [output_under] * i,
                    i,
                )
            ),  # (I, I-)
    return extrs


def construct_prog_from_tree(tree, node_num=0, config: Configuration = None):
    # cursively transform tree into program
    prog = tree.nodes[node_num]

    if not isinstance(prog, Node):  # not hole
        return prog

    prog_dict = vars(prog)
    # get children
    if node_num in tree.to_children:
        child_nums = tree.to_children[node_num]
    else:
        child_nums = []
    child_types = [
        item for item in list(prog_dict)
        if item not in {"val", "output_over", "output_under"} and item not in config.TERMINALS
    ]
    if child_types and child_types[0] == "extractors":
        # tree: Or[None] -> [Hole, Hole]
        # program: Or[Hole, Hole]
        for child_num in child_nums:
            prog_dict["extractors"].pop(0)
            child_prog = construct_prog_from_tree(tree, child_num, config)
            prog_dict["extractors"].append(child_prog)
        return prog
    # assert len(child_nums) == len(child_types)
    for child_type, child_num in zip(child_types, child_nums):
        child_prog = construct_prog_from_tree(tree, child_num, config)
        prog_dict[child_type] = child_prog
    return prog


def get_type(prog, config: Configuration):
    # get type of program

    # Hole -> Person/Vehicle/Text
    if not isinstance(prog, Node):
        return {PERSON, VEHICLE, TEXT}

    # Or/And/Not
    if isinstance(prog, Or):  # = or
        res = set()
        for sub_extr in prog.extractors:
            sub_extr_type = get_type(sub_extr, config=config)
            if not sub_extr_type:
                return sub_extr_type
            res = res.union(get_type(sub_extr, config=config))
        return res
    elif isinstance(prog, And):  # = and
        res = {PERSON, VEHICLE, TEXT}
        for sub_extr in prog.extractors:
            res = res.intersection(get_type(sub_extr, config))
        return res
    elif isinstance(prog, Not):  # = not
        return get_type(prog.extractor, config=config)

    # Person/Vehicle/Text related functions
    elif isinstance(prog, (IsVehicle, GetColor, GetType)):
        return {VEHICLE}
    elif isinstance(prog, (IsPerson, IsMale, IsAgeLess, IsAgeEq, IsAgeGreater, GetOrientation, IsGlasses, IsHat, \
                           IsHoldObjectsInFront, GetBag, GetTopStyle, GetBottomStyle, IsShortSleeve, IsLongSleeve, \
                           IsLongCoat, IsTrousers, IsShorts, IsSkirtDress, IsBoots)):
        return {PERSON}
    elif isinstance(prog, (IsEmpty, IsPureNumber, IsPureAlphabet, IsLengthLess, IsLengthEq, IsLengthGreater, \
                           IsStartsWith, IsEndsWith, IsIn, IsRegexMatch)):
        return {TEXT}
    else:
        raise NotImplementedError(f'Unknown output type of {prog}.')


def get_prog_output(prog, env, parent, eval_cache=None, config: Configuration = None):
    # return program output
    # partial program
    if (
            isinstance(prog, Or)
            or isinstance(prog, And)
            or isinstance(prog, Not)
            or isinstance(prog, (GetColor, GetType, IsAgeLess, IsAgeEq, IsAgeGreater, GetOrientation, GetBag, \
                                 GetTopStyle, GetBottomStyle, IsLengthLess, IsLengthEq, IsLengthGreater,))
            # add functions that have many arguments as they cannot be evaluated because of holes
    ):
        return None
    # parent that have many arguments
    if isinstance(parent, (GetColor, GetType, IsAgeLess, IsAgeEq, IsAgeGreater, GetOrientation, GetBag, GetTopStyle, \
                           GetBottomStyle, IsLengthLess, IsLengthEq, IsLengthGreater,)):
        prog = parent.__class__(prog)
    return eval_extractor(prog, env, eval_cache=eval_cache, config=config)


def invalid_output(output_over, output_under, prog_output):
    # I- <= output <= I+
    return not (output_under.issubset(prog_output) and prog_output.issubset(output_over))


def simplify(prog, env_size, output_dict):
    # rewrite program

    # (1) simplify terms of Or/And/Not
    if isinstance(prog, Or) or isinstance(prog, And):
        prog.extractors = [simplify(sub_extr, env_size, output_dict) for sub_extr in prog.extractors]
        if None in prog.extractors:
            return None
    elif isinstance(prog, Not):
        prog.extractor = simplify(prog.extractor, env_size, output_dict)
        if prog.extractor is None:
            return None

    # (2) simplify Or/And/Not
    while True:
        changed = True
        if isinstance(prog, Or):
            if len(prog.extractors) == 1:
                # Or[E] <=> E
                new_prog = prog.extractors[0]
            else:
                new_sub_extrs = []
                for i, sub_extr in enumerate(prog.extractors):
                    val = output_dict[sub_extr.val] if sub_extr.val is not None else None
                    # Identity
                    if val is not None and len(val) == 0:
                        continue
                    if (
                            isinstance(sub_extr, Or)
                            or isinstance(sub_extr, And)
                            and not sub_extr.extractors
                    ):
                        continue
                    # Domination
                    if val is not None and len(val) == env_size:
                        new_sub_extrs = [sub_extr]
                        break
                    should_keep = True
                    for j, other_sub_extr in enumerate(prog.extractors):
                        # Idempotency
                        if sub_extr == other_sub_extr and i < j:
                            should_keep = False
                            break
                        if (
                                val is not None
                                and other_sub_extr.val is not None
                                and val.issubset(output_dict[other_sub_extr.val])
                                and i != j
                        ):
                            should_keep = False
                            break
                        # Absorption
                        if (
                                isinstance(sub_extr, And)
                                and other_sub_extr in sub_extr.extractors
                        ):
                            should_keep = False
                            break
                    if should_keep:
                        new_sub_extrs.append(sub_extr)
                new_sub_extrs.sort()
                if new_sub_extrs == prog.extractors:
                    changed = False
                if len(new_sub_extrs) < 2:
                    return None
                new_prog = Or(new_sub_extrs)

        elif isinstance(prog, And):
            if len(prog.extractors) == 1:
                new_prog = prog.extractors[0]
            else:
                new_sub_extrs = []
                for i, sub_extr in enumerate(prog.extractors):
                    val = (
                        output_dict[sub_extr.val] if sub_extr.val is not None else None
                    )
                    should_keep = True
                    # Identity
                    if val is not None and len(val) == env_size:
                        continue
                    if (
                            isinstance(sub_extr, Or)
                            or isinstance(sub_extr, And)
                            and not sub_extr.extractors
                    ):
                        continue
                    # Domination
                    if val is not None and len(val) == 0:
                        new_sub_extrs = [sub_extr]
                        break
                    for j, other_sub_extr in enumerate(prog.extractors):
                        # Idempotency
                        if sub_extr == other_sub_extr and i < j:
                            should_keep = False
                            break
                        if (
                                val is not None
                                and other_sub_extr.val is not None
                                and output_dict[other_sub_extr.val].issubset(val)
                                and i != j
                        ):
                            should_keep = False
                            break
                        # Absorption
                        if (
                                isinstance(sub_extr, Or)
                                and other_sub_extr in sub_extr.extractors
                        ):
                            should_keep = False
                            break
                    if should_keep:
                        new_sub_extrs.append(sub_extr)
                new_sub_extrs.sort()
                if new_sub_extrs == prog.extractors:
                    changed = False
                if len(new_sub_extrs) < 2:
                    return None
                new_prog = And(new_sub_extrs)
        # Double negation
        elif isinstance(prog, Not) and isinstance(prog.extractor, Not):
            return None
            # new_prog = prog.extractor.extractor
        elif isinstance(prog, Not) and isinstance(prog.extractor, And):
            new_sub_extrs = [
                Not(sub_extr) for sub_extr in prog.extractor.extractors
            ]
            new_prog = Or(new_sub_extrs)
        elif isinstance(prog, Not) and isinstance(prog.extractor, Or):
            new_sub_extrs = [
                Not(sub_extr) for sub_extr in prog.extractor.extractors
            ]
            new_prog = And(new_sub_extrs)
        else:
            new_prog = prog
            changed = False

        if not changed:
            break
        prog = new_prog
    return prog


def get_valid_colors(env, output_under, output_over):
    # output_over is a subset of output_under
    req_colors = set(env[obj_id]["Color"] for obj_id in output_under if "Color" in env[obj_id])
    if len(req_colors) == 1:
        return req_colors
    if len(req_colors) > 1:
        return []
    return set(env[obj_id]["Color"] for obj_id in output_over if "Color" in env[obj_id])


def get_valid_types(env, output_under, output_over):
    # output_over is a subset of output_under
    req_types = set(env[obj_id]["Type"] for obj_id in output_under if "Type" in env[obj_id])
    if len(req_types) == 1:
        return req_types
    if len(req_types) > 1:
        return []
    return set(env[obj_id]["Type"] for obj_id in output_over if "Type" in env[obj_id])


def get_valid_ages(env, output_under, output_over):
    # output_over is a subset of output_under
    req_ages = set(env[obj_id]["Age"] for obj_id in output_under if "Age" in env[obj_id])
    if len(req_ages) == 1:
        return req_ages
    if len(req_ages) > 1:
        return []
    return sorted(set(env[obj_id]["Age"] for obj_id in output_over if "Age" in env[obj_id]))


def get_valid_orientations(env, output_under, output_over):
    # output_over is a subset of output_under
    req_orientations = set(env[obj_id]["Orientation"] for obj_id in output_under if "Orientation" in env[obj_id])
    if len(req_orientations) == 1:
        return req_orientations
    if len(req_orientations) > 1:
        return []
    return set(env[obj_id]["Orientation"] for obj_id in output_over if "Orientation" in env[obj_id])


def get_valid_bags(env, output_under, output_over):
    # output_over is a subset of output_under
    req_bags = set(env[obj_id]["Bag"] for obj_id in output_under if "Bag" in env[obj_id])
    if len(req_bags) == 1:
        return req_bags
    if len(req_bags) > 1:
        return []
    return set(env[obj_id]["Bag"] for obj_id in output_over if "Bag" in env[obj_id])


def get_valid_topstyles(env, output_under, output_over):
    # output_over is a subset of output_under
    req_topstyles = set(env[obj_id]["TopStyle"] for obj_id in output_under if "TopStyle" in env[obj_id])
    if len(req_topstyles) == 1:
        return req_topstyles
    if len(req_topstyles) > 1:
        return []
    return set(env[obj_id]["TopStyle"] for obj_id in output_over if "TopStyle" in env[obj_id])


def get_valid_bottomstyles(env, output_under, output_over):
    # output_over is a subset of output_under
    req_bottomstyles = set(env[obj_id]["BottomStyle"] for obj_id in output_under if "BottomStyle" in env[obj_id])
    if len(req_bottomstyles) == 1:
        return req_bottomstyles
    if len(req_bottomstyles) > 1:
        return []
    return set(env[obj_id]["BottomStyle"] for obj_id in output_over if "BottomStyle" in env[obj_id])


def get_valid_lengths(env, output_under, output_over):
    # output_over is a subset of output_under
    req_lengths = set(len(env[obj_id]["Context"]) for obj_id in output_under if "Context" in env[obj_id])
    if len(req_lengths) == 1:
        return req_lengths
    if len(req_lengths) > 1:
        return []
    return sorted(set(len(env[obj_id]["Context"]) for obj_id in output_over if "Context" in env[obj_id]))
