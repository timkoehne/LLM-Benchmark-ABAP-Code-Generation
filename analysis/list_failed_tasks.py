import pandas as pd
import numpy as np
import os
from typing import Dict, List
from common import FEEDBACK_COLS, RESULTS_CSV, SUCCESS, order_models

def get_failed_task_counts(file_path):
    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None, None

    target_models = df['Model'].unique()
    
    target_models = order_models(target_models)
    
    # print(f"Models considered: {target_models}")
    
    df = df[df['Model'].isin(target_models)]

    categories = [
        'String Handling',
        'List or Array Operation',
        'Mathematical Calculation',
        'Logical Condition',
        'ABAP Database Operation'
    ]
    
    failed_task_ids = {model: {} for model in target_models}
    
    for model in target_models:
        model_df = df[df['Model'] == model]
        
        for category in categories:
            if category not in df.columns:
                failed_task_ids[model][category] = set()
                continue
                
            category_df = model_df[model_df[category].astype(str) == 'True']
            
            if len(category_df) == 0:
                failed_task_ids[model][category] = set()
                continue
            
            tasks = category_df['Prompt'].unique()
            
            current_category_failed_ids = set()
            
            for task_id in tasks:
                task_attempts = category_df[category_df['Prompt'] == task_id]
                
                task_succeeded_once = False
                
                for _, row in task_attempts.iterrows():
                    is_success = False
                    if str(row['Success']) == 'True':
                        is_success = True
                    else:
                        rounds_content = [row[col] for col in FEEDBACK_COLS]
                        for content in rounds_content:
                            if pd.isna(content) or content == '':
                                continue
                            if SUCCESS in str(content):
                                is_success = True
                                break
                    
                    if is_success:
                        task_succeeded_once = True
                        break
                
                if not task_succeeded_once:
                    current_category_failed_ids.add(task_id)
            
            failed_task_ids[model][category] = current_category_failed_ids

    return failed_task_ids

def list_failed_tasks(failed_task_ids: Dict[str, Dict[str, set]]):
    models = list(failed_task_ids.keys())
    first_model = models[0]
    categories = list(failed_task_ids[first_model].keys())
    
    all_failed_ids = set()

    for category in categories:
        sets = [failed_task_ids[model][category] for model in models]
        intersection = set.intersection(*sets)
        
        if intersection:
            # print(f"\nCategory: {category}")
            # for task_id in intersection:
            #     print(f"  - {task_id}")
            all_failed_ids.update(intersection)

    print("\nTotal Unique Failed Prompt IDs (Intersection of all models):")
    sorted_ids = sorted(list(all_failed_ids))
    for task_id in sorted_ids:
        print(task_id)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = RESULTS_CSV
    failed_task_ids = get_failed_task_counts(file_path)
    if failed_task_ids:
        list_failed_tasks(failed_task_ids)
