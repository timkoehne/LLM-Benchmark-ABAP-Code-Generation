import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from typing import Dict, List
from plot_style import COLORS, apply_plot_style, MODEL_ABBREVIATIONS

apply_plot_style()

# One key per feedback status written by consolidate_results.py.  The previous
# version tested for substrings that never appeared ("syntax error in unit
# test") and double-counted others, so four of the eight statuses were missed.
ERROR_KEY_BY_STATUS = {
    "class could not be created": "class_creation_errors",
    "source code could not be set": "source_code_errors",
    "syntax check failed": "syntax_errors",
    "unittest syntax check failed": "unittest_syntax_errors",
    "class name not found": "class_name_errors",
    "not one public method": "public_method_errors",
    "unit test failed": "unit_test_failures",
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
        
        errors = {k: 0 for k in ERROR_KEY_BY_STATUS.values()}

        feedback_cols = [c for c in df.columns if 'Feedback_Round' in c]

        for _, row in model_df.iterrows():
            for col in feedback_cols:
                val = row[col]
                if pd.isna(val) or val == '':
                    continue

                key = ERROR_KEY_BY_STATUS.get(str(val).strip().lower())
                if key is not None:
                    errors[key] += 1

        summary[model] = errors
        
    return summary

def visualize_combined_summary_errors(summary: dict):
    combined_summary = {}
    combined_counts = {}
    
    for model, errors in summary.items():
        # Same grouping as Figure 6: "class name not found" and "not one public
        # method" reject the generated source, so they are syntax-stage
        # failures; a failing unit-test syntax check is also a syntax failure,
        # not a semantic one - the tests never ran.
        combined = {
            "class_creation_errors": errors.get("class_creation_errors", 0)
            + errors.get("source_code_errors", 0),
            "syntax_errors": errors.get("syntax_errors", 0)
            + errors.get("unittest_syntax_errors", 0)
            + errors.get("class_name_errors", 0)
            + errors.get("public_method_errors", 0),
            "unit_test_errors": errors.get("unit_test_failures", 0),
        }
        
        total_errors = sum(combined.values())
        combined_counts[model] = { 'counts': combined, 'total': total_errors }
        
        if total_errors > 0:
            combined_summary[model] = {k: v / total_errors for k, v in combined.items()}
        else:
            combined_summary[model] = {k: 0 for k in combined.keys()}

    df = pd.DataFrame(combined_summary).T 
    df = df[["class_creation_errors", "syntax_errors", "unit_test_errors"]]

    available_models = df.index.tolist()
    
    desired_order = [
         "llama-3.3-70b-instruct",
        "codestral-22b",
        "qwen2.5-coder-32b-instruct",
        "qwen3-coder",
        "gpt-oss_20b",
        "gpt-oss_120b",
        "gpt-5-2025-08-07",
        "claude-sonnet-4-20250514"
    ]
    model_order = [m for m in desired_order if m in available_models]
    remaining = [m for m in available_models if m not in model_order]
    model_order.extend(remaining)
    
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
        
        errors = []
        
        for model in models:
            p = combined_summary[model][etype]
            n = combined_counts[model]['total']
            
            if n > 0:
                se = np.sqrt(p * (1 - p) / n)
                margin = 1.96 * se
            else:
                margin = 0
            errors.append(margin)

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
    ax.set_title("Relative Distribution of Errors by Model (with 95% CIs)")
    ax.legend(title="Error Type", bbox_to_anchor=(0.5, 1.08), loc='lower center', ncol=3)

    plt.tight_layout()
    output_file = '../plots/error_categories_by_model.png'
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")
    # plt.show()

if __name__ == "__main__":
    summary = get_error_summary_from_csv('../data/results.csv')
    if summary:
        visualize_combined_summary_errors(summary)