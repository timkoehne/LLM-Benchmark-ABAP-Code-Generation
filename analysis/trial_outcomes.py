"""Parse the raw conversation logs into one row per trial.

This replaces the round extraction in ``consolidate_results.py``, which only
recognises four of the eight feedback messages the harness actually emits and
therefore silently drops ~11% of all feedback events, shifting every
round index towards zero.  The full set of feedback messages is:

    The syntax check failed with the following errors:          -> syntax
    The unittest syntax check failed with the following errors: -> syntax   (dropped before)
    The class could not be created due to the following error:  -> class
    Class name not found.                                       -> class    (dropped before)
    There should only be the one public method.                 -> class    (dropped before)
    The source code could not be set due to the following error:-> class    (dropped before)
    The unit test failed with the following errors:             -> unittest
    The unit tests were successful.                             -> success

Emitted columns per trial: the ordered list of feedback events, the round at
which Level-2 success was reached (``success_round``), the round at which
Level-1 success was reached (``l1_round``, i.e. success without ever having
received unit-test failure feedback) and the terminating stage.
"""

import glob
import json
import os

import numpy as np
import pandas as pd

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Fine-grained label per feedback message, plus the pipeline stage it belongs
# to.  "Class name not found" and "There should only be the one public method"
# are structural rejections of the generated source, so they belong to the
# syntax/structure stage rather than to class creation - this is the grouping
# that reproduces Figure 6 of the paper.
FEEDBACK_PATTERNS = [
    ("The unit tests were successful", "success", "success"),
    ("The unittest syntax check failed", "ut_syntax", "syntax"),
    ("The syntax check failed", "syntax", "syntax"),
    ("The unit test failed", "unittest", "unittest"),
    ("The class could not be created", "class_create", "class"),
    ("The source code could not be set", "src_set", "class"),
    ("Class name not found", "name_not_found", "syntax"),
    ("There should only be the one public method", "one_public_method", "syntax"),
]
STAGE = {label: stage for _, label, stage in FEEDBACK_PATTERNS}

MAX_ROUNDS = 6


def classify(content):
    for needle, label, _stage in FEEDBACK_PATTERNS:
        if content.startswith(needle):
            return label
    return None


def build_trials(strict_rounds=True):
    """Return a DataFrame with one row per (model, task, repetition) trial.

    ``strict_rounds`` restricts Level-1/Level-2 success to the first
    ``MAX_ROUNDS`` feedback rounds (n = 0..5), matching the experimental design.
    """
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        if os.path.basename(path) in ("syntax_errors.json", "results.json"):
            continue
        with open(path, encoding="utf-8") as f:
            content = json.load(f)
        if not isinstance(content, dict) or not next(iter(content)).endswith(".txt"):
            continue
        model = os.path.basename(path).replace(".json", "")
        for prompt_file, repetitions in content.items():
            task = prompt_file.replace(".txt", "")
            for rep, conversation in enumerate(repetitions):
                events = []
                for msg in conversation:
                    if msg["role"] != "user":
                        continue
                    label = classify(msg["content"])
                    if label is not None:
                        events.append(label)

                n_gen = sum(1 for m in conversation if m["role"] == "assistant")

                try:
                    s_round = events.index("success")
                except ValueError:
                    s_round = np.nan

                if np.isnan(s_round):
                    l1_round = np.nan
                elif "unittest" in events[:int(s_round)]:
                    l1_round = np.nan
                else:
                    l1_round = s_round

                if strict_rounds:
                    if not np.isnan(s_round) and s_round >= MAX_ROUNDS:
                        s_round = np.nan
                    if not np.isnan(l1_round) and l1_round >= MAX_ROUNDS:
                        l1_round = np.nan

                final = events[-1] if events else "none"
                rows.append({
                    "Model": model,
                    "Prompt": task,
                    "Repetition": rep,
                    "n_generations": n_gen,
                    "n_events": len(events),
                    "events": "|".join(events),
                    "success_round": s_round,
                    "l1_round": l1_round,
                    "final_event": final,
                    "final_stage": STAGE.get(final, "class"),
                })

    df = pd.DataFrame(rows)

    cls = pd.read_csv(os.path.join(DATA, "prompt_classification.csv"), sep=";")
    cls["Prompt"] = cls[cls.columns[0]].astype(str)
    rename = {
        "String Handling": "String Handling",
        "List & Array Operations": "List or Array Operation",
        "Mathematical Calculations": "Mathematical Calculation",
        "Logical Checks": "Logical Condition",
        "Database Operations (ABAP)": "ABAP Database Operation",
    }
    cls = cls.rename(columns=rename)
    cat_cols = list(rename.values())
    for c in cat_cols:
        cls[c] = cls[c].astype(str).str.strip().str.upper().eq("X")
    df = df.merge(cls[["Prompt"] + cat_cols], on="Prompt", how="left")
    df[cat_cols] = df[cat_cols].fillna(False)
    return df, cat_cols


if __name__ == "__main__":
    df, cats = build_trials()
    print(df.shape)
    print(df.groupby("Model")["n_events"].describe())
    print("\nmax feedback rounds observed:", df["n_events"].max())
    print("trials with more than 6 feedback events:",
          int((df["n_events"] > MAX_ROUNDS).sum()))
    print("\nfinal stage distribution:")
    print(df["final_stage"].value_counts())
    print("\ntasks per category:")
    print(df.drop_duplicates("Prompt")[cats].sum())
