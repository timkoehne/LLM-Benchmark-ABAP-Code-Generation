"""95% confidence intervals for every proportion reported in the paper.

Two intervals are produced for each success rate:

* the **Wilson score interval**, which is what the paper says it uses.  It
  treats the |T| * M trials of a model as i.i.d. Bernoulli draws.  That is an
  approximation: trials are clustered within tasks and task difficulty is
  heterogeneous, so the Wilson width understates the true uncertainty.
* a **cluster bootstrap interval** that resamples whole tasks with
  replacement.  This respects the clustering and is the interval to quote if a
  reviewer challenges the independence assumption.

For proportions that are already task-level (the pi@10 metrics, the
never-solved counts per category) the unit of analysis is the task, so the
Wilson interval is appropriate as-is and no bootstrap is reported.

Writes ``data/confidence_intervals.csv`` and prints LaTeX-ready tables.

    python confidence_intervals.py
"""

import json
import os

import numpy as np
import pandas as pd

from plot_style import MODEL_ABBREVIATIONS as AB
from trial_outcomes import DATA, build_trials

MODEL_ORDER = [
    "llama-3.3-70b-instruct",
    "codestral-22b",
    "qwen2.5-coder-32b-instruct",
    "qwen3-coder",
    "gpt-oss_20b",
    "gpt-oss_120b",
    "gpt-5-2025-08-07",
    "claude-sonnet-4-20250514",
]
Z = 1.959963984540054          # two-sided 95%
N_BOOT = 10000
SEED = 20260830


def wilson(k, n, z=Z):
    """Wilson score interval for a binomial proportion, in percent."""
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return p * 100, max(0.0, centre - half) * 100, min(1.0, centre + half) * 100


def cluster_bootstrap(success_by_task, n_boot=N_BOOT, seed=SEED):
    """Percentile bootstrap over tasks for a mean of clustered indicators.

    ``success_by_task`` maps each task to the number of successful trials and
    the number of trials in that task.
    """
    succ = np.asarray([s for s, _ in success_by_task], dtype=float)
    tot = np.asarray([t for _, t in success_by_task], dtype=float)
    if tot.sum() == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(succ), size=(n_boot, len(succ)))
    draws = succ[idx].sum(axis=1) / tot[idx].sum(axis=1)
    return float(np.percentile(draws, 2.5) * 100), float(np.percentile(draws, 97.5) * 100)


def newcombe_diff(k1, n1, k2, n2, z=Z):
    """Newcombe's hybrid score interval for the difference of two proportions."""
    p1, l1, u1 = [v / 100 for v in wilson(k1, n1, z)]
    p2, l2, u2 = [v / 100 for v in wilson(k2, n2, z)]
    lo = (p1 - p2) - np.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = (p1 - p2) + np.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return (p1 - p2) * 100, lo * 100, hi * 100


def fmt(p, lo, hi):
    if np.isnan(p):
        return "-"
    return f"{p:5.1f} [{lo:4.1f}, {hi:5.1f}]"


def main():
    df, CATS = build_trials()
    per = {m: df[df.Model == m] for m in MODEL_ORDER}
    rows = []

    def trial_ci(sub, col, n, label, model, boot=True):
        k = int((sub[col] <= n).sum())
        tot = len(sub)
        p, lo, hi = wilson(k, tot)
        blo = bhi = float("nan")
        if boot and tot:
            g = sub.assign(ok=sub[col] <= n).groupby("Prompt")["ok"]
            blo, bhi = cluster_bootstrap(list(zip(g.sum(), g.size())))
        rows.append(dict(metric=label, model=AB[model], level="trial", k=k, n=tot,
                         estimate=p, wilson_low=lo, wilson_high=hi,
                         boot_low=blo, boot_high=bhi))
        return p, lo, hi, blo, bhi

    def task_ci(sub, col, n, label, model):
        solved = sub.assign(ok=sub[col] <= n).groupby("Prompt")["ok"].any()
        k, tot = int(solved.sum()), len(solved)
        p, lo, hi = wilson(k, tot)
        rows.append(dict(metric=label, model=AB[model], level="task", k=k, n=tot,
                         estimate=p, wilson_low=lo, wilson_high=hi,
                         boot_low=np.nan, boot_high=np.nan))
        return p, lo, hi

    # ---------------------------------------------------------------- Table 5/6
    print("=" * 100)
    print("TABLES 5 & 6  trial-level rates, n = 1800     Wilson [.] / cluster bootstrap over tasks {.}")
    print("=" * 100)
    print(f"{'Model':<12}{'p1@1(0)':>34}{'p1@1(5)':>34}{'p2@1(5)':>34}")
    for m in MODEL_ORDER:
        cells = []
        for col, n, lab in [("l1_round", 0, "p1@1(0)"), ("l1_round", 5, "p1@1(5)"),
                            ("success_round", 5, "p2@1(5)")]:
            p, lo, hi, blo, bhi = trial_ci(per[m], col, n, lab, m)
            cells.append(f"{fmt(p, lo, hi)} {{{blo:4.1f},{bhi:5.1f}}}")
        print(f"{AB[m]:<12}" + "".join(f"{c:>34}" for c in cells))

    # ------------------------------------------------------------------ Table 7
    print("\n" + "=" * 100)
    print("TABLES 5 & 7  task-level rates pi@10(n), n = 180 tasks")
    print("=" * 100)
    print(f"{'Model':<12}{'p1@10(0)':>24}{'p1@10(5)':>24}{'p2@10(5)':>24}")
    for m in MODEL_ORDER:
        cells = []
        for col, n, lab in [("l1_round", 0, "p1@10(0)"), ("l1_round", 5, "p1@10(5)"),
                            ("success_round", 5, "p2@10(5)")]:
            cells.append(fmt(*task_ci(per[m], col, n, lab, m)))
        print(f"{AB[m]:<12}" + "".join(f"{c:>24}" for c in cells))

    # ----------------------------------------------------------------- Figure 3
    for col, name in [("success_round", "p2@1(n)"), ("l1_round", "p1@1(n)")]:
        print("\n" + "=" * 100)
        print(f"FIGURE 3  cumulative {name} with Wilson intervals, n = 1800 per cell")
        print("=" * 100)
        print(f"{'Model':<12}" + "".join(f"{'n='+str(i):>22}" for i in range(6)))
        for m in MODEL_ORDER:
            cells = []
            for i in range(6):
                p, lo, hi, _, _ = trial_ci(per[m], col, i, f"{name[:5]}({i})", m, boot=False)
                cells.append(fmt(p, lo, hi))
            print(f"{AB[m]:<12}" + "".join(f"{c:>22}" for c in cells))

    # ----------------------------------------------------------------- Figure 5
    print("\n" + "=" * 100)
    print("FIGURE 5  p2@1(5) by task category, Wilson intervals (n = tasks_in_category x 10)")
    print("=" * 100)
    print(f"{'Model':<12}" + "".join(f"{c[:11]:>23}" for c in CATS))
    for m in MODEL_ORDER:
        cells = []
        for c in CATS:
            sub = per[m][per[m][c]]
            p, lo, hi, _, _ = trial_ci(sub, "success_round", 5, f"p2@1(5)|{c}", m, boot=False)
            cells.append(fmt(p, lo, hi))
        print(f"{AB[m]:<12}" + "".join(f"{x:>23}" for x in cells))

    # ---------------------------------------------------------------- Table 11
    print("\n" + "=" * 100)
    print("TABLE 11  share of tasks per category never solved by either GPT-5 or Claude-S4")
    print("=" * 100)
    g5, cs4 = "gpt-5-2025-08-07", "claude-sonnet-4-20250514"
    cnt = {m: per[m].assign(ok=per[m]["success_round"] <= 5)
                    .groupby("Prompt")["ok"].sum() for m in MODEL_ORDER}
    never = {m: set(cnt[m][cnt[m] == 0].index) for m in MODEL_ORDER}
    inter = never[g5] & never[cs4]
    univ = set.intersection(*[never[m] for m in MODEL_ORDER if m != "codestral-22b"])
    tasks = df.drop_duplicates("Prompt").set_index("Prompt")[CATS]
    print(f"{'Category':<28}{'never/total':>14}{'Wilson 95%':>24}{'universal/total':>18}{'Wilson 95%':>24}")
    for c in CATS:
        ic = set(tasks.index[tasks[c]])
        for name, s in [("never", inter), ("univ", univ)]:
            rows.append(dict(metric=f"{name}_solved|{c}", model="GPT-5+Claude-S4" if name == "never" else "all models",
                             level="task", k=len(s & ic), n=len(ic),
                             **dict(zip(("estimate", "wilson_low", "wilson_high"),
                                        wilson(len(s & ic), len(ic)))),
                             boot_low=np.nan, boot_high=np.nan))
        a = wilson(len(inter & ic), len(ic))
        b = wilson(len(univ & ic), len(ic))
        print(f"{c:<28}{f'{len(inter & ic)}/{len(ic)}':>14}{fmt(*a):>24}"
              f"{f'{len(univ & ic)}/{len(ic)}':>18}{fmt(*b):>24}")

    # ---------------------------------------------------------------- Table 12
    print("\n" + "=" * 100)
    print("TABLE 12  syntax-error category shares, Wilson intervals "
          "(n = categorised errors per model)")
    print("=" * 100)
    with open(os.path.join(DATA, "syntax_errors.json")) as f:
        se = json.load(f)
    order = ["Lexical and Token Errors", "Structural and Formatting Errors",
             "Type and Conversion Errors", "OOP Errors", "Declaration Errors"]
    print(f"{'Model':<12}" + "".join(f"{c[:11]:>23}" for c in order) + f"{'n':>8}")
    for m in MODEL_ORDER:
        cnts = {c: sum(len(v) for v in se.get(m, {}).get(c, {}).values()) for c in order}
        tot = sum(cnts.values())
        cells = []
        for c in order:
            p, lo, hi = wilson(cnts[c], tot)
            rows.append(dict(metric=f"syntax_error|{c}", model=AB[m], level="error",
                             k=cnts[c], n=tot, estimate=p, wilson_low=lo, wilson_high=hi,
                             boot_low=np.nan, boot_high=np.nan))
            cells.append(fmt(p, lo, hi))
        print(f"{AB[m]:<12}" + "".join(f"{x:>23}" for x in cells) + f"{tot:>8}")

    # -------------------------------------------------- pairwise model contrasts
    print("\n" + "=" * 100)
    print("PAIRWISE CONTRASTS  difference in p2@1(5), Newcombe hybrid score interval")
    print("=" * 100)
    print(f"{'contrast':<28}{'difference (pp)':>32}")
    pairs = [(g5, cs4), ("gpt-oss_120b", "gpt-oss_20b"), (g5, "gpt-oss_120b"),
             (cs4, "gpt-oss_120b")]
    for a, b in pairs:
        ka = int((per[a]["success_round"] <= 5).sum())
        kb = int((per[b]["success_round"] <= 5).sum())
        d, lo, hi = newcombe_diff(ka, len(per[a]), kb, len(per[b]))
        rows.append(dict(metric="diff p2@1(5)", model=f"{AB[a]} - {AB[b]}", level="trial",
                         k=ka - kb, n=len(per[a]), estimate=d,
                         wilson_low=lo, wilson_high=hi, boot_low=np.nan, boot_high=np.nan))
        star = "" if lo <= 0 <= hi else "  (excludes 0)"
        print(f"{AB[a]+' - '+AB[b]:<28}{d:>13.1f} [{lo:5.1f}, {hi:5.1f}]{star}")

    out = os.path.join(DATA, "confidence_intervals.csv")
    pd.DataFrame(rows).to_csv(out, index=False, float_format="%.4f")
    print(f"\nwrote {os.path.abspath(out)}  ({len(rows)} rows)")

    # ----------------------------------------------------------------- LaTeX
    print("\n% ---- LaTeX: Table 6 with Wilson intervals ----")
    print("\\begin{tabular}{lccc}")
    print("\\hline")
    print("\\textbf{Model} & $p_1@1(0)$ & $p_1@1(5)$ & $p_2@1(5)$ \\\\")
    print("\\hline")
    for m in MODEL_ORDER:
        cells = []
        for col, n in [("l1_round", 0), ("l1_round", 5), ("success_round", 5)]:
            k = int((per[m][col] <= n).sum())
            p, lo, hi = wilson(k, len(per[m]))
            cells.append(f"{p:.1f}\\% [{lo:.1f}, {hi:.1f}]")
        print(f"{AB[m]} & " + " & ".join(cells) + " \\\\")
    print("\\hline")
    print("\\end{tabular}")

    print("\n% ---- LaTeX: Table 7 with Wilson intervals ----")
    print("\\begin{tabular}{lccc}")
    print("\\hline")
    print("\\textbf{Model} & $p_1@10(0)$ & $p_1@10(5)$ & $p_2@10(5)$ \\\\")
    print("\\hline")
    for m in MODEL_ORDER:
        cells = []
        for col, n in [("l1_round", 0), ("l1_round", 5), ("success_round", 5)]:
            s = per[m].assign(ok=per[m][col] <= n).groupby("Prompt")["ok"].any()
            p, lo, hi = wilson(int(s.sum()), len(s))
            cells.append(f"{p:.1f}\\% [{lo:.1f}, {hi:.1f}]")
        print(f"{AB[m]} & " + " & ".join(cells) + " \\\\")
    print("\\hline")
    print("\\end{tabular}")


if __name__ == "__main__":
    main()
