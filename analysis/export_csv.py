"""
Export raw diagram data to wide-format CSV files.

Outputs:
  data/export_success_distribution.csv   – histogram bin counts per model
  data/export_success_by_category.csv    – success counts per model × category
  data/export_success_by_round.csv       – cumulative success counts per model × feedback round
"""

import pandas as pd
import numpy as np
import os
from common import DATA_DIR, FEEDBACK_COLS, MAX_ROUNDS, RESULTS_CSV, ROUND_LABELS, SUCCESS, order_models

FILE_PATH = RESULTS_CSV
OUT_DIR   = DATA_DIR


def load_df(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=';')
    df['Success_Bool'] = df['Success'].astype(str) == 'True'
    return df


def ordered_models(df: pd.DataFrame) -> list:
    models = df['Model'].unique()
    models = [m for m in models if 'codestral' not in m.lower()]
    return order_models(models)


# ---------------------------------------------------------------------------
# 1. success_distribution – histogram bin counts  (wide: one row per model)
# ---------------------------------------------------------------------------

def export_success_distribution(df: pd.DataFrame, out_path: str):
    target_models = ['gpt-5-2025-08-07', 'claude-sonnet-4-20250514']
    bins   = [-0.01, 0.1001, 0.2001, 0.3001, 0.4001, 0.5001,
               0.6001, 0.7001, 0.8001, 0.9001, 1.01]
    labels = ["0-10%", "11-20%", "21-30%", "31-40%", "41-50%",
              "51-60%", "61-70%", "71-80%", "81-90%", "91-100%"]

    rows = []
    for model in target_models:
        model_df = df[df['Model'] == model]
        if model_df.empty:
            print(f"Warning: no data for {model}")
            continue

        task_success = model_df.groupby('Prompt')['Success_Bool'].mean()
        total        = len(task_success)
        counts, _    = np.histogram(task_success, bins=bins)

        row = {'Model': model}
        for label, count in zip(labels, counts):
            row[label] = int(count)
        row['Total'] = total
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(out_path, index=False)
    print(f"Saved {out_path}")


# ---------------------------------------------------------------------------
# 2. plot_success_by_category – success counts  (wide: one row per model)
# ---------------------------------------------------------------------------

def export_success_by_category(df: pd.DataFrame, out_path: str):
    models = ordered_models(df)
    categories = [
        'String Handling',
        'List or Array Operation',
        'Mathematical Calculation',
        'Logical Condition',
        'ABAP Database Operation',
    ]

    rows = []
    totals_row = {'Model': 'Tasks in Category'}

    for model in models:
        row = {'Model': model}

        for category in categories:
            if category not in df.columns:
                row[category] = 0
                continue

            subset = df[(df['Model'] == model) & (df[category].astype(str) == 'True')]
            totals_row[category] = len(subset)  # same total per category regardless of model

            success_count = 0
            for _, r in subset.iterrows():
                is_success = str(r['Success']) == 'True'
                if not is_success:
                    for col in FEEDBACK_COLS:
                        content = r[col]
                        if pd.isna(content) or content == '':
                            continue
                        if SUCCESS in str(content):
                            is_success = True
                            break
                if is_success:
                    success_count += 1

            row[category] = success_count

        rows.append(row)

    rows.append(totals_row)

    out = pd.DataFrame(rows)
    out.to_csv(out_path, index=False)
    print(f"Saved {out_path}")


# ---------------------------------------------------------------------------
# 3. plot_success_by_round – cumulative success counts  (wide: one row per model)
# ---------------------------------------------------------------------------

def export_success_by_round(df: pd.DataFrame, out_path: str):
    models = ordered_models(df)

    rows = []
    for model in models:
        model_df = df[df['Model'] == model]
        total    = len(model_df)

        row = {'Model': model}
        for r in range(MAX_ROUNDS):
            success_count = 0
            for _, entry in model_df.iterrows():
                is_success = str(entry['Success']) == 'True'
                duration   = 0

                rounds_content = [entry[col] for col in FEEDBACK_COLS]
                found_string   = False
                for idx, content in enumerate(rounds_content):
                    if pd.isna(content) or content == '':
                        break
                    duration = idx
                    if SUCCESS in str(content):
                        found_string = True
                        break

                if found_string:
                    is_success = True

                if is_success and duration <= r:
                    success_count += 1

            row[ROUND_LABELS[r]] = success_count

        row['Total'] = total
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(out_path, index=False)
    print(f"Saved {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    df = load_df(FILE_PATH)

    export_success_distribution(
        df, os.path.join(OUT_DIR, 'export_success_distribution.csv'))
    export_success_by_category(
        df, os.path.join(OUT_DIR, 'export_success_by_category.csv'))
    export_success_by_round(
        df, os.path.join(OUT_DIR, 'export_success_by_round.csv'))
