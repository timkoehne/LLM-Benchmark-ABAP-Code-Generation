import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from typing import Dict, Tuple
from plot_style import COLORS, apply_plot_style

apply_plot_style()

def get_comparison_data(file_path: str) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, int]]:
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {}, {}, {}

    models = df['Model'].unique()
    models = [m for m in models if 'codestral' not in m.lower()]
    
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
    model_order = [m for m in desired_order if m in models]
    remaining = [m for m in models if m not in model_order]
    models = model_order + remaining
    
    success_normal = {}
    success_no_ut = {}
    sample_counts = {}

    for model in models:
        model_df = df[df['Model'] == model]
        total_samples = len(model_df)
        sample_counts[model] = total_samples
        
        normal_success_count = 0
        no_ut_success_count = 0
        
        for _, row in model_df.iterrows():
            is_success = False
            
            if str(row['Success']) == 'True':
                 is_success = True
            
            rounds_content = [row[f'Feedback_Round_{i}'] for i in range(6)]
            
            for content in rounds_content:
                if pd.isna(content) or content == '':
                    break
                if 'unit tests were successful' in str(content):
                    is_success = True
                    break
                    
            if is_success:
                normal_success_count += 1
                
                # Check if it succeeded without ever needing unit test feedback
                used_ut_feedback = False
                for content in rounds_content:
                    if pd.isna(content) or content == '':
                        break
                    if 'unit test failed' in str(content):
                        used_ut_feedback = True
                        break
                
                if not used_ut_feedback:
                    no_ut_success_count += 1
                    
        if total_samples > 0:
            success_normal[model] = (normal_success_count / total_samples) * 100
            success_no_ut[model] = (no_ut_success_count / total_samples) * 100
        else:
            success_normal[model] = 0
            success_no_ut[model] = 0
            
    return success_normal, success_no_ut, sample_counts

def plot_comparison(success_normal: Dict[str, float], success_no_ut: Dict[str, float], sample_counts: Dict[str, int]):
    models = list(success_normal.keys())
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(models))
    bar_width = 0.35
    
    normal_vals = [success_normal[m] for m in models]
    no_ut_vals = [success_no_ut[m] for m in models]
    
    # Calculate error margins if sample counts format allows
    def get_errors(values):
        errors = []
        for i, model in enumerate(models):
            p = values[i] / 100.0
            n = sample_counts[model]
            if n > 0:
                se = np.sqrt(p * (1 - p) / n)
                margin = 1.96 * se * 100
                errors.append(margin)
            else:
                errors.append(0)
        return errors
        
    normal_errs = get_errors(normal_vals)
    no_ut_errs = get_errors(no_ut_vals)
    
    # Plot bars
    bars1 = ax.bar(
        x - bar_width/2, 
        no_ut_vals, 
        width=bar_width, 
        label='Without Semantic Feedback for Improvement', 
        color=COLORS[4], 
        yerr=no_ut_errs,
        capsize=3,
        error_kw={'elinewidth': 1, 'alpha': 0.7}
    )
    
    bars2 = ax.bar(
        x + bar_width/2, 
        normal_vals, 
        width=bar_width, 
        label='With Semantic Feedback for Improvement', 
        color=COLORS[0], 
        yerr=normal_errs,
        capsize=3,
        error_kw={'elinewidth': 1, 'alpha': 0.7}
    )
    
    # Add text labels
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + no_ut_errs[i] + 1, f'{height:.1f}%', ha='center', va='bottom', fontsize=9, rotation=0)
        
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + normal_errs[i] + 1, f'{height:.1f}%', ha='center', va='bottom', fontsize=9, rotation=0)
    
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylabel("Successful Code Generations")
    ax.yaxis.set_major_formatter(PercentFormatter(100))
    ax.set_title("Success Rate: Without Unit Test Improvement vs After 5 Feedback Rounds\n(with 95% Confidence Intervals)")
    ax.legend()
    
    plt.tight_layout()
    output_file = '../plots/success_with_vs_without_unittest.png'
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")
    
def print_comparison_table(success_normal: Dict[str, float], success_no_ut: Dict[str, float]):
    print("\nSuccess Rates Comparison:")
    print(f"{'Model':<25} | {'Without Unit Test Improvement':<30} | {'After 5 Rounds (Normal)':<25} | {'Difference'}")
    print("-" * 105)
    for model in success_normal.keys():
        val_normal = success_normal[model]
        val_no_ut = success_no_ut[model]
        diff = val_normal - val_no_ut
        print(f"{model:<25} | {val_no_ut:29.2f}% | {val_normal:24.2f}% | {diff:9.2f}%")

if __name__ == "__main__":
    success_normal, success_no_ut, counts = get_comparison_data('../data/results.csv')
    if success_normal:
        plot_comparison(success_normal, success_no_ut, counts)
        print_comparison_table(success_normal, success_no_ut)
