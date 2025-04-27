# -*- coding:utf-8 -*-


import os
import json
from constants import DATASET_DIR
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from constants import PROJECT_DIR
import argparse
from benchmarks import DIR as BENCHMARK_DIR

DIR = os.path.dirname(__file__)

parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str, default="history", choices=["benchmarks", "history"])
args = parser.parse_args()

OUT_DIR = os.path.join(PROJECT_DIR, {
    "benchmarks": "rqs",
    "history": "history",
}[args.directory])

matplotlib.rcParams['text.usetex'] = True

EUSOLVER = "eusolver"
IMAGEEYE = "imageeye"
MAINRENDER = "mainrender"


def save_figure(fig, filename):
    filename = os.path.join(PROJECT_DIR, filename)
    fig.savefig(filename, transparent=True)


def get_timecosts(filename, time_func=sum):
    timecosts = []

    file = os.path.join(PROJECT_DIR, args.directory, filename)
    with open(file, 'r') as reader:
        for line in reader:
            line = json.loads(line)
            avg_time = round(time_func(line["time"]) / len(line["time"]), 4)
            timecosts.append(avg_time)
    return timecosts


def get_vanilla_timecosts():
    filenames = [
        "results.eusolver",
        "results.imageeye",
        "results.diff-abst.manirender"
    ]

    def time_func(timecosts: list):
        if isinstance(timecosts[0], list):
            total_timecost = sum(sum(x[:2]) for x in timecosts) / len(timecosts)
        else:
            total_timecost = sum(timecosts) / len(timecosts)
        return round(total_timecost, 4)

    funcs = [sum, time_func, time_func][-len(filenames):]
    labels = ["EUSolver", "ImageEye", "ManiRender"][-len(filenames):]
    timecosts = {}
    for label, filename, func in zip(labels, filenames, funcs):
        timecosts[label] = get_timecosts(filename, func)
    return timecosts


def get_ablation_study():
    def time_func(timecosts: list):
        if isinstance(timecosts[0], list):
            total_timecost = sum(sum(x[:2]) for x in timecosts) / len(timecosts)
        else:
            total_timecost = sum(timecosts) / len(timecosts)
        return round(total_timecost, 4)

    filenames = [
        "results.manirender",
        "results.abst.manirender",
        "results.diff.manirender",
        "results.diff-abst.manirender"
    ]
    funcs = [time_func, time_func, time_func, time_func]
    labels = ["ManiRender w/o Diff + Abst", "ManiRender w/o Diff", "ManiRender w/o Abst", "ManiRender"][
             -len(filenames):]
    timecosts = {}
    for label, filename, func in zip(labels, filenames, funcs):
        timecosts[label] = get_timecosts(filename, func)
    return timecosts


def plot_baselines(filename):
    # print(filename)
    timecosts = get_vanilla_timecosts()

    fig = plt.figure(figsize=[5, 2.7])
    fig.subplots_adjust(top=0.97, bottom=0.17, left=0.12, right=0.97)
    NUM_PROGS = 102
    MAX_TIME = 180
    ax = fig.add_subplot(111)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_xlabel("\#Programs")
    ax.set_ylabel("Time (s)")
    ax.set_yticks(range(0, MAX_TIME + 30, 30))
    plt.ylim([0, MAX_TIME])
    plt.xlim([0, NUM_PROGS])

    markers = ["*", "^", "."][-len(timecosts):]
    colors = ["#377eb8", "#4daf4a", "#984ea3"][-len(timecosts):]
    for (label, times), marker, color in zip(timecosts.items(), markers, colors):
        x_data = list(range(0, 1 + NUM_PROGS))
        y_data = [0] + sorted(times)
        x_data, y_data = zip(*[(x, y) for x, y in zip(x_data, y_data) if y < MAX_TIME])
        ax.plot(x_data, y_data, label=label, marker=marker, markersize=4, color=color)
        # print(f"{label}: {len(x_data) - 1}")
    ax.legend(loc="upper left")
    plt.grid(linestyle="--", linewidth=0.3)
    # plt.show()
    save_figure(fig, filename)


def plot_ablation_study(filename):
    # print(filename)
    timecosts = get_ablation_study()

    fig = plt.figure(figsize=[5, 2.7])
    fig.subplots_adjust(top=0.97, bottom=0.17, left=0.12, right=0.97)
    NUM_PROGS = 102
    MAX_TIME = 180
    ax = fig.add_subplot(111)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_xlabel("\#Programs")
    ax.set_ylabel("Time (s)")
    ax.set_yticks(range(0, MAX_TIME + 30, 30))
    plt.ylim([0, MAX_TIME])
    plt.xlim([0, NUM_PROGS])
    markers = ["+", "*", "^", "."][-len(timecosts):]
    colors = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3"][-len(timecosts):]
    for (label, times), marker, color in zip(timecosts.items(), markers, colors):
        x_data = list(range(0, 1 + NUM_PROGS))
        y_data = [0] + sorted(times)
        x_data, y_data = zip(*[(x, y) for x, y in zip(x_data, y_data) if y < MAX_TIME])
        ax.plot(x_data, y_data, label=label, marker=marker, markersize=4, color=color)
        # print(f"{label}: {len(x_data) - 1}")
    ax.legend(loc="upper left")
    plt.grid(linestyle="--", linewidth=0.3)
    # plt.show()
    save_figure(fig, filename)


if __name__ == '__main__':
    plot_baselines(filename=os.path.join(OUT_DIR, "Fig8.pdf"))
    plot_ablation_study(filename=os.path.join(OUT_DIR, "Fig9.pdf"))
