import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from common import FEEDBACK_COLS, MODEL_ABBREVIATIONS, PLOTS_DIR, RESULTS_CSV, STAGE_BY_LABEL, order_models
from plot_style import COLORS, apply_plot_style

apply_plot_style()


OUTCOME_COLORS = {
    "Class Creation Error": COLORS[0],
    "Syntax Error":         COLORS[2],
    "Semantic Error":       COLORS[4],
    "Success":              COLORS[6],
}


# Display name of the pipeline stage an attempt terminated in (stages are
# defined in common.py).
OUTCOME_BY_STAGE = {
    "success": "Success",
    "syntax": "Syntax Error",
    "unittest": "Semantic Error",
    "class": "Class Creation Error",
}


def get_final_outcome(row, feedback_cols):
    """Return the final outcome category for a single attempt."""
    # Walk through rounds and remember the last non-empty feedback
    last_feedback = None
    for col in feedback_cols:
        val = row[col]
        if pd.isna(val) or str(val).strip() == "":
            break
        last_feedback = str(val).strip()

    # Explicit success flag or successful unit-test message
    if row["Success"] is True or str(row["Success"]) == "True":
        return "Success"

    # No feedback at all → treat as class-creation failure (generation failed immediately)
    return OUTCOME_BY_STAGE[STAGE_BY_LABEL.get(last_feedback, "class")]


def get_outcome_distribution(file_path):
    df = pd.read_csv(file_path, sep=";")
    feedback_cols = FEEDBACK_COLS

    records = []
    for _, row in df.iterrows():
        outcome = get_final_outcome(row, feedback_cols)
        records.append({"Model": row["Model"], "Outcome": outcome})

    outcomes_df = pd.DataFrame(records)
    counts = outcomes_df.groupby(["Model", "Outcome"]).size().unstack(fill_value=0)

    # Ensure all outcome columns are present
    for col in OUTCOME_COLORS:
        if col not in counts.columns:
            counts[col] = 0

    counts = counts[list(OUTCOME_COLORS.keys())]

    # Order models
    available = counts.index.tolist()
    model_order = order_models(available)
    counts = counts.reindex(model_order)

    # Convert to percentages
    totals = counts.sum(axis=1)
    pct = counts.div(totals, axis=0) * 100

    return pct, totals


def plot_stacked_outcomes(pct, totals):
    models = pct.index.tolist()
    categories = list(OUTCOME_COLORS.keys())
    colors = list(OUTCOME_COLORS.values())

    _, ax = plt.subplots(figsize=(13, 7))
    x = np.arange(len(models))
    bar_width = 0.55

    # Use white text on dark segments, dark text on light segments
    light_cats = {"Class Creation Error", "Syntax Error"}

    bottoms = np.zeros(len(models))
    for cat, color in zip(categories, colors):
        vals = pct[cat].values
        bars = ax.bar(x, vals, width=bar_width, bottom=bottoms, label=cat, color=color)
        text_color = "#333333" if cat in light_cats else "white"
        for i, (bar, val) in enumerate(zip(bars, vals)):
            if val >= 4:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bottoms[i] + val / 2,
                    f"{val:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color=text_color,
                )
        bottoms += vals

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_ABBREVIATIONS.get(m, m) for m in models], rotation=15, ha="right")
    ax.set_ylabel("Share of Attempts")
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_ylim(0, 100)
    ax.legend(title="Outcome", bbox_to_anchor=(0.5, 1.08), loc="lower center", ncol=4)

    plt.tight_layout()
    output_file = os.path.join(PLOTS_DIR, "outcome_distribution_by_model.png")
    plt.savefig(output_file, bbox_inches="tight")
    print(f"Plot saved to {output_file}")


if __name__ == "__main__":
    pct, totals = get_outcome_distribution(RESULTS_CSV)
    print(pct.to_string())
    plot_stacked_outcomes(pct, totals)
