import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from typing import Dict, List
from common import FEEDBACK_COLS, MAX_ROUNDS, ROUND_LABELS, MODEL_ABBREVIATIONS, PLOTS_DIR, RESULTS_CSV, SUCCESS, order_models
from plot_style import COLORS, apply_plot_style, wilson_halfwidths

apply_plot_style()

def get_model_data_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None, None

    models = df['Model'].unique()
    models = [m for m in models if 'codestral' not in m.lower()]
    
    models = order_models(models)

    
    model_data = {}
    sample_counts = {}

    for model in models:
        model_df = df[df['Model'] == model]
        total_samples = len(model_df)
        sample_counts[model] = total_samples
        
        cumulative_success = []
        
        for r in range(MAX_ROUNDS):
            success_count = 0
            for _, row in model_df.iterrows():
                is_success = False
                duration = 0
                
                if str(row['Success']) == 'True':
                     is_success = True
                
                rounds_content = [row[col] for col in FEEDBACK_COLS]
                found_string = False
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
            
            cumulative_success.append((success_count / total_samples) * 100)
            
        model_data[model] = cumulative_success
        
    return model_data, sample_counts

def visualize_success_by_llm(model_data: Dict[str, List[float]], sample_counts: Dict[str, int] = None):
    models = list(model_data.keys())
    rounds = list(range(MAX_ROUNDS))
    bar_width = 0.13
    x = np.arange(len(models))

    fig, ax = plt.subplots(figsize=(12, 7))


    for i in rounds:
        round_values = [model_data[model][i] for model in models]
        
        if sample_counts:
            errors = wilson_halfwidths(
                [model_data[m][i] for m in models],
                [sample_counts.get(m, 0) for m in models],
            )
        else:
            errors = None
            
        bar_positions = x + (i - (MAX_ROUNDS - 1) / 2) * bar_width
        ax.bar(
            bar_positions,
            round_values,
            width=bar_width,
            label=ROUND_LABELS[i],
            color=COLORS[i % len(COLORS)],
            yerr=errors if sample_counts else None,
            capsize=3,
            error_kw={'elinewidth': 1, 'alpha': 0.7}
        )

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_ABBREVIATIONS.get(m, m) for m in models], rotation=15, ha="right")
    ax.set_ylabel("Cumulative Successful Runs")
    ax.yaxis.set_major_formatter(PercentFormatter(100))
    ax.legend(title="Feedback Rounds", loc='best')
    plt.tight_layout()
    
    output_file = os.path.join(PLOTS_DIR, 'success_by_model_by_feedbackround_in_percent.png')
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")
    # plt.show()

def print_success_table(model_data: Dict[str, List[float]]):
    print("\nCumulative Success Rates by Feedback Round:")
    print(f"{'Model':<25} | {'No Feedback':<12} | {'1 Feedback':<12} | {'2 Feedbacks':<12} | {'3 Feedbacks':<12} | {'4 Feedbacks':<12} | {'5 Feedbacks':<12}")
    print("-" * 130)
    for model, values in model_data.items():
        row = f"{model:<25}"
        for val in values:
            row += f" | {val:11.2f}%"
        print(row)

if __name__ == "__main__":
    data, counts = get_model_data_from_csv(RESULTS_CSV)
    if data:
        visualize_success_by_llm(data, counts)
        print_success_table(data)