import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from common import MODEL_ABBREVIATIONS, PLOTS_DIR, RESULTS_CSV
from plot_style import COLORS, apply_plot_style

apply_plot_style()

def get_success_rates_by_model(file_path):
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

    df['Success_Bool'] = df['Success'].astype(str) == 'True'
    
    if 'Prompt' not in df.columns:
        print("Error: 'Prompt' column not found.")
        return None
        
    target_models = ['gpt-5-2025-08-07', 'claude-sonnet-4-20250514']
    model_data = {}
    
    for model in target_models:
        model_df = df[df['Model'] == model]
        if model_df.empty:
            print(f"Warning: No data found for model {model}")
            continue
            
        task_success = model_df.groupby('Prompt')['Success_Bool'].mean()
        model_data[model] = task_success
    
    return model_data

def plot_comparative_histogram(model_data):
    if not model_data:
        print("No model data to plot.")
        return

    # Each task is run 10 times, so the success count is a discrete value 0..10
    values = np.arange(0, 11)

    plot_data = {}
    for model, series in model_data.items():
        success_counts = np.round(series.values * 10).astype(int)
        counts = np.bincount(success_counts, minlength=11)
        total = len(series)
        if total > 0:
            percents = (counts / total) * 100
        else:
            percents = np.zeros(len(counts))
        plot_data[model] = percents

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_width = 0.4

    models = list(model_data.keys())
    model_colors = [COLORS[2], COLORS[5]]

    for i, model in enumerate(models):
        if i >= len(model_colors):
            break
        offset = (i - 0.5) * bar_width
        bars = ax.bar(
            values + offset,
            plot_data[model],
            width=bar_width,
            label=MODEL_ABBREVIATIONS.get(model, model),
            color=model_colors[i],
            edgecolor='white'
        )

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 0.5,
                    f'{int(round(height))}%',
                    ha='center',
                    va='bottom',
                    fontsize=8,
                    color='black'
                )

    ax.set_xlabel('Number of Successful Runs (out of 10)')
    ax.set_ylabel('Percent of Tasks')

    ax.set_xticks(values)
    ax.set_xticklabels([str(v) for v in values])

    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.legend()
    
    plt.tight_layout()
    output_file = os.path.join(PLOTS_DIR, 'success_distribution.png')
    plt.savefig(output_file)
    print(f"Saved plot to {output_file}")

if __name__ == "__main__":
    file_path = RESULTS_CSV
    data = get_success_rates_by_model(file_path)
    if data:
        plot_comparative_histogram(data)
