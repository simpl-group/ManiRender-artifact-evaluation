# -*- coding:utf-8 -*-

import os
import json
from constants import (
    DATASET_DIR, PROJECT_DIR,
    TEXT, VEHICLE, PERSON,
)
import glob
from openai import OpenAI
import base64
import requests
import random
from datetime import datetime
import re
from collections import defaultdict
import itertools
import time

# "%Y-%m-%d_%H:%M:%S"
# LOG_FILEHEAD = os.path.join(os.path.dirname(__file__), 'logs', f'{datetime.now().strftime("%Y-%m-%d")}')
LOG_FILEHEAD = os.path.join(os.path.dirname(__file__), 'logs', '2024-10-21')

# https://platform.openai.com/usage
OPENAI_KEY = ""
assert len(OPENAI_KEY) > 0, ValueError("Please set your OpenAI Key.")
GPT4O = "gpt-4o-2024-08-06"  # 30,000 TPM
# GPT4O = "gpt-4o-mini-2024-07-18"  # 200,000 TPM
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_KEY}"
}

get_file_index = lambda x: int(os.path.basename(x)[:-4])


def jpg2base64(file):
    with open(file, 'rb') as reader:
        return base64.b64encode(reader.read()).decode('utf-8')


def finetune(train_xs, train_ys, test_xs, log_file,
             shuffle_train=False, shuffle_test=False, model=GPT4O, MAX_TOKENS=300) -> dict:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if shuffle_train:
        indices = list(range(len(train_xs)))
        random.shuffle(indices)
        train_xs = [train_xs[idx] for idx in indices]
        train_ys = [train_ys[idx] for idx in indices]

    train_xs_base64 = list(map(jpg2base64, train_xs))
    train_inputs = []
    for file, gt in zip(train_xs_base64, train_ys):
        train_inputs += [
            {"role": "user", "content": [
                {"type": "text", "text": "Is this object positive or negative?"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{file}"}},
            ]},
            {"role": "assistant", "content": gt},
        ]

    if shuffle_test:
        indices = list(range(len(test_xs)))
        random.shuffle(indices)
        test_xs = [test_xs[idx] for idx in indices]

    test_xs_base64 = list(map(jpg2base64, test_xs))
    test_inputs = {"role": "user", "content": [
        {
            "type": "text",
            "text": f"Are these objects positive or negative? Answer only `positive` or `negative` for each of them. Given there are {len(test_xs)} images, you should return {len(test_xs)} `positive` or `negative`'s."
        }
    ]}
    for file in test_xs_base64:
        test_inputs["content"] += [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{file}"}
            }
        ]

    payload = {
        "model": model,
        "messages": [
            {"role": "system",
             "content": "You are a binary classify which only answers `positive` or `negative` for an image object."},
            *train_inputs,
            test_inputs,
        ],
        "max_tokens": MAX_TOKENS,
        "n": 10,
    }

    if os.path.exists(log_file):
        with open(log_file, 'r') as reader:
            response = json.load(reader)
    else:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=HEADERS, json=payload)
        response = response.json()
        with open(log_file, 'w') as writer:
            json.dump(response, fp=writer)
        time.sleep(100)  # to avoid reach the GPT TPM

    def eval_answers(answers):
        out = []
        for idx, prediction in enumerate(answers):
            items = re.split(r'[,\n]', prediction['message']['content'])
            items = [item.strip() for item in items if item.strip()]
            items = [1 if item == 'positive' else 0 for item in items][:len(test_xs)]
            items += [0 for _ in range(len(test_xs) - len(items))]  # the default prediction is negative
            if len(items) != len(test_xs):
                continue
            if shuffle_test:
                unshuffle = [None] * len(items)
                for src, dst in enumerate(indices):
                    unshuffle[dst] = items[src]
                items = unshuffle
            # prediction['message']['content'] = items
            out.append(items)
        return out

    predictions = eval_answers(response['choices'])
    return predictions


if __name__ == '__main__':
    eval_flag = True
    if eval_flag:
        outfile = os.path.join(DATASET_DIR, "results.gpt4o")
        writer = open(outfile, 'w')

    for idx in map(str, range(1, 21)):
        task_file = os.path.join(DATASET_DIR, idx, f"image{idx}.tasks")
        images = glob.glob(os.path.join(DATASET_DIR, idx, ".sobjs", "*", "*.jpg"))
        images = {get_file_index(img): img for img in images}

        obj_file = os.path.join(DATASET_DIR, idx, f"image{idx}.objs")
        idx2cls, cls2ids = {}, defaultdict(set)
        with open(obj_file, 'r') as reader:
            for line in map(json.loads, reader):
                idx2cls[line["id"]] = line["cls"]
                cls2ids[line["cls"]].add(line["id"])

        with open(task_file, 'r') as reader:
            for task_id, task in enumerate(map(json.loads, reader), start=1):
                print(f"file: {idx}, task: {task_id}")
                # train
                train_xs = [images[i] for i in task["positive"] + task["negative"]]
                train_ys = ["positive"] * len(task["positive"]) + ["negative"] * len(task["negative"])
                train_cls = {idx2cls[i] for i in task["positive"] + task["negative"]}
                # test
                test_ids = sorted(itertools.chain(*[list(cls2ids[cls]) for cls in train_cls]))
                test_xs = [images[i] for i in test_ids]
                test_ys = [1 if i in set(task["groundtruth"]) else 0 for i in test_ids]
                # finetune
                test_ys_preds = finetune(train_xs, train_ys, test_xs, log_file=f"{LOG_FILEHEAD}_{idx}_{task_id}.log")
                # eval
                if eval_flag:
                    # use with the most votes
                    test_ys_hat = []
                    deterministic = True  # with different predications every time
                    for i in range(len(test_ys)):
                        preds = [candidate[i] for candidate in test_ys_preds]
                        # >= 50% predications are positive then GPT4 thinks its positive
                        pred = int(sum(preds) / len(test_ys_preds) >= 0.5)
                        test_ys_hat.append(pred)
                        deterministic = deterministic and all(p == preds[0] for p in preds)
                    # predicate any positive/negative input as negative/positive
                    consistent = all(test_ys_hat[test_ids.index(pos)] == 1 for pos in task["positive"]) and \
                                 all(test_ys_hat[test_ids.index(neg)] == 0 for neg in task["negative"])
                    coverage = {i for i, pred in enumerate(test_ys_hat, start=1) if pred}
                    groundtruth = set(task["groundtruth"])
                    correct = sorted(coverage & groundtruth)
                    wrong = sorted(coverage - groundtruth)
                    log = {
                        "file": task_file[len(PROJECT_DIR) + 1:], **task,
                        "classes": list(train_cls),
                        "choices": test_ys_preds,
                        "prediction": test_ys_hat,
                        "correct": correct,
                        "wrong": wrong,
                        "#correct": len(correct),
                        "#wrong": len(wrong),
                        "#groundtruth": len(task['groundtruth']),
                        "consistent": consistent,
                        "deterministic": deterministic,
                    }
                    print(json.dumps(log, ensure_ascii=False), file=writer)

    if eval_flag:
        writer.close()
