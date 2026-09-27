"""Parse the raw conversation logs into one row per trial.

Works directly on data/<model>.json rather than data/results.csv. Feedback
messages, their labels and stages are defined once in common.py.

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

from common import (
    CATEGORIES,
    CATEGORY_RENAME,
    DATA_DIR,
    MAX_ROUNDS,
    PROMPT_CLASSIFICATION_CSV,
    STAGE_BY_LABEL,
    SUCCESS,
    UNIT_TEST_FAILED,
    classify_feedback,
)


def build_trials(strict_rounds=True):
    """Return a DataFrame with one row per (model, task, repetition) trial.

    ``strict_rounds`` restricts Level-1/Level-2 success to the first
    ``MAX_ROUNDS`` feedback rounds (n = 0..5), matching the experimental design.
    """
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
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
                    label = classify_feedback(msg["content"])
                    if label is not None:
                        events.append(label)

                n_gen = sum(1 for m in conversation if m["role"] == "assistant")

                try:
                    s_round = events.index(SUCCESS)
                except ValueError:
                    s_round = np.nan

                if np.isnan(s_round):
                    l1_round = np.nan
                elif UNIT_TEST_FAILED in events[:int(s_round)]:
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
                    "final_stage": STAGE_BY_LABEL.get(final, "class"),
                })

    df = pd.DataFrame(rows)

    cls = pd.read_csv(PROMPT_CLASSIFICATION_CSV, sep=";")
    cls["Prompt"] = cls[cls.columns[0]].astype(str)
    cls = cls.rename(columns=CATEGORY_RENAME)
    cat_cols = CATEGORIES
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
