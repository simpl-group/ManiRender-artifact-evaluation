# -*- coding:utf-8 -*-

import time

import numpy as np
from matplotlib import pyplot as plt

import cv2
import matplotlib as mpl
from segment_anything import sam_model_registry, SamPredictor
import os
from matplotlib.patches import Circle
from cv_tools.configs import SAM_CHECKPOINT_MODEL
from constants import device
import supervision as sv
import json
from demo import DIR

HOLES = "holes"
ISLANDS = "islands"


class Segmentor:
    MIN_MASK_REGION_AREA = 500

    def __init__(self, device=device):
        # use SAM to handle images
        self.sam = sam_model_registry["vit_h"](checkpoint=SAM_CHECKPOINT_MODEL).to(device)
        self.predictor = SamPredictor(self.sam)
        # self.sam = self.predictor = None

    @staticmethod
    def read_image(file, size=(1920, 1080)):
        # RGB + opacity
        img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        # # resize it within 1920 x 1080
        # w, h = img.shape[:2]
        # ratio = min(size[0] / h, size[1] / w)
        # size = (int(h * ratio), int(w * ratio))
        # img = cv2.resize(img, size, interpolation=cv2.INTER_LANCZOS4)
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif img.ndim == 2:
            img = np.repeat(img[:, :, np.newaxis], 3, axis=2)
        return img

    def load_file(self, file):
        self.img = self.read_image(file)
        # self.tmp_file = os.path.join(TMP_DIR, os.path.basename(file)[:-4] + ".jsonlines")  # user-segmented file
        # self.cache_file = os.path.join(CACHE_DIR, os.path.basename(file)[:-4] + ".jsonlines")  # pre-segmented file
        self.predictor.set_image(self.img)
        # label +/- samples for segmentation
        # trace := [Bool], True -> + label, False -> - label
        self.add_xs, self.add_ys, self.rem_xs, self.rem_ys, self.trace = [], [], [], [], []

        # self.fig = plt.Figure(figsize=(10 * (self.img.shape[1] / max(self.img.shape)) * 2,
        #                                10 * (self.img.shape[0] / max(self.img.shape))))
        self.fig, self.axs = plt.subplots(1, 2, sharey=True, figsize=(60, 20))
        self.fig.subplots_adjust(top=0.99, bottom=0., left=0., right=1., wspace=0.)
        self.im = self.axs[0].imshow(self.img, cmap=mpl.cm.gray)
        self.axs[0].axis('off')
        self.axs[0].title.set_text('Input image')
        self.axs[1].axis('off')
        self.axs[1].title.set_text('Output image')
        self.axs1_fronze_box = None
        # choose segmentation color
        self.color_set = set()
        self.current_color = self.pick_color()
        self.label = 1
        # + labels for segmentation
        self.add_plot, = self.axs[0].plot([], [], 'o', markerfacecolor='green', markeredgecolor='black', markersize=5)
        # - labels for segmentation
        self.rem_plot, = self.axs[0].plot([], [], 'x', markerfacecolor='red', markeredgecolor='red', markersize=5)
        # + labels for manually labeling
        self.pos_plot, = self.axs[0].plot([], [], 'P', markerfacecolor='green', markeredgecolor='black', markersize=10)
        # - labels for manually labeling
        self.neg_plot, = self.axs[0].plot([], [], 'X', markerfacecolor='red', markeredgecolor='red', markersize=10)
        self.mask_data = np.zeros((self.img.shape[0], self.img.shape[1], 4), dtype=np.uint8)
        for i in range(3):
            self.mask_data[:, :, i] = self.current_color[i]
        self.mask_plot = self.axs[0].imshow(self.mask_data)
        self.prev_mask_data = np.zeros((self.img.shape[0], self.img.shape[1], 4), dtype=np.uint8)
        self.prev_mask_plot = self.axs[0].imshow(self.prev_mask_data)
        self.contour_plot, = self.axs[0].plot([], [], color='black')  # plot contours for segmented objs
        self.enable_button = self.enable_key = None

        self.opacity = 120  # out of 255
        self.global_masks = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=np.uint8)
        self.last_mask = np.zeros((self.img.shape[0], self.img.shape[1]), dtype=bool)  # to undo
        self.full_legend = []
        box = self.axs[0].get_position()
        self.axs[0].set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # GUI
        self.data = {'file': None, 'shape': self.img.shape[:2][::-1], 'objs': []}
        self.obj_id = None
        self.attr_update_func = self.info_update_func = None
        self.enable_button = self.enable_key = self.enable_click = self.enable_labels_handler = None
        self.pos_coverage = self.neg_coverage = None
        self.pos_contour_plots, self.neg_contour_plots = [], []

    def enable_interaction(self):
        self.enable_button = self.fig.canvas.mpl_connect('button_press_event', self._on_click)  # click events
        self.enable_key = self.fig.canvas.mpl_connect('key_press_event', self._on_key)  # key events

    def disable_interaction(self):
        if self.enable_button is not None:
            self.fig.canvas.mpl_disconnect(self.enable_button)
        if self.enable_key is not None:
            self.fig.canvas.mpl_disconnect(self.enable_key)

    # check attributes
    def _on_click_over_obj(self, event):
        # clear
        self.show_points(self.add_plot, [], [])

        if event.inaxes != self.axs[0] and (event.button in [1, 3]): return
        x = int(np.round(event.xdata))
        y = int(np.round(event.ydata))

        self.show_points(self.add_plot, [x], [y])
        self.obj_id = int(self.global_masks[y, x])
        if event.button == 1 and self.obj_id != 0:  # left click
            self.attr_update_func(str(self.data['objs'][self.obj_id - 1]['attrs']))
        else:
            self.obj_id = None
            self.attr_update_func("")

    def enable_click_obj(self):
        self.enable_click = self.fig.canvas.mpl_connect('button_press_event', self._on_click_over_obj)

    def disable_click_obj(self):
        self.show_points(self.add_plot, [], [])
        if self.enable_click is not None:
            self.fig.canvas.mpl_disconnect('button_press_event')

    # +/- labels
    def _click_label(self, event):
        if event.inaxes != self.axs[0] and (event.button in [1, 3]): return
        x = int(np.round(event.xdata))
        y = int(np.round(event.ydata))

        # (1) duplicate labels and (2) one object with +/- are not allowed
        obj_id = self.global_masks[y, x]
        if obj_id == 0:
            return

        if event.button == 1:
            if obj_id in self.negatives:
                self.negatives.pop(obj_id)
            self.positives[obj_id] = [x, y]
        else:  # right click
            if obj_id in self.positives:
                self.positives.pop(obj_id)
            self.negatives[obj_id] = [x, y]
        if len(self.positives) > 0:
            self.show_points(self.pos_plot, *zip(*self.positives.values()))
        else:
            self.show_points(self.pos_plot, [], [])
        if len(self.negatives) > 0:
            self.show_points(self.neg_plot, *zip(*self.negatives.values()))
        else:
            self.show_points(self.neg_plot, [], [])

    def enable_labels(self, drop_history=True):
        if drop_history:
            # remove +/- labels
            self.show_points(self.pos_plot, [], [])
            self.show_points(self.neg_plot, [], [])
            self.positives = {}
            self.negatives = {}
        self.enable_labels_handler = self.fig.canvas.mpl_connect('button_press_event', self._click_label)
        self.pos_coverage = self.neg_coverage = None

    def disable_labels(self):
        if self.enable_labels_handler is not None:
            self.fig.canvas.mpl_disconnect('button_press_event')

    # draw contours after synthesis
    def draw_contours_after_synthesis(self, pos, neg):
        self.contour_plot.set_data([], [])

        self.pos_contour_plots = []
        for idx in pos:
            xs, ys = zip(*self.data['objs'][idx]['polygons'])
            xs, ys = list(xs) + [np.nan], list(ys) + [np.nan]
            pos_contour_plot, = self.axs[0].plot([], [], color='green', linewidth=3)  # plot contours for - objs
            pos_contour_plot.set_data(xs, ys)
            self.pos_contour_plots.append(pos_contour_plot)

        self.neg_contour_plots = []
        for idx in neg:
            xs, ys = zip(*self.data['objs'][idx]['polygons'])
            xs, ys = list(xs) + [np.nan], list(ys) + [np.nan]
            neg_contour_plot, = self.axs[0].plot([], [], color='red', linewidth=3)  # plot contours for - objs
            neg_contour_plot.set_data(xs, ys)
            self.neg_contour_plots.append(neg_contour_plot)
        self.fig.canvas.draw()

    def pick_color(self):
        while True:
            color = tuple(np.random.randint(low=0, high=255, size=3).tolist())
            if color not in self.color_set:
                self.color_set.add(color)
                return color

    def _on_key(self, event):
        if event.key == 'z':
            self.undo()

        elif event.key == 'enter':
            self.new_tow()

        elif event.key == 'escape':  # save for notebooks
            self.get_segmented_objs()
            plt.close(self.fig)

    def _on_click(self, event):
        if event.inaxes != self.axs[0] and (event.button in [1, 3]): return
        x = int(np.round(event.xdata))
        y = int(np.round(event.ydata))

        if event.button == 1:  # left click
            self.trace.append(True)
            self.add_xs.append(x)
            self.add_ys.append(y)
            self.show_points(self.add_plot, self.add_xs, self.add_ys)

        else:  # right click
            self.trace.append(False)
            self.rem_xs.append(x)
            self.rem_ys.append(y)
            self.show_points(self.rem_plot, self.rem_xs, self.rem_ys)

        self.get_mask()

    def show_points(self, plot, xs, ys):
        plot.set_data(xs, ys)
        self.fig.canvas.draw()

    def clear_mask(self):
        self.contour_plot.set_data([], [])
        self.mask_data.fill(0)
        self.mask_plot.set_data(self.mask_data)
        self.fig.canvas.draw()

    def get_mask(self):
        # use SAM to segment
        mask, _, _ = self.predictor.predict(point_coords=np.array(list(zip(self.add_xs, self.add_ys)) +
                                                                  list(zip(self.rem_xs, self.rem_ys))),
                                            point_labels=np.array([1] * len(self.add_xs) + [0] * len(self.rem_xs)),
                                            multimask_output=False)
        mask = mask[0].astype(np.uint8)

        mask[self.global_masks > 0] = 0
        mask = self.remove_small_regions(mask, self.MIN_MASK_REGION_AREA, HOLES)
        mask = self.remove_small_regions(mask, self.MIN_MASK_REGION_AREA, ISLANDS)

        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        xs, ys = [], []
        for contour in contours:  # nan to disconnect contours
            xs.extend(contour[:, 0, 0].tolist() + [np.nan])
            ys.extend(contour[:, 0, 1].tolist() + [np.nan])
        self.contour_plot.set_data(xs, ys)

        self.mask_data[:, :, 3] = mask * self.opacity
        self.mask_plot.set_data(self.mask_data)
        self.fig.canvas.draw()

    def undo(self):
        if len(self.trace) == 0:  # undo last mask
            self.global_masks[self.last_mask] = 0
            self.prev_mask_data[:, :, 3][self.last_mask] = 0
            self.prev_mask_plot.set_data(self.prev_mask_data)
            self.label -= 1
            self.full_legend.pop()
            self.axs[0].legend(handles=self.full_legend, loc='center left', bbox_to_anchor=(1, 0.5), ncol=2)
            self.clear_mask()

        else:  # undo last point
            if self.trace[-1]:
                self.add_xs = self.add_xs[:-1]
                self.add_ys = self.add_ys[:-1]
                self.show_points(self.add_plot, self.add_xs, self.add_ys)
            else:
                self.rem_xs = self.rem_xs[:-1]
                self.rem_ys = self.rem_ys[:-1]
                self.show_points(self.rem_plot, self.rem_xs, self.rem_ys)

            self.trace.pop()

            if len(self.trace) != 0:
                self.get_mask()
            else:
                self.clear_mask()

    def new_tow(self):
        # clear points
        self.add_xs, self.add_ys, self.rem_xs, self.rem_ys, self.trace = [], [], [], [], []
        self.show_points(self.add_plot, self.add_xs, self.add_ys)
        self.show_points(self.rem_plot, self.rem_xs, self.rem_ys)

        mask = self.mask_data[:, :, 3] > 0
        self.global_masks[mask] = self.label
        self.last_mask = mask.copy()

        self.prev_mask_data[:, :, :3][mask] = self.current_color
        self.prev_mask_data[:, :, 3][mask] = 255
        self.prev_mask_plot.set_data(self.prev_mask_data)

        self.full_legend.append(Circle(1, color=np.array(self.current_color) / 255, label=f'{self.label}'))
        self.axs[0].legend(handles=self.full_legend, loc='center left', bbox_to_anchor=(1, 0.5), ncol=2)

        self.current_color = self.pick_color()
        self.label += 1

        for i in range(3):
            self.mask_data[:, :, i] = self.current_color[i]
        self.clear_mask()

    @staticmethod
    def remove_small_regions(mask, area_thresh, mode):
        # polish segmentation area
        """Function from https://github.com/facebookresearch/segment-anything/blob/main/segment_anything/utils/amg.py"""
        assert mode in [HOLES, ISLANDS]
        correct_holes = mode == HOLES
        working_mask = (correct_holes ^ mask).astype(np.uint8)
        n_labels, regions, stats, _ = cv2.connectedComponentsWithStats(working_mask, 8)
        sizes = stats[:, -1][1:]  # Row 0 is background label
        small_regions = [i + 1 for i, s in enumerate(sizes) if s < area_thresh]
        if len(small_regions) == 0:
            return mask
        fill_labels = [0] + small_regions
        if not correct_holes:
            fill_labels = [i for i in range(n_labels) if i not in fill_labels]
            # If every region is below threshold, keep largest
            if len(fill_labels) == 0:
                fill_labels = [int(np.argmax(sizes)) + 1]
        mask = np.isin(regions, fill_labels)
        return mask

    def get_segmented_objs(self):
        results = {}
        for idx in range(1, self.label):
            results[idx] = {'id': idx, 'size': list(self.img.shape[:2])}

            # masks
            bool_mask = self.global_masks == idx
            # # test mask
            # img = self.img.copy()
            # img[bool_mask, :] = 0
            # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # cv2.imshow("test", img)
            # cv2.waitKey(0)

            # bboxes
            x_min, y_min, x_max, y_max = map(int, sv.mask_to_xyxy(bool_mask[None, ...])[0])
            # xs, ys = np.where(bool_mask)
            # x_min, x_max, y_min, y_max = min(xs), max(xs), min(ys), max(ys)
            results[idx]['box'] = [x_min, y_min, x_max, y_max]
            # img = cv2.rectangle(self.img, (x_min, y_min), (x_max, y_max), color=(27, 158, 119), thickness=1)
            # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # cv2.imshow("test", img)
            # cv2.waitKey(0)

            # ploygons
            polygons, _ = cv2.findContours(bool_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            polygons = polygons[0][:, 0, :]
            results[idx]['polygons'] = [point.tolist() for point in polygons]
            # test ploygons
            # img = self.img.copy()
            # mask = sv.polygon_to_mask(polygons, self.img.shape[:2][::-1]).astype(np.bool_)
            # img[mask, :] = 0
            # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # cv2.imshow("test", img)
            # cv2.waitKey(0)

        with open(os.path.join(DIR, "tmp.jsonlines"), 'w') as writer:
            for line in results.values():
                print(json.dumps(line), file=writer)

        return results

    def plot_inpainting_image(self, img):
        # self.im = self.axs[1].imshow(img, cmap=mpl.cm.gray)
        self.axs[1].imshow(img, cmap=mpl.cm.gray)
        self.axs[1].axis('off')
        self.axs[1].title.set_text('Output image')
        box = self.axs[1].get_position()
        if self.axs1_fronze_box is None:
            self.axs1_fronze_box = [box.x0, box.y0, box.width * 0.8, box.height]
        self.axs[1].set_position(self.axs1_fronze_box)
        self.fig.canvas.draw()

    @staticmethod
    def encode_person_attrs(data, plattice=None):
        from order_theory.interval_lattice import IntervalLattice
        from order_theory.lazy_product_lattice import LazyProductLattice
        from order_theory.set_lattice import SetLattice

        def build_person_lattices(ages):
            lattices = {}
            lattices["Male"] = SetLattice.build("Male", [True, False])
            lattices["Age"] = IntervalLattice.build("Age", ages)
            lattices["Orientation"] = SetLattice.build("Orientation", ["Front", "Back", "Side"])
            lattices["Glasses"] = SetLattice.build("Glasses", [True, False])
            lattices["Hat"] = SetLattice.build("Hat", [True, False])
            lattices["HoldObjectsInFront"] = SetLattice.build("HoldObjectsInFront", [True, False])
            lattices["Bag"] = SetLattice.build("Bag", ["BackPack", "ShoulderBag", "HandBag", "NoBag"])
            lattices["TopStyle"] = SetLattice.build("TopStyle",
                                                    ["UpperStride", "UpperLogo", "UpperPlaid", "UpperSplice",
                                                     "NoTopStyle"])
            lattices["BottomStyle"] = SetLattice.build("BottomStyle",
                                                       ["BottomStripe", "BottomPattern", "NoBottomStyle"])
            lattices["UpperBody"] = SetLattice.build("UpperBody",
                                                     ["ShortSleeve", "LongSleeve", "LongCoat", "UnkUpperBody"])
            lattices["LowerBody"] = SetLattice.build("LowerBody", ["Trousers", "Shorts", "SkirtDress", "UnkLowerBody"])
            lattices["Boots"] = SetLattice.build("Boots", [True, False])
            product_lattice = LazyProductLattice(name="person", sublattices=list(lattices.values()))
            return product_lattice

        out = []
        ages = []
        for line in data:
            line["Age"] = int(line["Age"])
            ages.append(line["Age"])
            if line['ShortSleeve']:
                upperbody = 'ShortSleeve'
            elif line['LongSleeve']:
                upperbody = 'LongSleeve'
            elif line['LongCoat']:
                upperbody = 'LongCoat'
            else:
                upperbody = "UnkUpperBody"
            if line['Trousers']:
                lowerbody = 'Trousers'
            elif line['Shorts']:
                lowerbody = 'Shorts'
            elif line['SkirtDress']:
                lowerbody = 'SkirtDress'
            else:
                lowerbody = "UnkLowerBody"
            line = {
                "Male": line["Male"], "Age": [line["Age"], True, True, line["Age"]], "Orientation": line["Orientation"],
                "Glasses": line["Glasses"], "Hat": line["Hat"], "HoldObjectsInFront": line["HoldObjectsInFront"],
                "Bag": line["Bag"], "TopStyle": line["TopStyle"], "BottomStyle": line["BottomStyle"],
                "UpperBody": [upperbody], "LowerBody": [lowerbody], "Boots": line["Boots"],
            }
            out.append(line)
        ages = sorted(set(ages + [0, 100]))
        if plattice is None:
            build_start_time = time.time()
            plattice = build_person_lattices(ages)
            build_time = time.time() - build_start_time
        else:
            build_time = 0
        for idx, line in enumerate(out):
            out[idx] = tuple(sub_l.encode(value) for sub_l, value in zip(plattice.sublattices, line.values()))
        return out, plattice, round(build_time, 2)


if __name__ == '__main__':
    img_file = os.path.join(DIR, "demo1.jpg")
    segmenter = Segmentor()
    segmenter.load_file(img_file)
    segmenter.enable_interaction()
    plt.show(block=True)
