import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from plot_style import COLORS, apply_plot_style

apply_plot_style()

DESIRED_ORDER = [
    "llama-3.3-70b-instruct",
    "codestral-22b",
    "qwen2.5-coder-32b-instruct",
    "qwen3-coder",
    "gpt-oss_20b",
    "gpt-oss_120b",
    "gpt-5-2025-08-07",
    "claude-sonnet-4-20250514",
]

OUTCOME_COLORS = {
    "Class Creation Error": COLORS[0],
    "Syntax Error":         COLORS[2],
    "Semantic Error":       COLORS[4],
    "Success":              COLORS[6],
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
    if last_feedback == "unit tests were successful":
        return "Success"

    if last_feedback == "class could not be created":
        return "Class Creation Error"
    if last_feedback == "syntax check failed":
        return "Syntax Error"
    if last_feedback == "unit test failed":
        return "Semantic Error"

    # No feedback at all → treat as class-creation failure (generation failed immediately)
    return "Class Creation Error"


def get_outcome_distribution(file_path):
    df = pd.read_csv(file_path, sep=";")
    feedback_cols = [c for c in df.columns if c.startswith("Feedback_Round_")]

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
    model_order = [m for m in DESIRED_ORDER if m in available]
    model_order += [m for m in available if m not in model_order]
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
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylabel("Share of Attempts")
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_ylim(0, 100)
    ax.set_title("Outcome Distribution per Model\n(Class Creation Errors, Syntax Errors, Semantic Errors, Successes)")
    ax.legend(title="Outcome", bbox_to_anchor=(0.5, 1.08), loc="lower center", ncol=4)

    plt.tight_layout()
    output_file = "../plots/outcome_distribution_by_model.png"
    plt.savefig(output_file, bbox_inches="tight")
    print(f"Plot saved to {output_file}")


if __name__ == "__main__":
    pct, totals = get_outcome_distribution("../data/results.csv")
    print(pct.to_string())
    plot_stacked_outcomes(pct, totals)
