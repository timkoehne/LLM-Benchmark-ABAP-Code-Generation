import json
import os
import glob
import re
import ast

from common import DATA_DIR, FEEDBACK_SYNTAX_FAILED, SYNTAX_ERRORS_JSON
from abap_errors import ERRORS_BY_CATEGORY  # in src/, put on the path by common

def generate_syntax_errors():
    output_file = SYNTAX_ERRORS_JSON
    json_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    
    results = {}

    for file_path in json_files:
        filename = os.path.basename(file_path)
        
        if filename in ["package.json", "tsconfig.json", "results.json", "syntax_errors.json"]: 
            continue
            
        model_name = filename.replace(".json", "")
        print(f"Processing {model_name}...")
        
        results[model_name] = {category: {error.regex: [] for error in errors} 
                               for category, errors in ERRORS_BY_CATEGORY.items()}
        results[model_name]["Uncategorized"] = {"Other": []}
        skipped_warnings = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except json.JSONDecodeError:
            print(f"Skipping {filename}: Invalid JSON")
            continue
            
        if not content or not isinstance(content, dict):
            continue

        for prompt_file, repetitions in content.items():
            for conversation in repetitions:
                for message in conversation:
                    if message["role"] == "user":
                        content_txt = message["content"]
                        if FEEDBACK_SYNTAX_FAILED in content_txt:
                            try:
                                error_list_str = content_txt.split(f"{FEEDBACK_SYNTAX_FAILED}\n")[-1]
                                error_list = ast.literal_eval(error_list_str)
                                
                                for error_item in error_list:
                                    if isinstance(error_item, dict) and 'short_text' in error_item:
                                        # The syntax check reports errors ("E")
                                        # and warnings ("W") in the same list.
                                        # Warnings are not failures - they do
                                        # not stop activation - so they are not
                                        # part of the error profile.  Counting
                                        # them mixes ~3,700 deprecation and
                                        # style notices into the categories.
                                        if error_item.get('type') != 'E':
                                            skipped_warnings += 1
                                            continue

                                        short_text = error_item['short_text']
                                        
                                        matched = False
                                        for category, errors in ERRORS_BY_CATEGORY.items():
                                            for error_def in errors:
                                                if re.match(error_def.regex, short_text):
                                                    results[model_name][category][error_def.regex].append(short_text)
                                                    matched = True
                                                    break
                                            if matched:
                                                break
                                        
                                        if not matched:
                                            results[model_name]["Uncategorized"]["Other"].append(short_text)
                                            
                            except (SyntaxError, ValueError, IndexError) as e:
                                pass

        catch_all = len(results[model_name]["Declaration Errors"].get(".*", []))
        categorized = sum(
            len(v) for cat in results[model_name].values() for v in cat.values()
        )
        print(
            f"  {categorized} errors categorized "
            f"({catch_all} of them only by the '.*' catch-all), "
            f"{skipped_warnings} warnings skipped"
        )

    final_results = {}
    for model, categories in results.items():
        final_results[model] = {}
        for category, patterns in categories.items():
            non_empty_patterns = {p: v for p, v in patterns.items() if v}
            if non_empty_patterns:
                final_results[model][category] = non_empty_patterns

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=4)
    
    print(f"Successfully generated {output_file}")

if __name__ == "__main__":
    generate_syntax_errors()
