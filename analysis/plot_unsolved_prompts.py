import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Set, Tuple
from plot_style import COLORS, apply_plot_style, MODEL_ABBREVIATIONS

apply_plot_style()

def get_unsolved_prompts_per_model(file_path: str) -> Tuple[Dict[str, Set[str]], List[str]]:
    try:
        df = pd.read_csv(file_path, sep=';')
        df['Prompt'] = df['Prompt'].astype(str).str.strip()
        df['Model'] = df['Model'].astype(str).str.strip()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {}, []

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
    final_models = model_order + remaining
    
    unsolved_prompts = {}

    for model in final_models:
        model_df = df[df['Model'] == model]
        if model_df.empty:
            continue
            
        all_prompts = model_df['Prompt'].unique()
        model_unsolved = set()
        
        for prompt_id in all_prompts:
            prompt_attempts = model_df[model_df['Prompt'] == prompt_id]
            
            task_succeeded_once = False
            for _, row in prompt_attempts.iterrows():
                is_success = False
                if str(row['Success']).strip().lower() == 'true':
                    is_success = True
                else:
                    rounds_content = [row[f'Feedback_Round_{i}'] for i in range(6)]
                    for content in rounds_content:
                        if pd.isna(content) or content == '':
                            continue
                        if 'unit tests were successful' in str(content):
                            is_success = True
                            break
                
                if is_success:
                    task_succeeded_once = True
                    break
                    
            if not task_succeeded_once:
                model_unsolved.add(str(prompt_id))
                
        unsolved_prompts[model] = model_unsolved
        
    return unsolved_prompts, [m for m in final_models if m in unsolved_prompts]

def plot_unsolved_counts(unsolved_prompts: Dict[str, Set[str]], models: List[str]):
    fig, ax = plt.subplots(figsize=(12, 7))
    
    counts = [len(unsolved_prompts[m]) for m in models]
    x = np.arange(len(models))
    
    colors = [COLORS[1] if m == 'All Models (Intersection)' else COLORS[3] for m in models]
    
    bars = ax.bar(
        x, 
        counts, 
        width=0.5, 
        color=colors, 
        edgecolor='white'
    )
    
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2, 
            height + 0.5, 
            str(int(height)), 
            ha='center', 
            va='bottom', 
            fontsize=10,
            fontweight='bold'
        )
        
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_ABBREVIATIONS.get(m, m) for m in models], rotation=15, ha="right")
    ax.set_ylabel("Number of Unsolved Prompts")
    
    plt.tight_layout()
    output_file = '../plots/unsolved_prompts_per_model.png'
    plt.savefig(output_file)
    print(f"\nPlot saved to {output_file}")

def print_unsolved_details(unsolved_prompts: Dict[str, Set[str]], models: List[str]):
    print("\n" + "="*80)
    print("UNSOLVED PROMPTS PER MODEL")
    print("="*80)
    
    for model in models:
        failed_ids = sorted(list(unsolved_prompts[model]))
        count = len(failed_ids)
        print(f"\n{model} ({count} unsolved prompts):")
        
        # Print in groups of 10 for better readability
        if count == 0:
            print("  None - All prompts succeeded at least once!")
        else:
            for i in range(0, count, 15):
                chunk = failed_ids[i:i+15]
                print("  " + ", ".join(str(pid) for pid in chunk))

if __name__ == "__main__":
    file_path = '../data/results.csv'
    unsolved_prompts, ordered_models = get_unsolved_prompts_per_model(file_path)
    
    if unsolved_prompts:
        # Calculate intersection of all models
        all_failed = set.intersection(*[unsolved_prompts[m] for m in ordered_models])
        unsolved_prompts['All Models (Intersection)'] = all_failed
        ordered_models.append('All Models (Intersection)')
        
        plot_unsolved_counts(unsolved_prompts, ordered_models)
        print_unsolved_details(unsolved_prompts, ordered_models)
