import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from typing import Dict, List
from common import FEEDBACK_COLS, MODEL_ABBREVIATIONS, PLOTS_DIR, RESULTS_CSV, STAGE_BY_LABEL, order_models
from plot_style import COLORS, apply_plot_style, wilson_halfwidths

apply_plot_style()

# Every failed feedback event is counted under the pipeline stage it belongs
# to (stages are defined in common.py, the same grouping as Figure 6).
ERROR_KEY_BY_STAGE = {
    "class": "class_creation_errors",
    "syntax": "syntax_errors",
    "unittest": "unit_test_errors",
}


def get_error_summary_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

    models = df['Model'].unique()
    
    summary = {}

    for model in models:
        model_df = df[df['Model'] == model]
        
        errors = {k: 0 for k in ERROR_KEY_BY_STAGE.values()}

        for _, row in model_df.iterrows():
            for col in FEEDBACK_COLS:
                val = row[col]
                if pd.isna(val) or val == '':
                    continue

                stage = STAGE_BY_LABEL.get(str(val).strip().lower())
                key = ERROR_KEY_BY_STAGE.get(stage)
                if key is not None:
                    errors[key] += 1

        summary[model] = errors
        
    return summary

def visualize_combined_summary_errors(summary: dict):
    combined_summary = {}
    combined_counts = {}
    
    for model, combined in summary.items():
        total_errors = sum(combined.values())
        combined_counts[model] = { 'counts': combined, 'total': total_errors }
        
        if total_errors > 0:
            combined_summary[model] = {k: v / total_errors for k, v in combined.items()}
        else:
            combined_summary[model] = {k: 0 for k in combined.keys()}

    df = pd.DataFrame(combined_summary).T 
    df = df[["class_creation_errors", "syntax_errors", "unit_test_errors"]]

    available_models = df.index.tolist()
    
    model_order = order_models(available_models)
    
    df = df.reindex(model_order)

    error_types = df.columns.tolist()
    models = df.index.tolist()
    num_models = len(models)
    num_error_types = len(error_types)
    bar_width = 0.2
    x = np.arange(num_models)

    fig, ax = plt.subplots(figsize=(12, 6))

    for idx, etype in enumerate(error_types):
        error_props = df[etype].values
        
        errors = wilson_halfwidths(
            [combined_summary[m][etype] * 100 for m in models],
            [combined_counts[m]['total'] for m in models],
        ) / 100.0

        bar_positions = x + (idx - (num_error_types - 1) / 2) * bar_width
        ax.bar(
            bar_positions,
            error_props,
            width=bar_width,
            label=etype.replace("_", " ").title(),
            color=COLORS[(idx * 3) % len(COLORS)],
            yerr=errors,
            capsize=3,
            error_kw={'elinewidth': 1, 'alpha': 0.7}
        )

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_ABBREVIATIONS.get(m, m) for m in models], rotation=15, ha="right")
    ax.set_xlabel("Models")
    ax.set_ylabel("Percentage of Errors")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(title="Error Type", bbox_to_anchor=(0.5, 1.08), loc='lower center', ncol=3)

    plt.tight_layout()
    output_file = os.path.join(PLOTS_DIR, 'error_categories_by_model.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")
    # plt.show()

if __name__ == "__main__":
    summary = get_error_summary_from_csv(RESULTS_CSV)
    if summary:
        visualize_combined_summary_errors(summary)