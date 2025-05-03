# -*- coding:utf-8 -*-

import json
import os.path
import time

from functools import partial

from demo import *
import tkinter as tk
from tkinter.ttk import Combobox
from tkinter import (
    filedialog,
    Button,
    messagebox
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from demo.segmentor import Segmentor
from logger import LOGGER
from search import find_maximal_by_abstraction
import supervision as sv
import numpy as np
from matplotlib.patches import Circle
from order_theory import (
    IntervalLattice,
    SetLattice,
    LazyProductLattice,
)
from cv_tools.inpainter import Inpainter
from constants import (device, GPU, CPU)
from utils import (
    put_mosaic,
    blur_image,
)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--gpu', choices=[0, 1], type=int, default=0)
args = parser.parse_args()

DEVICE = CPU if args.gpu else GPU

# configuration
WIN_WIDTH, WIN_HEIGHT = 1680, 920
# WIN_WIDTH, WIN_HEIGHT = 960, 540
# WIN_WIDTH, WIN_HEIGHT = 1280, 720
FONT = ("Arial", 14)
ANN_FONT = ("Arial", 12)
PAD = 5
FIGURE_SIZE = (WIN_WIDTH * 0.98, 500)
SOLID = "solid"
RAISED = "raised"
SUNKEN = "sunken"

root = tk.Tk()
root.wm_title("MainRender")

# centre the Tkinter window

root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
root.resizable(False, False)


def init_labels():
    segment_lbl.configure(relief=RAISED)
    lattice_lbl.configure(relief=SUNKEN)
    label_lbl.configure(relief=SUNKEN)
    synthesis_lbl.configure(relief=SUNKEN)
    inpainting_lbl.configure(relief=SUNKEN)


def init_seg_btns():
    segment_btn.configure(state=tk.DISABLED)
    segment_btn.configure(text="Start segmenting")
    anl_btn.configure(state=tk.DISABLED)
    check_btn.configure(state=tk.DISABLED)
    txt_box.configure(state=tk.NORMAL)
    txt_box.delete("1.0", tk.END)
    txt_box.configure(state=tk.DISABLED)


def init_lattice_btns():
    # lattice_lbl.config(relief=SUNKEN)
    lattice_btn.configure(state=tk.DISABLED)
    lattice_info_box.configure(state=tk.NORMAL)
    lattice_info_box.delete("1.0", tk.END)
    lattice_info_box.configure(state=tk.DISABLED)


def init_lbl_btns():
    label_btn.configure(state=tk.DISABLED)
    revise_label_btn.configure(state=tk.DISABLED)


def init_syn_btns():
    synthesize_btn.configure(state=tk.DISABLED)
    program_textbox.configure(state=tk.NORMAL)
    program_textbox.delete("1.0", tk.END)
    program_textbox.insert(tk.END, "")
    program_textbox.configure(state=tk.DISABLED)


def init_inpainting_btns():
    # inpainting_lbl.config(relief=SUNKEN)
    inpainting_btn.configure(state=tk.DISABLED)
    op_listbox.configure(state=tk.NORMAL)
    op_listbox.set("")
    op_listbox.configure(state=tk.DISABLED)
    args_listbox.configure(state=tk.NORMAL)
    args_listbox.set("")
    args_listbox.configure(state=tk.DISABLED)
    inpainting_textbox.configure(state=tk.NORMAL)
    inpainting_textbox.delete("1.0", tk.END)
    inpainting_textbox.insert(tk.END, "")
    inpainting_textbox.configure(state=tk.DISABLED)
    export_btn.configure(state=tk.DISABLED)


def init():
    init_labels()
    init_seg_btns()
    init_lattice_btns()
    init_lbl_btns()
    init_syn_btns()
    init_inpainting_btns()


# help
def show_help_msg(event):
    messagebox.showinfo(
        "Help",
        "Q1: How to segment?\nA1:\n    Left click: positive label\n    Right click: negative label\n    Enter: segment object\n    Z: undo\n    Esc: Finish segmentation\n\nQ2: How to label objects?\nA2:\n    Left click: positive label\n    Right click: negative label"
    )


root.bind('<h>', show_help_msg)

# pipeline: Segmentation -> Label -> Lattice -> Synthesis -> Inpainting
LABEL_WIDTH, LABEL_HEIGHT = 20, 1
# Segmentation
segment_lbl = tk.Label(root, text="1.Segmentation", font=FONT, bd=3, relief=RAISED, padx=PAD, pady=PAD,
                       width=LABEL_WIDTH,
                       height=LABEL_HEIGHT)
segment_lbl.place(x=0, y=0)

# Lattice Construction
lattice_lbl = tk.Label(root, text="2.Lattice Construction", font=FONT, bd=3, relief=SUNKEN, padx=PAD, pady=PAD,
                       width=LABEL_WIDTH, height=LABEL_HEIGHT)
lattice_lbl.place(x=380, y=0)

# Label
label_lbl = tk.Label(root, text="3.Label", font=FONT, bd=3, relief=SUNKEN, padx=PAD, pady=PAD,
                     width=LABEL_WIDTH, height=LABEL_HEIGHT)
label_lbl.place(x=750, y=0)

synthesis_lbl = tk.Label(root, text="4.Synthesis", font=FONT, bd=3, relief=SUNKEN, padx=PAD, pady=PAD,
                         width=LABEL_WIDTH, height=LABEL_HEIGHT)
synthesis_lbl.place(x=1100, y=0)

# Inpainting
inpainting_lbl = tk.Label(root, text="5.Inpainting", font=FONT, bd=3, relief=SUNKEN, padx=PAD, pady=PAD,
                          width=LABEL_WIDTH, height=LABEL_HEIGHT)
inpainting_lbl.place(x=1440, y=0)

# how to use
help_lbl = tk.Label(root, text="Press H on keyboard to see how to use.", font=FONT)
help_lbl.place(x=20, y=40)


def read_jsonlines(file):
    with open(file, 'r') as reader:
        data = [json.loads(line) for line in reader]
    return data


# demo buttons
def load_demo_handler(demo):
    init()

    img_file = os.path.join(DIR, f"{demo}.jpg")
    segmenter.load_file(img_file)
    canvas = FigureCanvasTkAgg(segmenter.fig, master=root)
    canvas.get_tk_widget().place(x=20, y=150, width=FIGURE_SIZE[0], height=FIGURE_SIZE[1])
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    segmenter.attr_update_func = update_txt_box
    segmenter.info_update_func = lattice_info_update

    data_file = os.path.join(CACHE_DIR, f"{demo}/{demo}.jsonlines")
    objs = read_jsonlines(data_file)
    segmenter.data = {'file': img_file, 'shape': segmenter.img.shape[:2][::-1], 'objs': objs}
    full_legend = []
    for idx, obj in enumerate(objs, start=1):
        mask = sv.polygon_to_mask(np.asarray(obj['polygons']), segmenter.data['shape']).astype(np.bool_)
        segmenter.global_masks[mask, ...] = idx
        full_legend.append(Circle(1, color=np.array(segmenter.current_color) / 255, label=f'{idx}'))
        segmenter.mask_data[:, :, :3][mask] = segmenter.current_color
        segmenter.mask_data[:, :, 3][mask] = segmenter.opacity
        segmenter.mask_plot.set_data(segmenter.mask_data)
        segmenter.current_color = segmenter.pick_color()
    segmenter.axs[0].legend(handles=full_legend, loc='center left', bbox_to_anchor=(1, 0.5), ncol=2)
    segmenter.fig.canvas.draw()

    # load lattices
    lattice_dir = os.path.join(CACHE_DIR, demo)
    lattices = {}
    for key in ["Male", "Age", "Orientation", "Glasses", "Hat", "HoldObjectsInFront", "Bag", "TopStyle",
                "BottomStyle", "UpperBody", "LowerBody", "Boots"]:
        if key == "Age":
            lattices[key] = IntervalLattice.load(key, lattice_dir)
        else:
            lattices[key] = SetLattice.load(key, lattice_dir)
    product_lattice = LazyProductLattice(name="person", sublattices=list(lattices.values()))
    segmenter.data['data'], segmenter.lattice, _ = \
        segmenter.encode_person_attrs([obj for obj in segmenter.data['objs']], plattice=product_lattice)

    segmenter.data['masks'] = [
        sv.polygon_to_mask(np.asarray(obj['polygons']), segmenter.data['shape']).astype(np.bool_)
        for obj in segmenter.data['objs']
    ]

    # lattice_dir = os.path.join(CACHE_DIR, demo)
    # segmenter.data['data'], segmenter.lattice, build_time = \
    #     segmenter.encode_person_attrs([obj for obj in segmenter.data['objs']])
    # for sub_l in segmenter.lattice.sublattices:
    #     sub_l.dump(lattice_dir)

    label_btn.configure(state=tk.NORMAL)
    lattice_lbl.config(relief=RAISED)
    label_lbl.config(relief=RAISED)


demo1_btn = Button(root, text="Demo1", command=partial(load_demo_handler, demo="demo1"), font=FONT)
demo1_btn.place(x=400, y=70)

demo2_btn = Button(root, text="Demo2", command=partial(load_demo_handler, demo="demo2"), font=FONT)
demo2_btn.place(x=800, y=70)

demo3_btn = Button(root, text="Demo3", command=partial(load_demo_handler, demo="demo3"), font=FONT)
demo3_btn.place(x=1200, y=70)

# neural models
segmenter = Segmentor(device=DEVICE)
inpainter = Inpainter(device=DEVICE)


# load image
def load_img():
    file = filedialog.askopenfilename(title=f"Load an image",
                                      filetypes=[("Image Files", "*.jpg"), ("Image Files", "*.jpeg")])

    LOGGER.debug(file)
    segmenter.load_file(file)
    canvas = FigureCanvasTkAgg(segmenter.fig, master=root)
    canvas.get_tk_widget().place(x=20, y=150, width=FIGURE_SIZE[0], height=FIGURE_SIZE[1])
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    segmenter.data['file'] = file
    segmenter.attr_update_func = update_txt_box
    segmenter.info_update_func = lattice_info_update

    # check + init
    init()
    segment_btn.configure(state=tk.NORMAL)


load_btn = Button(root, text="Load an image", command=load_img, font=FONT, )
load_btn.place(x=20, y=680)


def start_segmenting_handler():
    btn_status = segment_btn.cget("text")
    if btn_status == "Start segmenting":
        segment_btn.configure(text="End segmenting")
        LOGGER.debug("Begin segmentation")
        segmenter.enable_interaction()
    else:
        if len(segmenter.trace) > 0:
            # if users do not press ENTER but click End segmenting, GUI will save current segmentation first
            segmenter.new_tow()

        # segment_btn.configure(text="Start segmenting")
        segment_btn.configure(state=tk.DISABLED)
        anl_btn.configure(state=tk.NORMAL)
        LOGGER.debug("Begin segmentation")
        segmenter.disable_interaction()
        seg_objs = segmenter.get_segmented_objs()
        segmenter.data['objs'] = list(seg_objs.values())


segment_btn = Button(root, text="Start segmenting", command=start_segmenting_handler, font=FONT, state=tk.DISABLED)
segment_btn.place(x=20, y=730)


def start_analysis_handler():
    anl_btn.configure(state=tk.DISABLED)
    check_btn.configure(state=tk.NORMAL)
    lattice_btn.configure(state=tk.NORMAL)
    segmenter.data['objs'][0] = {**segmenter.data['objs'][0],
                                 **{"Male": True, "Age": 22.01, "Orientation": "Front", "Glasses": False,
                                    "Hat": True, "HoldObjectsInFront": True, "Bag": "NoBag",
                                    "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True,
                                    "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": True,
                                    "SkirtDress": False, "Boots": True}}


anl_btn = Button(root, text="Start analysis", command=start_analysis_handler, font=FONT, state=tk.DISABLED)
anl_btn.place(x=20, y=780)


def check_attrs_handler():
    # click to check segmented obj
    segmenter.enable_click_obj()
    txt_box.config(state=tk.NORMAL)
    check_btn.configure(state=tk.DISABLED)
    upd_btn.config(state=tk.NORMAL)


check_btn = Button(root, text="Check attributes", command=check_attrs_handler, font=FONT, state=tk.DISABLED)
check_btn.place(x=20, y=830)

txt_box = tk.Text(root, wrap=tk.WORD, font=ANN_FONT, width=40, height=9, state=tk.DISABLED)
txt_box.place(x=220, y=680)


def update_attrs_handler():
    content = txt_box.get("1.0", tk.END)
    try:
        content = eval(content)
        segmenter.data['objs'][segmenter.obj_id - 1]['attrs'] = content
        LOGGER.debug(f"Updated attributes of #{segmenter.obj_id} obj.")
    except:
        messagebox.showinfo("Wrong attributes", content)


upd_btn = Button(root, text="Update", command=update_attrs_handler, font=FONT, state=tk.DISABLED)
upd_btn.place(x=500, y=870)


def update_txt_box(text):
    txt_box.delete("1.0", tk.END)
    txt_box.insert(tk.END, text)


# lattice

def build_lattice_handler():
    lattice_lbl.config(relief=SUNKEN)

    txt_box.configure(state=tk.NORMAL)
    update_txt_box("")
    txt_box.configure(state=tk.DISABLED)
    upd_btn.configure(state=tk.DISABLED)
    label_btn.configure(state=tk.NORMAL)
    segmenter.disable_click_obj()

    segmenter.data['data'], segmenter.lattice, build_time = \
        segmenter.encode_person_attrs([obj['attrs'] for obj in segmenter.data['objs']])

    # show info
    lattice_info_box.configure(state=tk.NORMAL)
    lattice_info_box.delete('1.0', tk.END)
    info = f"Building time: {build_time}s, #nodes: {segmenter.lattice.num_nodes}, #sub-lattices: {len(segmenter.lattice.sublattices)}."
    lattice_info_box.insert(tk.END, info)
    lattice_info_box.configure(state=tk.DISABLED)

    lattice_btn.configure(state=tk.DISABLED)


lattice_btn = Button(root, text="Build lattice", command=build_lattice_handler, font=FONT, state=tk.DISABLED)
lattice_btn.place(x=600, y=680)

lattice_info_box = tk.Text(root, wrap=tk.WORD, font=ANN_FONT, width=35, height=5, state=tk.DISABLED)
lattice_info_box.place(x=600, y=720)


def lattice_info_update(text):
    lattice_info_box.delete("1.0", tk.END)
    lattice_info_box.insert(tk.END, text)


# label

def remove_selected_contours():
    # remove contours from the synthesized program
    for plot in segmenter.pos_contour_plots + segmenter.neg_contour_plots:
        plot.set_data([], [])
        del plot
    segmenter.fig.canvas.draw()


def label_objs_handler():
    lattice_btn.configure(state=tk.DISABLED)
    init_inpainting_btns()

    btn_status = label_btn.cget("text")
    if btn_status == "Start labeling":
        label_btn.configure(text="End labeling")
        segmenter.enable_labels()
        revise_label_btn.configure(state=tk.DISABLED)
        label_lbl.config(relief=RAISED)
        synthesis_lbl.config(relief=SUNKEN)
        inpainting_lbl.config(relief=SUNKEN)
    elif btn_status == "Re-label":
        label_btn.configure(text="End labeling")
        segmenter.enable_labels()

        remove_selected_contours()

        synthesize_btn.configure(state=tk.DISABLED)
        revise_label_btn.configure(state=tk.DISABLED)
        program_textbox.configure(state=tk.NORMAL)
        program_textbox.delete("1.0", tk.END)
        program_textbox.insert(tk.END, "")
        program_textbox.configure(state=tk.DISABLED)

        inpainting_btn.configure(state=tk.DISABLED)
        op_listbox.configure(state=tk.NORMAL)
        op_listbox.set("")
        op_listbox.configure(state=tk.DISABLED)
        args_listbox.configure(state=tk.NORMAL)
        args_listbox.set("")
        args_listbox.configure(state=tk.DISABLED)
        inpainting_textbox.configure(state=tk.NORMAL)
        inpainting_textbox.delete("1.0", tk.END)
        inpainting_textbox.insert(tk.END, "")
        inpainting_textbox.configure(state=tk.DISABLED)
        export_btn.configure(state=tk.DISABLED)
    else:
        label_btn.configure(text="Re-label")
        segmenter.disable_labels()

        synthesize_btn.configure(state=tk.NORMAL)
        revise_label_btn.configure(state=tk.NORMAL)

        label_lbl.config(relief=RAISED)
        synthesis_lbl.config(relief=SUNKEN)
        inpainting_lbl.config(relief=SUNKEN)

        inpainting_btn.configure(state=tk.DISABLED)
        op_listbox.configure(state=tk.NORMAL)
        op_listbox.set("")
        op_listbox.configure(state=tk.DISABLED)
        args_listbox.configure(state=tk.NORMAL)
        args_listbox.set("")
        args_listbox.configure(state=tk.DISABLED)
        inpainting_textbox.configure(state=tk.NORMAL)
        inpainting_textbox.delete("1.0", tk.END)
        inpainting_textbox.insert(tk.END, "")
        inpainting_textbox.configure(state=tk.DISABLED)
        export_btn.configure(state=tk.DISABLED)


def revise_labels_handler():
    segmenter.enable_labels(drop_history=False)
    label_btn.configure(text="End labeling")
    program_textbox.configure(state=tk.NORMAL)
    program_textbox.delete("1.0", tk.END)
    program_textbox.insert(tk.END, "")
    program_textbox.configure(state=tk.DISABLED)
    revise_label_btn.configure(state=tk.DISABLED)

    label_lbl.config(relief=RAISED)
    synthesis_lbl.config(relief=SUNKEN)
    inpainting_lbl.config(relief=SUNKEN)


label_btn = Button(root, text="Start labeling", command=label_objs_handler, font=FONT, state=tk.DISABLED)
label_btn.place(x=600, y=830)

revise_label_btn = Button(root, text="Revise labels", command=revise_labels_handler, font=FONT, state=tk.DISABLED)
revise_label_btn.place(x=775, y=830)


# synthesize
def synthesize_handler():
    remove_selected_contours()

    synthesis_lbl.config(relief=RAISED)
    inpainting_lbl.config(relief=SUNKEN)
    label_btn.configure(state=tk.DISABLED)

    start_time = time.time()
    pos_ids = [segmenter.data['data'][idx - 1] for idx in segmenter.positives.keys()]
    neg_ids = [segmenter.data['data'][idx - 1] for idx in segmenter.negatives.keys()]
    LOGGER.debug(f"+: {sorted(segmenter.positives.keys())}, -: {sorted(segmenter.negatives.keys())}")
    if len(pos_ids) == 0 and len(neg_ids) == 0:
        prog = ""
        pos_coverage, neg_coverage = [], []
    elif len(pos_ids) != 0 and len(neg_ids) == 0:
        prog = "True"
        pos_coverage, neg_coverage = list(range(segmenter.label)), []
    elif len(pos_ids) == 0 and len(neg_ids) != 0:
        prog = "False"
        pos_coverage, neg_coverage = [], list(range(segmenter.label))
    else:
        maximals, prog = find_maximal_by_abstraction(pos_ids, neg_ids, segmenter.lattice, abstraction=True)
        pos_coverage, neg_coverage = [], [idx - 1 for idx in segmenter.negatives.keys()]
        for idx, encoded_obj in enumerate(segmenter.data['data'], start=0):
            if any(segmenter.lattice.coveredby(encoded_obj, maximal) for maximal in maximals):
                pos_coverage.append(idx)

    synth_time = round(time.time() - start_time, 2)
    prog = f"# time: {synth_time}s\nProgram = Filter(Lambda x. {prog.replace('∈', 'in')}, Objs)"
    segmenter.pos_coverage = pos_coverage
    segmenter.neg_coverage = neg_coverage

    # show program
    program_textbox.configure(state=tk.NORMAL)
    program_textbox.delete("1.0", tk.END)
    program_textbox.insert(tk.END, prog)
    program_textbox.configure(state=tk.DISABLED)

    segmenter.disable_labels()

    # highlight contours of +/- objects
    segmenter.draw_contours_after_synthesis(pos_coverage, neg_coverage)

    synthesize_btn.configure(state=tk.DISABLED)
    label_btn.configure(state=tk.NORMAL)

    inpainting_btn.configure(state=tk.NORMAL)
    op_listbox.configure(state=tk.NORMAL)
    args_listbox.configure(state=tk.DISABLED)


synthesize_btn = Button(root, text="Synthesize", command=synthesize_handler, font=FONT, state=tk.DISABLED)
synthesize_btn.place(x=930, y=680)

program_textbox = tk.Text(root, wrap=tk.WORD, font=ANN_FONT, width=35, height=7, state=tk.DISABLED)
program_textbox.place(x=930, y=720)


# inpainting
def inpainting_handler():
    inpainting_lbl.config(relief=RAISED)
    export_btn.configure(state=tk.NORMAL)

    op = op_listbox.get()
    args = args_listbox.get()

    start_time = time.time()
    img = segmenter.img.copy()
    if op == "Blankout":
        for idx in segmenter.pos_coverage:
            img[segmenter.data['masks'][idx], :] = 0
    elif op == "Mosaic":
        for idx in segmenter.pos_coverage:
            img = put_mosaic(img, segmenter.data['objs'][idx]['box'], segmenter.data['masks'][idx])
    elif op == "Blur":
        mask = np.zeros(img.shape[:2]).astype(np.bool_)
        for idx in segmenter.pos_coverage:
            mask |= segmenter.data['masks'][idx]
        img = blur_image(img, mask)
    elif op == "Remove":
        mask = np.zeros(img.shape[:2]).astype(np.bool_)
        for idx in segmenter.pos_coverage:
            mask |= segmenter.data['masks'][idx]
        img = inpainter.remove(img, mask)
    # elif op == "Recolor":
    #     if args == "":
    #         messagebox.showinfo("Error!!!", "You must choose one color.")
    #         return
    #     mask = np.zeros(img.shape[:2]).astype(np.bool_)
    #     for idx in segmenter.pos_coverage:
    #         mask |= segmenter.data['masks'][idx]
    #     img = inpainter.recolor(img, mask, color=args)
    elif op == "Change background (+ prompt)":
        if args == "":
            messagebox.showinfo("Error!!!", "No prompt.")
            return
        # segmenter.sam = segmenter.sam.to(CPU)
        # torch.cuda.empty_cache()
        # inpainter.device = GPU
        mask = np.zeros(img.shape[:2]).astype(np.bool_)
        for idx in segmenter.pos_coverage:
            mask |= segmenter.data['masks'][idx]
        LOGGER.debug(args)
        img = inpainter.replace(img, mask, args)
    elif op == "Replace objects (+ prompt)":
        if args == "":
            messagebox.showinfo("Error!!!", "No prompt.")
            return
        # segmenter.sam = segmenter.sam.to(CPU)
        # torch.cuda.empty_cache()
        # inpainter.device = GPU
        mask = np.zeros(img.shape[:2]).astype(np.bool_)
        for idx in segmenter.pos_coverage:
            mask |= segmenter.data['masks'][idx]
        LOGGER.debug(args)
        img = inpainter.fill(img, mask, args)
    else:
        messagebox.showinfo("Error!!!", "You must choose one operation.")
        return
    syn_time = round(time.time() - start_time, 2)

    LOGGER.debug(f"Inpainting: {img.shape}")
    segmenter.plot_inpainting_image(img)

    inpainting_textbox.config(state=tk.NORMAL)
    inpainting_textbox.delete("1.0", tk.END)
    inpainting_textbox.insert(tk.END, f"Inpainting time: {syn_time}s")
    inpainting_textbox.configure(state=tk.DISABLED)


inpainting_btn = Button(root, text="Inpainting", command=inpainting_handler, font=FONT, state=tk.DISABLED)
inpainting_btn.place(x=1260, y=680)


def op_change_handler(event):
    op = op_listbox.get()
    if op == "Recolor":
        args_listbox.configure(state=tk.NORMAL)
        args_listbox['values'] = color_options
    elif op == "Change background (+ prompt)":
        args_listbox.configure(state=tk.NORMAL)
        args_listbox.set("people on beach")
    elif op == "Replace objects (+ prompt)":
        args_listbox.configure(state=tk.NORMAL)
        args_listbox.set("dogs on soccer field")
    else:
        args_listbox.configure(state=tk.NORMAL)
        args_listbox.set("")
        args_listbox.configure(state=tk.DISABLED)


op_options = ["Blankout", "Mosaic", "Blur", "Remove", "Change background (+ prompt)", "Replace objects (+ prompt)"]
op_listbox = Combobox(root, values=op_options, font=FONT, state=tk.DISABLED, width=20, height=8)
op_listbox.bind("<<ComboboxSelected>>", op_change_handler)
op_listbox.place(x=1380, y=685)

color_options = ["black", "white", "blue"]
args_listbox = Combobox(root, values=[], font=FONT, state=tk.DISABLED, width=20, height=8)
args_listbox.place(x=1380, y=730)

inpainting_textbox = tk.Text(root, wrap=tk.WORD, font=ANN_FONT, width=40, height=2, state=tk.DISABLED)
inpainting_textbox.place(x=1260, y=770)


# export file

def export_handler():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("Image files", "*.jpg"), ("Image files", "*.jpeg")]
    )

    img = segmenter.axs[1].get_window_extent().transformed(segmenter.fig.dpi_scale_trans.inverted())
    plt.savefig(file_path, bbox_inches=img, dpi=300)


export_btn = Button(root, text="Save as", command=export_handler, font=FONT, state=tk.DISABLED)
export_btn.place(x=1260, y=840)

tk.mainloop()
