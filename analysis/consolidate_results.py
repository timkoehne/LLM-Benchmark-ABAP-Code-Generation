import json
import os
import glob
import pandas as pd

from common import (
    CATEGORIES,
    CATEGORY_RENAME,
    DATA_DIR,
    FEEDBACK_COLS,
    LAST_ROUND,
    PROMPT_CLASSIFICATION_CSV,
    RESULTS_CSV,
    SUCCESS,
    classify_feedback,
)


def consolidate_results():
    json_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    
    data = []

    for file_path in json_files:
        filename = os.path.basename(file_path)
        
        if filename in ["package.json", "tsconfig.json", "results.json"]: 
            continue
            
        model_name = filename.replace(".json", "")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except json.JSONDecodeError:
            print(f"Skipping {filename}: Invalid JSON")
            continue
            
        if not content or not isinstance(content, dict):
            continue
        
        first_key = next(iter(content))
        if not first_key.endswith(".txt"):
            continue

        print(f"Processing {model_name}...")

        for prompt_file, repetitions in content.items():
            prompt_id = prompt_file.replace(".txt", "")
            
            for rep_idx, conversation in enumerate(repetitions):
                row = {
                    "Model": model_name,
                    "Prompt": prompt_id,
                    "Repetition": rep_idx,
                    "Success": "False",
                    **{col: None for col in FEEDBACK_COLS},
                }
                
                feedback_round = 0
                
                for message in conversation:
                    if message["role"] == "user":
                        content_txt = message["content"]
                        
                        feedback_status = classify_feedback(content_txt)
                        is_feedback = feedback_status is not None
                        if feedback_status == SUCCESS:
                            row["Success"] = "True"
                    
                        if is_feedback:
                            if feedback_round <= LAST_ROUND:
                                row[f"Feedback_Round_{feedback_round}"] = feedback_status
                            feedback_round += 1
                data.append(row)
    df = pd.DataFrame(data)
    
    classification_path = PROMPT_CLASSIFICATION_CSV
    print(f"Checking for classification at: {os.path.abspath(classification_path)}")
    if os.path.exists(classification_path):
        print(f"Loading classification from {classification_path}")
        try:
            class_df = pd.read_csv(classification_path, sep=';')
            if 'HumanEval/Nr' in class_df.columns:
                class_df['Prompt_ID'] = class_df['HumanEval/Nr'].astype(str)
            elif 'Nr' in class_df.columns:
                 class_df['Prompt_ID'] = class_df['Nr'].astype(str)
            
            class_df = class_df.rename(columns=CATEGORY_RENAME)
            
            class_df = class_df.replace('X', 'True')

            cols_to_keep = ['Prompt_ID'] + CATEGORIES
            cols_to_keep = [c for c in cols_to_keep if c in class_df.columns]
            
            class_df = class_df[cols_to_keep]
            
            df = df.merge(class_df, left_on='Prompt', right_on='Prompt_ID', how='left')
            df = df.drop(columns=['Prompt_ID'])
            print("Merged prompt classification data.")
            
        except Exception as e:
            print(f"Failed to load/merge classification data: {e}")
    else:
        print(f"Warning: {classification_path} not found. Skipping classification merge.")

    try:
        df['Prompt_Int'] = df['Prompt'].astype(int)
        df = df.sort_values(by=['Model', 'Prompt_Int', 'Repetition'])
        df = df.drop(columns=['Prompt_Int'])
    except:
        df = df.sort_values(by=['Model', 'Prompt', 'Repetition'])

    output_path = RESULTS_CSV
    df.to_csv(output_path, sep=';', index=False)
    print(f"Successfully created {output_path} with {len(df)} rows.")

if __name__ == "__main__":
    consolidate_results()
