# -*- coding:utf-8 -*-

import argparse
import os
import json
import csv
from collections import defaultdict
import itertools
import re
from constants import (
    DATASET_DIR, TIMEOUT,
    PERSON, TEXT, VEHICLE, MIX, CODOMAINS, CLS2IDS, PROJECT_DIR
)
from lark_parser import Parser
from prettytable import PrettyTable
import numpy as np

DIR = os.path.dirname(__file__)

parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str, default="benchmarks", choices=["benchmarks", "history"])
args = parser.parse_args()

OUT_DIR = os.path.join(PROJECT_DIR, {
    "benchmarks": "rqs",
    "history": "history",
}[args.directory])

parser = Parser()
# why `+ 1e-10`? because in Python round(0.95)=0.9 and round(4.45)=4.5
mean = lambda xs: round(sum(xs) / len(xs) + 1e-10, 1) if len(xs) > 0 else 0
count_time = lambda xs: sum(x for x in xs if x is not None) if isinstance(xs, list) else xs
stats_func = lambda xs: [round(min(xs), 1), round(np.median(xs), 1), round(mean(xs), 1), round(max(xs), 1)]

eusolver_file = os.path.join(PROJECT_DIR, args.directory, "results.eusolver")
imageeye_file = os.path.join(PROJECT_DIR, args.directory, "results.imageeye")
manirender_wo_abst_diff_file = os.path.join(PROJECT_DIR, args.directory, "results.manirender")
manirender_wo_diff_file = os.path.join(PROJECT_DIR, args.directory, "results.abst.manirender")
manirender_wo_abst_file = os.path.join(PROJECT_DIR, args.directory, "results.diff.manirender")
manirender_file = os.path.join(PROJECT_DIR, args.directory, "results.diff-abst.manirender")
chatgpt4o_file = os.path.join(PROJECT_DIR, args.directory, "results.gpt4o")
scalability_attr_file = os.path.join(PROJECT_DIR, args.directory, "scalability.attr")
scalability_range_file = os.path.join(PROJECT_DIR, args.directory, "scalability.range")


def beautify_lattice_size(lattice_size):
    # old format
    # if lattice_size >= 1e9:
    #     lattice_size = round(lattice_size / 1e9 + 1e-10)
    #     lattice_size = f"{lattice_size}b"
    # elif lattice_size >= 1e6:
    #     lattice_size = round(lattice_size / 1e6 + 1e-10)
    #     lattice_size = f"{lattice_size}m"
    # else:
    #     lattice_size = round(lattice_size + 1e-10)
    #     lattice_size = str(lattice_size)
    # return lattice_size

    # new format
    return f"{lattice_size:.1e}"


def count_ast(ast, action):
    def _f(ast):
        if isinstance(ast, dict):
            return 1 + sum(_f(node) for node in ast.values())
        elif isinstance(ast, list):
            return sum(_f(node) for node in ast)
        else:
            return 1

    return _f(ast) + len(action)


def show_pretty_table(fields, rows, title=None):
    table = PrettyTable()
    if title is not None:
        table.title = title
    table.field_names = fields
    table.add_rows(rows)
    print(table, end='\n\n')


def parse_program(program, action):
    if program is None:
        return 0, 0, 0, 0, 0

    def match_pattern(pattern, prog):
        match_num = re.findall(pattern, prog)
        if match_num is None:
            return 0
        else:
            return len(match_num)

    prog_num_ast, prog_num_and, prog_num_or, prog_num_in, prog_num_nin = 0, 0, 0, 0, 0
    for cls in [TEXT, VEHICLE, PERSON]:
        if program[cls] is not None:
            if program[cls] in {True, False}:
                prog_num_ast += 1
            else:
                ast = parser.parse(program[cls])
                prog_num_ast += count_ast(ast, action)
                prog_num_and += match_pattern("AND\(", program[cls])
                prog_num_or += match_pattern("OR\(", program[cls])
                prog_num_in += match_pattern("∈", program[cls])
                prog_num_nin += match_pattern("∉", program[cls])
    return prog_num_ast, prog_num_and, prog_num_or, prog_num_in, prog_num_nin


def pprint_tables(tables):
    for rows in zip(*map(lambda xs: str(xs).split('\n'), tables)):
        print(''.join(rows))


def stats_benchmarks():
    tasks = {TEXT: [], VEHICLE: [], PERSON: [], MIX: []}
    for idx in range(1, 21):
        task_file = os.path.join(DATASET_DIR, str(idx), f"image{idx}.tasks")
        if not os.path.exists(task_file):
            continue
        obj_file = os.path.join(DATASET_DIR, str(idx), f"image{idx}.objs")
        idx2cls, cls2idx, data = {}, defaultdict(list), defaultdict(dict)
        with open(obj_file, 'r') as reader:
            for line in reader:
                line = json.loads(line)
                idx2cls[line['id']] = line['cls']
                cls2idx[line['cls']].append(line['id'])
                data[line['cls']][line['id']] = line
        with open(task_file, 'r') as reader:
            for line in reader:
                # print(line)
                line = json.loads(line)
                clses = {idx2cls[idx] for idx in line['positive'] + line['negative']}
                attrs = {}
                for cls in clses:
                    # #attr
                    cls_attrs = {key: len(values) for key, values in CODOMAINS[cls].items()}
                    if cls == TEXT:
                        if cls in line['parameters']:
                            for key, values in line['parameters'][cls].items():
                                cls_attrs.pop(key)
                                for v in values:
                                    cls_attrs[v] = 2
                        cls_attrs['Length'] = len(set([len(data[cls][id]['Context']) for id in cls2idx[cls]]))
                    elif cls == PERSON:
                        cls_attrs['Age'] = len(set([int(data[cls][id]['Age']) for id in cls2idx[cls]]))
                    attrs[cls] = cls_attrs
                info = [idx, line["id"], attrs, line['positive'], line['negative'], len(idx2cls)]
                if len(clses) == 1:
                    tasks[list(clses)[0]].append(info)
                else:
                    tasks["Mix"].append(info)

    CSV_FILE = os.path.join(OUT_DIR, "table1.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write fields
        fields = ["Task", "#", "Avg #attr", "Avg |range|", "Avg #pos", "Avg #neg", "Avg #obj"]
        writer.writerow(fields)
        # write lines
        num = 0
        positives, negatives, objects, attributes, ranges = [], [], [], [], []
        for cls, cls_tasks in tasks.items():
            num += len(cls_tasks)
            cls_positives, cls_negatives, cls_objects, cls_attrs, cls_ranges = [], [], [], [], []
            for task in cls_tasks:
                attrs, pos, neg, obj = task[2:]
                cls_positives.append(len(pos))
                cls_negatives.append(len(neg))
                cls_objects.append(obj)
                num_cls_attrs = sum([len(v) for _, v in attrs.items()])
                cls_attrs.append(num_cls_attrs)
                num_cls_ranges = sum(([sum(v.values()) for _, v in attrs.items()])) / num_cls_attrs
                cls_ranges.append(num_cls_ranges)
            writer.writerow([cls, len(cls_positives), mean(cls_attrs), mean(cls_ranges),
                             mean(cls_positives), mean(cls_negatives), mean(cls_objects)])
            positives += cls_positives
            negatives += cls_negatives
            objects += cls_objects
            attributes += cls_attrs
            ranges += cls_ranges
        writer.writerow(
            ["Total", len(positives), mean(attributes), mean(ranges), mean(positives), mean(negatives), mean(objects)])


def stats_manirender():
    data = []
    with open(manirender_file, 'r') as reader:
        for idx, line in enumerate(reader):
            line = json.loads(line)
            data.append(line)

    num_ast, num_and, num_or, num_in, num_nin = [], [], [], [], []
    num_solved, num_timeout, num_plausible, num_node, search_time = 0, 0, 0, [], []

    CSV_FILE = os.path.join(OUT_DIR, "table2.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write fields
        writer.writerow(["Task", "#", "|AST|", "#/\\", "#\\/", "#in", "#nin", "#T", "#S", "#P", "|L|", \
                         "Min-Time", "Med-Time", "Avg-Time", "Max-Time"])
        for cls, ids in CLS2IDS.items():
            cls_num_ast, cls_num_and, cls_num_or, cls_num_in, cls_num_nin = [], [], [], [], []
            cls_num_solved, cls_num_timeout, cls_num_plausible, cls_num_node, cls_search_time = 0, 0, 0, [], []
            for idx in ids:
                line = data[idx]
                # count #timeout, #solved, #plausible
                if 'correct' in line:
                    # not timeout
                    if set(line['correct']) == set(line['groundtruth']) and line['#wrong'] == 0:
                        cls_num_solved += 1
                    else:
                        cls_num_plausible += 1
                # count lattice size
                if '#plattice_node' in line:
                    cls_num_node.append(line['#plattice_node'])
                # count ast and operators

                prog_num_ast, prog_num_and, prog_num_or, prog_num_in, prog_num_nin = \
                    parse_program(line['program'], line['action'])
                cls_num_ast.append(prog_num_ast)
                cls_num_and.append(prog_num_and)
                cls_num_or.append(prog_num_or)
                cls_num_in.append(prog_num_in)
                cls_num_nin.append(prog_num_nin)

                # count avg time, do not approximate every tasks' timecosts
                timecosts = [count_time(tc) for tc in line['time']]
                timecost = sum(timecosts) / len(timecosts)
                if timecost < TIMEOUT:
                    cls_search_time.append(timecost)
                else:
                    cls_num_timeout += 1
            cls_num = cls_num_timeout + cls_num_solved + cls_num_plausible
            avg_cls_num_node = mean(cls_num_node)
            avg_cls_num_node = beautify_lattice_size(avg_cls_num_node)

            writer.writerow([cls, cls_num, stats_func(cls_num_ast)[2], mean(cls_num_and), mean(cls_num_or),
                             mean(cls_num_in), mean(cls_num_nin), cls_num_timeout, cls_num_solved, cls_num_plausible,
                             avg_cls_num_node, *stats_func(cls_search_time)])

            num_ast += cls_num_ast
            num_and += cls_num_and
            num_or += cls_num_or
            num_in += cls_num_in
            num_nin += cls_num_nin
            num_timeout += cls_num_timeout
            num_solved += cls_num_solved
            num_plausible += cls_num_plausible
            search_time += cls_search_time
            num_node += cls_num_node
        num = num_timeout + num_solved + num_plausible
        avg_num_node = mean(num_node)
        avg_num_node = beautify_lattice_size(avg_num_node)

        writer.writerow(["Total", num, stats_func(num_ast)[2], mean(num_and), mean(num_or), mean(num_in), mean(num_nin),
                         num_timeout, num_solved, num_plausible, avg_num_node, *stats_func(search_time)])


def stats_baseline(file, title):
    data = []
    with open(file, 'r') as reader:
        for idx, line in enumerate(reader):
            line = json.loads(line)
            data.append(line)

    fields = ["Task", "#", f"#T-{title}", f"#S-{title}", f"#P-{title}", f"Time(s)-{title}"]
    rows = []
    num_solved, num_timeout, num_plausible, search_time = 0, 0, 0, []
    for cls, ids in CLS2IDS.items():
        cls_num_solved, cls_num_timeout, cls_num_plausible, cls_search_time = 0, 0, 0, []
        for idx in ids:
            line = data[idx]
            if 'correct' in line:
                # not timeout
                if set(line['correct']) == set(line['groundtruth']) and line['#wrong'] == 0:
                    cls_num_solved += 1
                else:
                    cls_num_plausible += 1

            timecosts = [count_time(tc) for tc in line['time']]
            timecost = sum(timecosts) / len(timecosts)
            if timecost < TIMEOUT:
                cls_search_time.append(timecost)
            else:
                cls_num_timeout += 1

        cls_num = cls_num_timeout + cls_num_solved + cls_num_plausible
        rows.append([cls, cls_num, cls_num_timeout, cls_num_solved, cls_num_plausible, mean(cls_search_time)])
        num_timeout += cls_num_timeout
        num_solved += cls_num_solved
        num_plausible += cls_num_plausible
        search_time += cls_search_time
    num = num_timeout + num_solved + num_plausible
    rows.append(["Total", num, num_timeout, num_solved, num_plausible, mean(search_time)])
    return fields, rows


def stats_lattice(file, title, only_total=False):
    data = []
    with open(file, 'r') as reader:
        for idx, line in enumerate(reader):
            line = json.loads(line)
            data.append(line)

    fields = ["Task", "#", f"#T-{title}", f"#S-{title}", f"#P-{title}", f"Time(s)-{title}"]
    rows = []
    num_solved, num_timeout, num_plausible, num_node, search_time = 0, 0, 0, [], []
    for cls, ids in CLS2IDS.items():
        cls_num_solved, cls_num_timeout, cls_num_plausible, cls_num_node, cls_search_time = 0, 0, 0, [], []
        for idx in ids:
            line = data[idx]
            if 'correct' in line:
                # not timeout
                if set(line['correct']) == set(line['groundtruth']) and line['#wrong'] == 0:
                    cls_num_solved += 1
                else:
                    cls_num_plausible += 1
            if '#plattice_node' in line:
                cls_num_node.append(line['#plattice_node'])

            timecosts = [count_time(tc) for tc in line['time']]
            timecost = sum(timecosts) / len(timecosts)
            if timecost < TIMEOUT:
                cls_search_time.append(timecost)
            else:
                cls_num_timeout += 1
        cls_num = cls_num_timeout + cls_num_solved + cls_num_plausible
        if not only_total:
            rows.append([cls, cls_num, cls_num_timeout, cls_num_solved, cls_num_plausible, mean(cls_search_time)])
        num_timeout += cls_num_timeout
        num_solved += cls_num_solved
        num_plausible += cls_num_plausible
        search_time += cls_search_time
        num_node += cls_num_node
    num = num_timeout + num_solved + num_plausible
    rows.append(["Total", num, num_timeout, num_solved, num_plausible, mean(search_time)])
    return fields, rows


def stats_cmp_gts():
    stats_gts = [[10, 18.5, 20.4, 38], [11, 26.0, 30.8, 53], [10, 31.0, 37.8, 145], [10, 19.0, 19.1, 36],
                 [10, 27.0, 32.7, 145]]
    stats_syn_progs = {}
    with open(manirender_file, 'r') as reader:
        prog_sizes = []
        for line in map(json.loads, reader):
            prog_num_ast, _, _, _, _ = parse_program(line['program'], line['action'])
            prog_sizes.append(prog_num_ast)
        for cls, ids in CLS2IDS.items():
            cls_prog_sizes = [prog_sizes[idx] for idx in ids]
            stats_syn_progs[cls] = [len(cls_prog_sizes)] + stats_func(cls_prog_sizes)
        stats_syn_progs["Total"] = [len(prog_sizes)] + stats_func(prog_sizes)

    CSV_FILE = os.path.join(OUT_DIR, "table3.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Task", "#", "Syn-Min", "Syn-Med", "Syn-Avg", "Syn-Max", "GT-Min", "GT-Med", "GT-Avg", "GT-Max"])
        for idx, (cls, stats) in enumerate(stats_syn_progs.items()):
            writer.writerow([cls] + stats + stats_gts[idx])


def stats_baselines():
    fields1, rows1 = stats_baseline(eusolver_file, "EUSolver")
    fields2, rows2 = stats_baseline(imageeye_file, "ImageEye")
    fields3, rows3 = stats_lattice(manirender_file, "ManiRender")

    CSV_FILE = os.path.join(OUT_DIR, "table4.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write fields
        fields = fields1 + fields2[2:] + fields3[2:]
        writer.writerow(fields)
        # write lines
        for idx, (row1, row2, row3) in enumerate(zip(rows1, rows2, rows3)):
            writer.writerow(row1 + row2[2:] + row3[2:])


def stats_ablation():
    fields1, rows1 = stats_lattice(manirender_wo_abst_diff_file, "ManiRender w/o Diff & Abst", only_total=True)
    fields2, rows2 = stats_lattice(manirender_wo_diff_file, "ManiRender w/o Diff", only_total=True)
    fields3, rows3 = stats_lattice(manirender_wo_abst_file, "ManiRender w/o Abst", only_total=True)
    fields4, rows4 = stats_lattice(manirender_file, "ManiRender", only_total=True)
    # pprint_tables(
    #     tables=[manirender_wo_abst_diff_table, manirender_wo_diff_table, manirender_wo_abst_table, manirender_table])

    CSV_FILE = os.path.join(OUT_DIR, "table6.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write fields
        fields = ["Model", "#T", "#S", "#P", "Time (s)"]
        writer.writerow(fields)
        # write lines
        writer.writerow(["ManiRender w/o Diff & Abst"] + rows1[0][2:])
        writer.writerow(["ManiRender w/o Diff"] + rows2[0][2:])
        writer.writerow(["ManiRender w/o Abst"] + rows3[0][2:])
        writer.writerow(["ManiRender"] + rows4[0][2:])


def stats_prompt():
    def stats_gpt(file, title):
        # print(file)
        data = []
        with open(file, 'r') as reader:
            for idx, line in enumerate(reader):
                line = json.loads(line)
                data.append(line)

        num_solved, num_determ, num_consist = 0, 0, 0
        fields = ["Task", "#", f"#S-{title}", f"#D-{title}", f"#C-{title}"]
        rows = []
        for cls, ids in CLS2IDS.items():
            cls_num_solved, cls_num_determ, cls_num_consist = 0, 0, 0
            for idx in ids:
                if idx >= len(data):
                    continue

                line = data[idx]
                if 'correct' in line and set(line['correct']) == set(line['groundtruth']) and line['#wrong'] == 0:
                    cls_num_solved += 1
                    assert line['consistent'] == True, line
                cls_num_determ += int(line['deterministic'])
                cls_num_consist += int(line['consistent'])
            rows.append([cls, len(CLS2IDS[cls]), cls_num_solved, cls_num_determ, cls_num_consist])
            num_solved += cls_num_solved
            num_determ += cls_num_determ
            num_consist += cls_num_consist
        rows.append(["Total", sum(len(ids) for ids in CLS2IDS.values()), num_solved, num_determ, num_consist])
        return fields, rows

    def stats_manirender(file, title):
        data = []
        with open(file, 'r') as reader:
            for idx, line in enumerate(reader):
                line = json.loads(line)
                data.append(line)

        num_solved, num_determ, num_consist = 0, 0, 0
        table = PrettyTable()
        table.title = title
        fields = ["Task", "#", f"#S-{title}", f"#D-{title}", f"#C-{title}"]
        rows = []
        for cls, ids in CLS2IDS.items():
            cls_num_solved, cls_num_determ, cls_num_consist = 0, 0, 0
            for idx in ids:
                line = data[idx]
                if 'correct' in line and set(line['correct']) == set(line['groundtruth']) and line['#wrong'] == 0:
                    cls_num_solved += 1
                cls_num_determ += 1
                cls_num_consist += 1
            rows.append([cls, len(CLS2IDS[cls]), cls_num_solved, cls_num_determ, cls_num_consist])
            num_solved += cls_num_solved
            num_determ += cls_num_determ
            num_consist += cls_num_consist
        rows.append(["Total", sum(len(ids) for ids in CLS2IDS.values()), num_solved, num_determ, num_consist])
        return fields, rows

    fields1, rows1 = stats_gpt(chatgpt4o_file, "GPT-4o")
    fields2, rows2 = stats_manirender(manirender_file, "ManiRender")
    # pprint_tables(tables=[gpt_table, manirender_table])

    CSV_FILE = os.path.join(OUT_DIR, "table5.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write fields
        fields = fields1 + fields2[2:]
        writer.writerow(fields)
        # write lines
        for idx, (row1, row2) in enumerate(zip(rows1, rows2)):
            writer.writerow(row1 + row2[2:])


def stats_scalability():
    beautify_times = lambda xs: [x if isinstance(x, str) else round(x + 1e-10, 2) for x in xs]

    with open(scalability_attr_file, 'r') as reader:
        data = list(map(json.loads, reader))

    CSV_FILE = os.path.join(OUT_DIR, "table7.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write fields
        fields = ["#attr"] + [line["#attr"] for line in data]
        writer.writerow(fields)
        # write lines
        load_times = beautify_times([line["time"][0] for line in data])
        writer.writerow(["Loading (s)"] + load_times)
        search_times = beautify_times([line["time"][1] for line in data])
        writer.writerow(["Search (s)"] + search_times)

    with open(scalability_range_file, 'r') as reader:
        data = list(map(json.loads, reader))

    CSV_FILE = os.path.join(OUT_DIR, "table8.csv")
    with open(CSV_FILE, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # write fields
        fields = ["|range|"] + [line["#range"] for line in data]
        writer.writerow(fields)
        # write lines
        load_times = [line["time"][0] for line in data]
        load_times = ["<0.01" if not isinstance(x, str) and x < 0.01 else x for x in load_times]
        writer.writerow(["Loading (s)"] + beautify_times(load_times))
        search_times = [line["time"][1] for line in data]
        search_times = ["<0.02" if not isinstance(x, str) and x < 0.02 else x for x in search_times]
        writer.writerow(["Search (s)"] + beautify_times(search_times))


if __name__ == '__main__':
    stats_benchmarks()  # Table 1
    stats_manirender()  # Table 2
    stats_cmp_gts()  # Table 3
    stats_baselines()  # Table 4
    stats_prompt()  # Table 5
    stats_ablation()  # Table 6
    stats_scalability()  # Tables 7 and 8
