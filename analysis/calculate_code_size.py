"""Code-size metrics (LOC / SLOC / LLOC) for the ABAP benchmark.

Complements the functional pass@k metrics: among solutions that *pass* the unit
tests, this measures how concise / verbose the generated code is, a common
code-quality proxy in code-generation benchmarking papers.

Metrics (all computed on the final assistant submission that passed the tests):
  LOC   - Lines of Code: every physical line, including blanks and comments.
  SLOC  - (physical) Source Lines of Code: non-blank, non-comment lines.
  LLOC  - Logical Lines of Code: number of ABAP statements.

ABAP specifics:
  - Comments: a line whose first non-whitespace char is '*' is a full-line
    comment; a '"' starts an inline comment to end of line.
  - Statements terminate with a period '.'. Because the system prompt forces '.'
    as the decimal separator, a plain period-count would over-count (e.g. "1.5").
    LLOC therefore strips string/template literals and inline comments, then
    counts only periods that terminate a statement (followed by whitespace or
    end-of-line) -- a pragmatic approximation, not a full ABAP parse.

Run from the analysis/ directory:  python calculate_code_size.py
"""

import json
import os
import re
import glob
import numpy as np
import pandas as pd

from common import DATA_DIR, DATASET_DIR, MODEL_ABBREVIATIONS, MODEL_ORDER, SUCCESS, classify_feedback


CANONICAL_DIR = os.path.join(DATASET_DIR, "abap_canonical_solution")


# --- code extraction -------------------------------------------------------

def remove_code_blocks(llm_response: str) -> str:
    """Strip markdown code fences. Mirrors src/generate_llm_answers.py."""
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", llm_response, flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*```\s*$", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()


# --- metric functions ------------------------------------------------------

_STRING_LITERAL = re.compile(r"'[^']*'")
_TEMPLATE_LITERAL = re.compile(r"\|[^|]*\|")
_STMT_TERMINATOR = re.compile(r"\.(?=\s|$)")


def count_loc(src: str) -> int:
    """Total physical lines."""
    if not src:
        return 0
    return len(src.splitlines())


def count_sloc(src: str) -> int:
    """Non-blank, non-comment physical lines."""
    count = 0
    for line in src.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("*") or stripped.startswith('"'):
            continue  # full-line comment
        count += 1
    return count


def count_lloc(src: str) -> int:
    """Number of ABAP statements (statement-terminating periods)."""
    total = 0
    for line in src.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("*"):
            continue  # blank or full-line comment
        # Remove string/template literals so their '.' and '"' don't interfere.
        cleaned = _STRING_LITERAL.sub("''", stripped)
        cleaned = _TEMPLATE_LITERAL.sub("||", cleaned)
        # Cut an inline comment (first remaining '"' to end of line).
        quote = cleaned.find('"')
        if quote != -1:
            cleaned = cleaned[:quote]
        total += len(_STMT_TERMINATOR.findall(cleaned))
    return total


def metrics(src: str) -> tuple:
    return count_loc(src), count_sloc(src), count_lloc(src)


# --- passing-submission extraction -----------------------------------------

def passing_sources(model_json_path: str):
    """Yield the ABAP source of every attempt that passed the unit tests.

    The passing submission is the assistant message immediately preceding a user
    message containing 'The unit tests were successful' (same detection as
    consolidate_results.py).
    """
    with open(model_json_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    for _prompt_id, attempts in prompts.items():
        for conversation in attempts:
            prev_assistant = None
            for message in conversation:
                role = message.get("role")
                content = message.get("content", "")
                if role == "user" and classify_feedback(str(content)) == SUCCESS:
                    if prev_assistant is not None:
                        yield remove_code_blocks(prev_assistant)
                    break
                if role == "assistant":
                    prev_assistant = content


# --- canonical baseline ----------------------------------------------------

def canonical_baseline():
    files = sorted(glob.glob(os.path.join(CANONICAL_DIR, "*.abap")))
    locs, slocs, llocs = [], [], []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        loc, sloc, lloc = metrics(src)
        locs.append(loc)
        slocs.append(sloc)
        llocs.append(lloc)
    return {
        "Model": "Baseline",
        "N": len(files),
        "Mean LOC": np.mean(locs),
        "Median LOC": np.median(locs),
        "Mean SLOC": np.mean(slocs),
        "Median SLOC": np.median(slocs),
        "Mean LLOC": np.mean(llocs),
        "Median LLOC": np.median(llocs),
    }


# --- main ------------------------------------------------------------------

def calculate_code_size():
    canonical = canonical_baseline()
    canon_median_sloc = canonical["Median SLOC"]
    print(f"Baseline solutions: {canonical['N']} files, "
          f"median SLOC {canon_median_sloc:.1f}")

    rows = []
    for model in MODEL_ORDER:
        path = os.path.join(DATA_DIR, f"{model}.json")
        if not os.path.exists(path):
            print(f"  WARNING: missing {path}, skipping")
            continue

        sources = list(passing_sources(path))
        if not sources:
            rows.append({
                "Model": model, "N": 0,
                "Mean LOC": np.nan, "Median LOC": np.nan,
                "Mean SLOC": np.nan, "Median SLOC": np.nan,
                "Mean LLOC": np.nan, "Median LLOC": np.nan,
                "SLOC vs Baseline": np.nan,
            })
            print(f"  {model}: 0 passing solutions")
            continue

        m = np.array([metrics(s) for s in sources], dtype=float)
        loc, sloc, lloc = m[:, 0], m[:, 1], m[:, 2]
        rows.append({
            "Model": model,
            "N": len(sources),
            "Mean LOC": loc.mean(),
            "Median LOC": np.median(loc),
            "Mean SLOC": sloc.mean(),
            "Median SLOC": np.median(sloc),
            "Mean LLOC": lloc.mean(),
            "Median LLOC": np.median(lloc),
            "SLOC vs Baseline": np.median(sloc) / canon_median_sloc,
        })
        print(f"  {model}: {len(sources)} passing solutions")

    # Baseline row (ratio is 1.0 by definition).
    canonical["SLOC vs Baseline"] = 1.0
    rows.append(canonical)

    df = pd.DataFrame(rows)

    # --- console table ---
    header = (f"{'Model':<28} | {'N':>4} | {'LOC (mean/med)':>16} | "
              f"{'SLOC (mean/med)':>16} | {'LLOC (mean/med)':>16} | {'SLOC/Base':>10}")
    print("\n" + "=" * len(header))
    print(header)
    print("-" * len(header))
    for _, r in df.iterrows():
        label = MODEL_ABBREVIATIONS.get(r["Model"], r["Model"])
        if pd.isna(r["Mean SLOC"]):
            print(f"{label:<28} | {int(r['N']):>4} | {'—':>16} | "
                  f"{'—':>16} | {'—':>16} | {'—':>10}")
            continue
        loc_s = f"{r['Mean LOC']:.1f}/{r['Median LOC']:.0f}"
        sloc_s = f"{r['Mean SLOC']:.1f}/{r['Median SLOC']:.0f}"
        lloc_s = f"{r['Mean LLOC']:.1f}/{r['Median LLOC']:.0f}"
        print(f"{label:<28} | {int(r['N']):>4} | {loc_s:>16} | "
              f"{sloc_s:>16} | {lloc_s:>16} | {r['SLOC vs Baseline']:>10.2f}")
    print("=" * len(header))

    # --- CSV ---
    out_file = os.path.join(DATA_DIR, "code_size_metrics.csv")
    df.to_csv(out_file, index=False, float_format="%.3f")
    print(f"\nSaved results to {out_file}")

    # --- LaTeX ---
    print("\nLaTeX Table:\n")
    print("\\begin{table}[h!]")
    print("    \\centering")
    print("    \\resizebox{\\textwidth}{!}{")
    print("    \\begin{tabular}{lrrrrr}")
    print("    \\hline")
    print("    \\textbf{Model} & \\textbf{N} & \\textbf{LOC} & "
          "\\textbf{SLOC} & \\textbf{LLOC} & \\textbf{SLOC vs Base.} \\\\")
    print("    \\hline")
    for _, r in df.iterrows():
        name = MODEL_ABBREVIATIONS.get(r["Model"], r["Model"])
        if pd.isna(r["Median SLOC"]):
            print(f"    {name} & {int(r['N'])} & -- & -- & -- & -- \\\\")
            continue
        ratio = (f"{r['SLOC vs Baseline']:.2f}"
                 if not pd.isna(r["SLOC vs Baseline"]) else "--")
        print(f"    {name} & {int(r['N'])} & {r['Median LOC']:.1f} & "
              f"{r['Median SLOC']:.1f} & {r['Median LLOC']:.1f} & {ratio} \\\\")
    print("    \\hline")
    print("    \\end{tabular}")
    print("    }")
    print("    \\caption{Code-size metrics for passing solutions: median Lines of "
          "Code (LOC), physical Source Lines of Code (SLOC) and Logical Lines of "
          "Code (LLOC), plus median SLOC relative to the baseline reference "
          "solutions.}")
    print("    \\label{tab:code_size_metrics}")
    print("\\end{table}")


if __name__ == "__main__":
    calculate_code_size()
