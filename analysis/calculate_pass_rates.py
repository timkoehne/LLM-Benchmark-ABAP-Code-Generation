import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def get_success_flags(row: pd.Series) -> pd.Series:
    is_success = False
    if str(row['Success']).strip().lower() == 'true':
        is_success = True
    else:
        for i in range(6):
            col_name = f'Feedback_Round_{i}'
            if col_name in row:
                content = row[col_name]
                if pd.isna(content) or content == '':
                    continue
                if 'unit tests were successful' in str(content).lower():
                    is_success = True
                    break
                    
    is_success_no_ut = False
    if is_success:
        used_ut_feedback = False
        for i in range(6):
            col_name = f'Feedback_Round_{i}'
            if col_name in row:
                content = row[col_name]
                if pd.isna(content) or content == '':
                    continue
                if 'unit test failed' in str(content).lower():
                    used_ut_feedback = True
                    break
        if not used_ut_feedback:
            is_success_no_ut = True

    return pd.Series([is_success, is_success_no_ut])

def calculate_pass_rates(file_path: str):
    print("Loading data...")
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    df['Prompt'] = df['Prompt'].astype(str).str.strip()
    df['Model'] = df['Model'].astype(str).str.strip()
    
    print("Processing success flags...")
    df[['is_success', 'is_success_no_ut']] = df.apply(get_success_flags, axis=1)
    
    results = []
    
    for model in df['Model'].unique():
        model_df = df[df['Model'] == model]
        if model_df.empty:
            continue
            
        total_attempts = len(model_df)
        total_successes = model_df['is_success'].sum()
        total_successes_no_ut = model_df['is_success_no_ut'].sum()
        
        pass_at_1 = total_successes / total_attempts if total_attempts > 0 else 0
        pass_at_1_no_ut = total_successes_no_ut / total_attempts if total_attempts > 0 else 0
        
        prompts_grouped = model_df.groupby('Prompt')['is_success'].agg(['sum'])
        total_prompts = len(prompts_grouped)
        prompts_with_success = (prompts_grouped['sum'] > 0).sum()
        pass_at_10 = prompts_with_success / total_prompts if total_prompts > 0 else 0
        
        prompts_grouped_no_ut = model_df.groupby('Prompt')['is_success_no_ut'].agg(['sum'])
        prompts_with_success_no_ut = (prompts_grouped_no_ut['sum'] > 0).sum()
        pass_at_10_no_ut = prompts_with_success_no_ut / total_prompts if total_prompts > 0 else 0
        
        results.append({
            'Model': model,
            'Pass@1 (%)': pass_at_1 * 100,
            'Pass@10 (%)': pass_at_10 * 100,
            'Pass@1 No UT (%)': pass_at_1_no_ut * 100,
            'Pass@10 No UT (%)': pass_at_10_no_ut * 100,
            'Total Prompts': total_prompts,
            'Total Attempts': total_attempts
        })
        
    results_df = pd.DataFrame(results)
    
    # Define desired model order if present, else sort by Pass@10
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
    
    # Sort results
    model_order = {model: i for i, model in enumerate(desired_order)}
    results_df['order'] = results_df['Model'].map(lambda x: model_order.get(x, 999))
    results_df = results_df.sort_values(by=['order', 'Pass@10 (%)'], ascending=[True, False]).drop(columns=['order'])
    
    print("\n" + "="*120)
    print(f"{'Model':<30} | {'Pass@1 (%)':>12} | {'Pass@10 (%)':>12} | {'Pass@1 No UT (%)':>16} | {'Pass@10 No UT (%)':>17} | {'Prompts':>8} | {'Attempts':>8}")
    print("-" * 120)
    
    for _, row in results_df.iterrows():
        print(f"{row['Model']:<30} | {row['Pass@1 (%)']:>11.2f}% | {row['Pass@10 (%)']:>11.2f}% | {row['Pass@1 No UT (%)']:>15.2f}% | {row['Pass@10 No UT (%)']:>16.2f}% | {row['Total Prompts']:>8} | {row['Total Attempts']:>8}")
        
    print("="*120)
    
    out_file = "../data/pass_rates.csv"
    results_df.to_csv(out_file, index=False)
    print(f"\nSaved results to {out_file}")

    print("\nLaTeX Table:\n")
    print("\\begin{table}[h!]")
    print("    \\centering")
    print("    \\resizebox{\\textwidth}{!}{")
    print("    \\begin{tabular}{lrrrr}")
    print("    \\hline")
    print("    \\textbf{Model} & \\textbf{Pass@1} & \\textbf{Pass@10} & \\textbf{Pass@1 (No UT)} & \\textbf{Pass@10 (No UT)} \\\\")
    print("    \\hline")
    for _, row in results_df.iterrows():
        model_name = row['Model']
        if model_name == "llama-3.3-70b-instruct": model_name = "Llama-3.3-70B-Instruct"
        if model_name == "codestral-22b": model_name = "Codestral-22B"
        if model_name == "qwen2.5-coder-32b-instruct": model_name = "Qwen2.5-Coder-32B-Instruct"
        if model_name == "qwen3-coder": model_name = "Qwen3-Coder"
        if model_name == "gpt-oss_20b": model_name = "GPT-OSS-20B"
        if model_name == "gpt-oss_120b": model_name = "GPT-OSS-120B"
        if model_name == "gpt-5-2025-08-07": model_name = "GPT-5-2025-08-07"
        if model_name == "claude-sonnet-4-20250514": model_name = "Claude-Sonnet-4-20250514"
        print(f"    {model_name} & {row['Pass@1 (%)']:.2f}\\% & {row['Pass@10 (%)']:.2f}\\% & {row['Pass@1 No UT (%)']:.2f}\\% & {row['Pass@10 No UT (%)']:.2f}\\% \\\\")
    print("    \\hline")
    print("    \\end{tabular}")
    print("    }")
    print("    \\caption{Success rates (Pass@1 and Pass@10) with and without unit test improvements.}")
    print("    \\label{tab:model_pass_rates}")
    print("\\end{table}")

if __name__ == '__main__':
    calculate_pass_rates('../data/results.csv')
