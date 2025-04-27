# -*- coding:utf-8 -*-

import re
from .dsl import *
from typing import Dict, Any
from constants import (
    PERSON, VEHICLE, TEXT,
)
from .config import Configuration
import operator


def update_output_approx(prog, output_under, output_over, env, output_dict):
    if (
            isinstance(prog, str)
            or isinstance(prog, int)
            or output_under == prog.output_under
            and output_over == prog.output_over
    ):
        return
    over_str = str(output_over)
    under_str = str(output_under)
    if over_str not in output_dict:
        output_dict[over_str] = output_over
    if under_str not in output_dict:
        output_dict[under_str] = output_under
    prog.output_under = under_str
    prog.output_over = over_str
    if isinstance(prog, Or):
        for sub_extr in prog.extractors:
            update_output_approx(sub_extr, set(), output_over, env, output_dict)
    elif isinstance(prog, And):
        for sub_extr in prog.extractors:
            update_output_approx(
                sub_extr, output_under, set(env.keys()), env, output_dict
            )
    elif isinstance(prog, Not):
        update_output_approx(
            prog.extractor,
            set(env.keys()) - output_over,
            set(env.keys() - output_under),
            env,
            output_dict,
        )


def partial_eval(extractor, env, output_dict, eval_cache, config: Configuration):
    # hole
    if not isinstance(extractor, Extractor):
        return False

    if extractor.val is not None:
        return False

    if str(extractor) in eval_cache:
        val = eval_cache[str(extractor)]
        extractor.val = str(val)
        if len(val) == 0:
            return True
        return False

    persons = {obj for obj in env.keys() if env[obj]["cls"] == PERSON}
    vehicles = {obj for obj in env.keys() if env[obj]["cls"] == VEHICLE}
    texts = {obj for obj in env.keys() if env[obj]["cls"] == TEXT}

    val = None
    # vehicle
    if isinstance(extractor, IsVehicle):
        val = vehicles
    elif isinstance(extractor, GetColor):
        val = set()
        if not vehicles:
            val = set()
        elif not isinstance(extractor.color, str):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != VEHICLE:
                continue
            if details["Color"] == extractor.color:
                val.add(obj_id)
    elif isinstance(extractor, GetType):
        val = set()
        if not vehicles:
            val = set()
        elif not isinstance(extractor.type, str):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != VEHICLE:
                continue
            if details["Type"] == extractor.type:
                val.add(obj_id)
    # person
    elif isinstance(extractor, IsPerson):
        val = persons
    elif isinstance(extractor, (IsMale, IsGlasses, IsHat, IsHoldObjectsInFront, IsShortSleeve, IsLongSleeve, \
                                IsLongCoat, IsTrousers, IsShorts, IsSkirtDress, IsBoots)):
        val = {obj for obj in env if env[obj].get(str(extractor)[2:], False)}
    elif isinstance(extractor, (IsAgeLess, IsAgeEq, IsAgeGreater)):
        if isinstance(extractor, IsAgeLess):
            age_eval_func = operator.lt
        elif isinstance(extractor, IsAgeEq):
            age_eval_func = operator.eq
        else:
            age_eval_func = operator.gt
        val = set()
        if not persons:
            val = set()
        elif not isinstance(extractor.age, int):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != PERSON:
                continue
            if age_eval_func(details["Age"], extractor.age):
                val.add(obj_id)
    elif isinstance(extractor, GetOrientation):
        val = set()
        if not PERSON:
            val = set()
        elif not isinstance(extractor.orientation, str):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != PERSON:
                continue
            if details["Orientation"] == extractor.orientation:
                val.add(obj_id)
    elif isinstance(extractor, GetBag):
        val = set()
        if not PERSON:
            val = set()
        elif not isinstance(extractor.bag, str):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != PERSON:
                continue
            if details["Bag"] == extractor.bag:
                val.add(obj_id)
    elif isinstance(extractor, GetTopStyle):
        val = set()
        if not PERSON:
            val = set()
        elif not isinstance(extractor.topstyle, str):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != PERSON:
                continue
            if details["TopStyle"] == extractor.topstyle:
                val.add(obj_id)
    elif isinstance(extractor, GetBottomStyle):
        val = set()
        if not PERSON:
            val = set()
        elif not isinstance(extractor.bottomstyle, str):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != PERSON:
                continue
            if details["BottomStyle"] == extractor.bottomstyle:
                val.add(obj_id)
    # text
    elif isinstance(extractor, IsText):
        val = texts
    elif isinstance(extractor, (IsEmpty, IsPureNumber, IsPureAlphabet, IsStartsWith, IsEndsWith, IsIn, IsRegexMatch)):
        val = {obj for obj in env if env[obj].get(str(extractor)[2:], False)}
    elif isinstance(extractor, (IsLengthLess, IsLengthEq, IsLengthGreater)):
        if isinstance(extractor, IsLengthLess):
            age_eval_func = operator.lt
        elif isinstance(extractor, IsLengthEq):
            age_eval_func = operator.eq
        else:
            age_eval_func = operator.gt
        val = set()
        if not texts:
            val = set()
        elif not isinstance(extractor.length, int):
            return False
        for (obj_id, details) in env.items():
            if details["cls"] != TEXT:
                continue
            if age_eval_func(len(details["Context"]), extractor.length):
                val.add(obj_id)
    # Or/And/Not
    elif isinstance(extractor, Or):
        should_prune = False
        for sub_extr in extractor.extractors:
            should_prune = partial_eval(sub_extr, env, output_dict, eval_cache, config) or should_prune
        vals = []
        none_vals = []
        val_total = set()
        for i, sub_extr in enumerate(extractor.extractors):
            if sub_extr.val is None:
                none_vals.append(i)
            else:
                vals.append(output_dict[sub_extr.val])
                val_total.update(output_dict[sub_extr.val])
        if len(none_vals) == 1 and extractor.output_over == extractor.output_under:
            # if Or[A, B, Hole](I+, I-), then Hole's approximation = (I+, I- \ {A.I-, B.I-})
            sub_extr = extractor.extractors[none_vals[0]]
            output_over = output_dict[sub_extr.output_over]
            new_output_under = output_over - val_total
            update_output_approx(
                sub_extr, new_output_under, output_over, env, output_dict
            )
        if vals and not none_vals:
            val = set.union(*vals)
        elif set(env.keys()) in vals:
            val = set(env.keys())
        if should_prune:
            return True
    elif isinstance(extractor, And):
        should_prune = False
        for sub_extr in extractor.extractors:
            should_prune = (
                    partial_eval(sub_extr, env, output_dict, eval_cache, config) or should_prune
            )
        vals = []
        none_vals = []
        val_total = set()
        for i, sub_extr in enumerate(extractor.extractors):
            if sub_extr.val is None:
                none_vals.append(i)
            else:
                vals.append(output_dict[sub_extr.val])
                val_total = val_total.intersection(output_dict[sub_extr.val])
        if len(none_vals) == 1 and extractor.output_over == extractor.output_under:
            # if And[A, B, Hole](I+, I-), then Hole's approximation = (I+ \ {}, I-)
            sub_extr = extractor.extractors[none_vals[0]]
            output_under = output_dict[sub_extr.output_under]
            new_output_over = set(env.keys()) - (val_total - output_under)
            update_output_approx(
                sub_extr, output_under, new_output_over, env, output_dict
            )
        if vals and not none_vals:
            val = set.intersection(*vals)
        elif set() in vals:
            val = set()
        if should_prune:
            return True
    elif isinstance(extractor, Not):
        if partial_eval(extractor.extractor, env, output_dict, eval_cache, config):
            return True
        if extractor.extractor.val is not None:
            val = set(env.keys()) - output_dict[extractor.extractor.val]

    if val is not None:
        extractor.val = str(val)
        eval_cache[str(extractor)] = val
        if str(val) not in output_dict:
            output_dict[str(val)] = val
        if len(val) == 0:
            return True
    return False


def eval_extractor(
        extractor: Extractor,
        details: Dict[str, Dict[str, Any]],
        rec: bool = True,
        output_dict={},
        eval_cache=None,
        config: Configuration = None,
):  # -> Set[dict[str, str]]:
    # return output of new program

    if output_dict and extractor.val is not None:
        return output_dict[extractor.val]

    # cache
    if eval_cache and str(extractor) in eval_cache:
        return eval_cache[str(extractor)]

    # ========================================================= #
    # Do not need `IsCls` function as we classify input-output at first
    # ========================================================= #
    # elif isinstance(extractor, IsVehicle):
    #     res = {obj for obj in details.keys() if details[obj]["cls"] == VEHICLE}
    # elif isinstance(extractor, IsPerson):
    #     res = {obj for obj in details.keys() if details[obj]["cls"] == PERSON}
    # elif isinstance(extractor, IsText):
    #     res = {obj for obj in details.keys() if details[obj]["cls"] == TEXT}

    # ========================================================= #
    # we do not have function that has argument, instead all functions are predicates
    # ========================================================= #
    # vehicle
    if config.CLASS == VEHICLE:
        if isinstance(extractor, GetColor):
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != VEHICLE:
                    continue
                if obj_details["Color"] == extractor.color:
                    objs.add(obj_id)
            res = objs
        elif isinstance(extractor, GetType):
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != VEHICLE:
                    continue
                if obj_details["Type"] == extractor.type:
                    objs.add(obj_id)
            res = objs
    # person
    elif config.CLASS == PERSON:
        if isinstance(extractor, (IsMale, IsGlasses, IsHat, IsHoldObjectsInFront, IsShortSleeve, IsLongSleeve, \
                                  IsLongCoat, IsTrousers, IsShorts, IsSkirtDress, IsBoots,)):
            res = {obj for obj in details if details[obj].get(str(extractor)[2:], False)}
        elif isinstance(extractor, (IsAgeLess, IsAgeEq, IsAgeGreater)):
            if isinstance(extractor, IsAgeLess):
                age_eval_func = operator.lt
            elif isinstance(extractor, IsAgeEq):
                age_eval_func = operator.eq
            else:
                age_eval_func = operator.gt
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != PERSON:
                    continue
                if age_eval_func(obj_details["Age"], extractor.age):
                    objs.add(obj_id)
            res = objs
        elif isinstance(extractor, GetOrientation):
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != PERSON:
                    continue
                if obj_details["Orientation"] == extractor.orientation:
                    objs.add(obj_id)
            res = objs
        elif isinstance(extractor, GetBag):
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != PERSON:
                    continue
                if obj_details["Bag"] == extractor.bag:
                    objs.add(obj_id)
            res = objs
        elif isinstance(extractor, GetTopStyle):
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != PERSON:
                    continue
                if obj_details["TopStyle"] == extractor.topstyle:
                    objs.add(obj_id)
            res = objs
        elif isinstance(extractor, GetBottomStyle):
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != PERSON:
                    continue
                if obj_details["BottomStyle"] == extractor.bottomstyle:
                    objs.add(obj_id)
            res = objs
    # text
    elif config.CLASS == TEXT:
        if isinstance(extractor, (IsEmpty, IsPureNumber, IsPureAlphabet)):
            res = {obj for obj in details if details[obj].get(str(extractor)[2:], False)}
        elif isinstance(extractor, (IsLengthLess, IsLengthEq, IsLengthGreater)):
            if isinstance(extractor, IsLengthLess):
                age_eval_func = operator.lt
            elif isinstance(extractor, IsLengthEq):
                age_eval_func = operator.eq
            else:
                age_eval_func = operator.gt
            objs = set()
            for (obj_id, obj_details) in details.items():
                if obj_details["cls"] != TEXT:
                    continue
                if age_eval_func(len(obj_details["Context"]), extractor.length):
                    objs.add(obj_id)
            res = objs
        elif isinstance(extractor, IsStartsWith):
            res = {obj for obj in details if str.startswith(details[obj]["Context"], extractor.substr)}
        elif isinstance(extractor, IsEndsWith):
            res = {obj for obj in details if str.endswith(details[obj]["Context"], extractor.substr)}
        elif isinstance(extractor, IsIn):
            res = {obj for obj in details if extractor.substr in details[obj]["Context"]}
        elif isinstance(extractor, IsRegexMatch):
            res = {obj for obj in details if re.search(extractor.substr, details[obj]["Context"]) is not None}


    # Or/And/Not
    elif isinstance(extractor, Or):
        if rec:
            res = set()
            for sub_extr in extractor.extractors:
                res = res.union(
                    eval_extractor(sub_extr, details, rec, output_dict, eval_cache, config)
                )
            res = res
        else:
            res = set()
            for sub_extr in extractor.extractors:
                res = res.union(sub_extr.objs)
            res = res
    elif isinstance(extractor, And):
        if rec:
            res = set(details.keys())
            for sub_extr in extractor.extractors:
                res = res.intersection(
                    eval_extractor(sub_extr, details, rec, output_dict, eval_cache, config)
                )
        else:
            res = set()
            for sub_extr in extractor.extractors:
                res = res.intersection(sub_extr.objs)
    elif isinstance(extractor, Not):
        # All objs in target image except those extracted
        if rec:
            extracted_objs = eval_extractor(
                extractor.extractor, details, rec, output_dict, eval_cache, config
            )
            res = details.keys() - extracted_objs
        else:
            res = details.keys() - set(extractor.extractor.objs)
    elif any(isinstance(extractor, func) for func in config.get_all_codomain()):
        res = {obj for obj in details if details[obj].get(extractor.key, None) == extractor.value}
    else:
        # print(extractor)
        raise Exception(extractor)
    # update cache
    if eval_cache is not None:
        eval_cache[str(extractor)] = res
    return res
