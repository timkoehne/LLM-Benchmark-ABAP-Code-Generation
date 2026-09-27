import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from common import MODEL_ABBREVIATIONS, PLOTS_DIR, SYNTAX_ERRORS_JSON, order_models
from plot_style import COLORS, apply_plot_style, wilson_halfwidths

apply_plot_style()

def visualize_syntax_errors(json_path=SYNTAX_ERRORS_JSON):
    with open(json_path, 'r') as f:
        raw_data = json.load(f)
    
    data = {}
    total_counts = {}
    
    for model, categories in raw_data.items():
        data[model] = {}
        model_total = 0
        for category, patterns in categories.items():
            cat_count = 0
            for pattern, occurrences in patterns.items():
                cat_count += len(occurrences)
            data[model][category] = cat_count
            model_total += cat_count
        total_counts[model] = model_total

    df = pd.DataFrame(data).T.fillna(0)
    
    relative_df = df.div(df.sum(axis=1), axis=0).fillna(0)
    
    available_models = df.index.tolist()
    model_order = order_models(available_models)
    
    df = df.reindex(model_order)
    relative_df = relative_df.reindex(model_order)

    error_types = df.columns.tolist()
    models = df.index.tolist()
    num_models = len(models)
    num_error_types = len(error_types)
    bar_width = 0.15
    x = np.arange(num_models)

    fig, ax = plt.subplots(figsize=(14, 10))

    for idx, etype in enumerate(error_types):
        error_props = relative_df[etype].values
        
        # 95% Wilson score half-widths; wilson_halfwidths works in percentage
        # points, while relative_df holds proportions, so scale in and back out.
        errors = wilson_halfwidths(
            error_props * 100,
            [total_counts.get(m, 0) for m in models],
        ) / 100

        bar_positions = x + (idx - (num_error_types - 1) / 2) * bar_width
        
        ax.bar(
            bar_positions,
            error_props,
            width=bar_width,
            label=etype,
            color=COLORS[(idx + 1) % len(COLORS)],
            yerr=errors,
            capsize=3,
            error_kw={'elinewidth': 1, 'alpha': 0.7}
        )

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_ABBREVIATIONS.get(m, m) for m in models], rotation=15, ha="right")
    ax.set_xlabel("Models")
    ax.set_ylabel("Percentage of Errors")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(title="Error Category", bbox_to_anchor=(0.5, 1.08), loc='lower center', ncol=3)

    plt.tight_layout()
    output_path = os.path.join(PLOTS_DIR, 'syntax_error_types_by_model.png')
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")
    print("\nModel Order used:", model_order)

if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = SYNTAX_ERRORS_JSON
    visualize_syntax_errors(json_path)