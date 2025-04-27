# -*- coding:utf-8 -*-

"""
Program adapted from https://github.com/celestebarnaby/ImageEye.
Thank Celeste Barnaby's opensource codes!
"""

import itertools
import os
from typing import Dict, List
import heapq as hq
from baselines.ImageEye.interpreter import *
from baselines.ImageEye.dsl import *
from baselines.ImageEye.utils import *


class Tree:
    def __init__(self, _id: int):
        self.id: int = _id
        self.nodes: Dict[int, Extractor] = {}
        self.to_children: Dict[int, List[int]] = {}
        self.to_parent: Dict[int, int] = {}
        self.node_id_counter = itertools.count(0)
        self.depth = 1
        self.size = 1
        self.var_nodes = []  # hole node indices

    def duplicate(self, _id: int) -> "Tree":
        ret = Tree(_id)
        # ret.nodes = copy.copy(self.nodes)
        ret.nodes = {}
        for key, val in self.nodes.items():
            if isinstance(val, Hole) or isinstance(val, Node):
                ret.nodes[key] = val.duplicate()
            else:
                ret.nodes[key] = val
        ret.to_children = self.to_children.copy()
        ret.to_parent = self.to_parent.copy()
        ret.node_id_counter = itertools.tee(self.node_id_counter)[1]
        ret.var_nodes = self.var_nodes.copy()
        ret.depth = self.depth
        ret.size = self.size
        return ret

    def __lt__(self, other):
        if self.size == other.size and self.depth == other.depth:
            return self.id < other.id
        if self.size == other.size:
            return self.depth < other.depth
        return self.size < other.size

    def __repr__(self):
        return str(self.nodes)

    def __str__(self):
        return self.__repr__()


class Synthesizer:
    def __init__(self, max_synth_depth: int = 5):
        self.max_synth_depth = max_synth_depth
        self.program_counter = itertools.count(0)

    def synthesize_top_down(self, env, eval_cache, output_over, output_under, output_refuted, config):
        # instead of output, we need output_under, output_over
        output_dict = {str(output_over): output_over,
                       str(output_under): output_under,
                       str(output_refuted): output_refuted}  # output samples
        seen_progs = set()

        tree = Tree(next(self.program_counter))
        tree.nodes[0] = Hole(0, "extr", str(output_over), str(output_under))  # Set I+/I- for hole
        tree.var_nodes.append(0)  # extensible (i.e., has Holes) node indices
        worklist = []
        hq.heappush(worklist, tree)
        num_progs = 0

        while worklist:
            num_progs += 1
            cur_tree = hq.heappop(worklist)

            # transform tree into program
            # print(cur_tree)
            prog = construct_prog_from_tree(cur_tree, config=config)
            if not get_type(prog, config):  # type checking for program
                continue

            # EQUIVALENCE REDUCTION
            # partially evaluate program (i.e., execute partial programs) and save their results in `eval_cache`
            should_prune = partial_eval(prog, env, output_dict, eval_cache, config)  # !!!!!!!!!!!!!!
            if should_prune:
                continue

            # simplify program with rewrite rules
            if not isinstance(prog, Hole):
                simplified_prog = simplify(prog.duplicate(), len(env), output_dict)
                if simplified_prog is None or str(simplified_prog) in seen_progs:
                    continue
                seen_progs.add(str(simplified_prog))

            # concrete program, i.e., no hole
            if not cur_tree.var_nodes:
                # !!!!!!!!!!!!!!
                extracted_objs = eval_extractor(prog, env, output_dict=output_dict, eval_cache=eval_cache)
                # check whether its a valid program
                if output_over.issubset(extracted_objs) and len(extracted_objs & output_refuted) == 0:
                    # print("Num progs: ", num_progs)
                    # print("Size:", cur_tree.size)
                    return prog, num_progs
                continue

            # program has holes, therefore synthesizing
            hole_num = cur_tree.var_nodes.pop(0)
            hole = cur_tree.nodes[hole_num]
            if hole.depth > self.max_synth_depth:
                continue
            node_type = cur_tree.nodes[hole_num].node_type
            parent_node = None if hole_num == 0 else cur_tree.nodes[cur_tree.to_parent[hole_num]]
            # !!!!!!!!!!!!!!
            if node_type == "extr":
                new_sub_extrs = get_extractors(
                    parent_node, output_dict[hole.output_over], output_dict[hole.output_under], env,
                    config,
                )
            elif node_type == "Color":
                new_sub_extrs = [
                    (color, [], [], [], 0)
                    for color in get_valid_colors(env, output_dict[hole.output_under], output_dict[hole.output_over])
                ]
            elif node_type == "Type":
                new_sub_extrs = [
                    (type, [], [], [], 0)
                    for type in get_valid_types(env, output_dict[hole.output_under], output_dict[hole.output_over])
                ]
            elif node_type == "Age":
                new_sub_extrs = [
                    (age, [], [], [], 0)
                    for age in get_valid_ages(env, output_dict[hole.output_under], output_dict[hole.output_over])
                ]
            elif node_type == "Orientation":
                new_sub_extrs = [
                    (orientation, [], [], [], 0)
                    for orientation in get_valid_orientations(env, output_dict[hole.output_under],
                                                              output_dict[hole.output_over])
                ]
            elif node_type == "Bag":
                new_sub_extrs = [
                    (bag, [], [], [], 0)
                    for bag in get_valid_bags(env, output_dict[hole.output_under], output_dict[hole.output_over])
                ]
            elif node_type == "TopStyle":
                new_sub_extrs = [
                    (topstyle, [], [], [], 0)
                    for topstyle in get_valid_topstyles(env, output_dict[hole.output_under],
                                                        output_dict[hole.output_over])
                ]
            elif node_type == "BottomStyle":
                new_sub_extrs = [
                    (bottomstyle, [], [], [], 0)
                    for bottomstyle in get_valid_bottomstyles(env, output_dict[hole.output_under],
                                                              output_dict[hole.output_over])
                ]
            elif node_type == "Length":
                new_sub_extrs = [
                    (length, [], [], [], 0)
                    for length in get_valid_lengths(env, output_dict[hole.output_under], output_dict[hole.output_over])
                ]
            else:
                raise NotImplemented(node_type)

            # new_sub_extrs
            for sub_extr, children, child_outputs_over, child_outputs_under, size in new_sub_extrs:
                # update synthesized program's (I+, I-)
                if isinstance(sub_extr, Node):
                    sub_extr.output_over = str(hole.output_over)
                    sub_extr.output_under = str(hole.output_under)

                # print(sub_extr)
                prog_output = get_prog_output(sub_extr, env, parent_node, config=config)
                # print(prog_output)
                # OUTPUT ESTIMATION-BASED PRUNING
                # (1) if prog_output is None, do extension
                # (2) if prog_output is an empty set, continue
                # (3) if prog_output is not empty, check validity
                if prog_output is not None and len(prog_output) == 0:
                    continue
                if prog_output and \
                        invalid_output(output_dict[hole.output_over], output_dict[hole.output_under], prog_output):
                    continue
                new_tree = cur_tree.duplicate(next(self.program_counter))
                new_tree.nodes[hole_num] = sub_extr
                new_tree.size += size

                for child, child_output_over, child_output_under in \
                        zip(children, child_outputs_over, child_outputs_under):
                    # programs that have many arguments
                    over_str = str(child_output_over)
                    under_str = str(child_output_under)
                    if over_str not in output_dict:
                        output_dict[over_str] = child_output_over
                    if under_str not in output_dict:
                        output_dict[under_str] = child_output_under
                    new_hole = Hole(hole.depth + 1, child, over_str, under_str)
                    new_tree.depth = max(new_tree.depth, new_hole.depth)
                    new_node_num = len(new_tree.nodes)
                    new_tree.nodes[new_node_num] = new_hole
                    new_tree.var_nodes.append(new_node_num)
                    new_tree.to_parent[new_node_num] = hole_num
                    if hole_num in new_tree.to_children:
                        new_tree.to_children[hole_num].append(new_node_num)
                    else:
                        new_tree.to_children[hole_num] = [new_node_num]
                hq.heappush(worklist, new_tree)
