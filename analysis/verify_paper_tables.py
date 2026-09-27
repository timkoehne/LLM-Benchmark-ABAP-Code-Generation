"""Recompute every numeric claim in the paper from the raw benchmark logs.

Reads the conversation logs through ``trial_outcomes.build_trials`` (which,
unlike ``consolidate_results.py``/``data/results.csv``, recognises all eight
feedback messages the harness emits) and prints each recomputed value next to
the value printed in the paper, flagging mismatches.

    python verify_paper_tables.py
"""

import json
import os
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

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
CORR_MODELS = [m for m in MODEL_ORDER if m != "codestral-22b"]
ROUNDS = range(6)
G5, CS4 = "gpt-5-2025-08-07", "claude-sonnet-4-20250514"

OK, BAD = "ok", "** MISMATCH **"


def check(got, paper, tol=0.05):
    if paper is None or got is None:
        return "-"
    return OK if abs(got - paper) <= tol else BAD


def header(title):
    print("\n" + "=" * 104)
    print(title)
    print("=" * 104)


def main():
    df, CATS = build_trials()
    per = {m: df[df.Model == m] for m in MODEL_ORDER}
    tasks = df.drop_duplicates("Prompt").set_index("Prompt")[CATS]

    def p_at_1(m, col, n):
        return (per[m][col] <= n).mean() * 100

    def p_at_10(m, col, n):
        d = per[m]
        return d.assign(ok=d[col] <= n).groupby("Prompt")["ok"].any().mean() * 100

    print(f"{len(df)} trials = {df.Model.nunique()} models x "
          f"{df.Prompt.nunique()} tasks x {df.Repetition.nunique()} repetitions")

    # ------------------------------------------------------------------ T2
    header("TABLE 2  Task counts per category")
    paper = {"String Handling": 76, "List or Array Operation": 108,
             "Mathematical Calculation": 93, "Logical Condition": 125,
             "ABAP Database Operation": 16}
    for c in CATS:
        n = int(tasks[c].sum())
        print(f"  {c:<28}{n:>6}  paper {paper[c]:>4}   {check(n, paper[c], 0)}")
    print(f"  {'distinct tasks':<28}{len(tasks):>6}  paper  180   {check(len(tasks), 180, 0)}")

    # ------------------------------------------------------------------ T5
    header("TABLE 5  Initial trial  p1@1(0) / p1@10(0)")
    paper = {"Llama-33": (0.0, 0.0), "Code-22": (0.0, 0.0), "Qwen-25C": (6.0, 9.4),
             "Qwen-3C": (11.7, 18.9), "GPT-OSS20": (3.1, 15.0),
             "GPT-OSS120": (1.4, 9.4), "GPT-5": (19.3, 50.6), "Claude-S4": (24.1, 29.4)}
    print(f"  {'Model':<12}{'p1@1(0)':>9}{'paper':>8}{'p1@10(0)':>11}{'paper':>8}   status")
    for m in MODEL_ORDER:
        a, b = p_at_1(m, "l1_round", 0), p_at_10(m, "l1_round", 0)
        pa, pb = paper[AB[m]]
        print(f"  {AB[m]:<12}{a:>8.1f}%{pa:>7.1f}%{b:>10.1f}%{pb:>7.1f}%   "
              f"{check(a, pa)} / {check(b, pb)}")

    # ------------------------------------------------------------------ T6
    header("TABLE 6  p1@1(0) / p1@1(5) / p2@1(5)")
    paper = {"Llama-33": (0.0, 16.4, 20.8), "Code-22": (0.0, 0.0, 0.0),
             "Qwen-25C": (6.0, 10.6, 13.0), "Qwen-3C": (11.7, 18.3, 20.9),
             "GPT-OSS20": (3.1, 26.0, 29.3), "GPT-OSS120": (1.4, 39.6, 46.2),
             "GPT-5": (19.3, 69.3, 77.1), "Claude-S4": (24.1, 65.4, 74.7)}
    print(f"  {'Model':<12}{'p1@1(0)':>9}{'pap':>7}{'p1@1(5)':>10}{'pap':>7}"
          f"{'p2@1(5)':>10}{'pap':>7}   status")
    for m in MODEL_ORDER:
        v = (p_at_1(m, "l1_round", 0), p_at_1(m, "l1_round", 5), p_at_1(m, "success_round", 5))
        p = paper[AB[m]]
        print(f"  {AB[m]:<12}{v[0]:>8.1f}%{p[0]:>6.1f}%{v[1]:>9.1f}%{p[1]:>6.1f}%"
              f"{v[2]:>9.1f}%{p[2]:>6.1f}%   "
              f"{check(v[0],p[0])} {check(v[1],p[1])} {check(v[2],p[2])}")

    # ------------------------------------------------------------------ T7
    header("TABLE 7  p1@10(0) / p1@10(5) / p2@10(5)")
    paper = {"Llama-33": (0.0, 27.2, 32.8), "Code-22": (0.0, 0.0, 0.0),
             "Qwen-25C": (9.4, 16.1, 19.4), "Qwen-3C": (18.9, 27.8, 33.9),
             "GPT-OSS20": (15.0, 52.8, 56.1), "GPT-OSS120": (9.4, 68.3, 74.4),
             "GPT-5": (50.6, 82.2, 86.1), "Claude-S4": (29.4, 78.3, 84.4)}
    print(f"  {'Model':<12}{'p1@10(0)':>10}{'pap':>7}{'p1@10(5)':>11}{'pap':>7}"
          f"{'p2@10(5)':>11}{'pap':>7}   status")
    for m in MODEL_ORDER:
        v = (p_at_10(m, "l1_round", 0), p_at_10(m, "l1_round", 5), p_at_10(m, "success_round", 5))
        p = paper[AB[m]]
        print(f"  {AB[m]:<12}{v[0]:>9.1f}%{p[0]:>6.1f}%{v[1]:>10.1f}%{p[1]:>6.1f}%"
              f"{v[2]:>10.1f}%{p[2]:>6.1f}%   "
              f"{check(v[0],p[0])} {check(v[1],p[1])} {check(v[2],p[2])}")

    # ------------------------------------------------- cumulative trajectories
    header("FIGURE 3  Cumulative rates per feedback cycle (used by the text of 4.2)")
    for col, name in [("success_round", "p2@1(n)"), ("l1_round", "p1@1(n)")]:
        print(f"\n  {name}")
        print(f"  {'Model':<12}" + "".join(f"{'n='+str(n):>9}" for n in ROUNDS))
        for m in MODEL_ORDER:
            print(f"  {AB[m]:<12}" +
                  "".join(f"{p_at_1(m, col, n):>8.1f}%" for n in ROUNDS))

    # ------------------------------------------------------------------ T8
    header("TABLE 8  Solution-stability distribution (Level-2 after 5 cycles)")
    paper = {"Llama-33": (120, 42, 18), "Qwen-25C": (145, 23, 12),
             "Qwen-3C": (118, 43, 19), "GPT-OSS20": (78, 86, 16),
             "GPT-OSS120": (47, 96, 37), "GPT-5": (26, 48, 106),
             "Claude-S4": (29, 36, 115)}
    succ_cnt = {}
    for m in MODEL_ORDER:
        d = per[m]
        succ_cnt[m] = d.assign(ok=d["success_round"] <= 5).groupby("Prompt")["ok"].sum()
    print(f"  {'Model':<12}{'never':>7}{'pap':>6}{'1-9':>7}{'pap':>6}{'10/10':>7}{'pap':>6}   status")
    for m in MODEL_ORDER:
        c = succ_cnt[m]
        v = (int((c == 0).sum()), int(((c >= 1) & (c <= 9)).sum()), int((c == 10).sum()))
        p = paper.get(AB[m])
        if p is None:
            print(f"  {AB[m]:<12}{v[0]:>7}{'-':>6}{v[1]:>7}{'-':>6}{v[2]:>7}{'-':>6}   (not in paper)")
            continue
        print(f"  {AB[m]:<12}{v[0]:>7}{p[0]:>6}{v[1]:>7}{p[1]:>6}{v[2]:>7}{p[2]:>6}   "
              f"{check(v[0],p[0],0)} {check(v[1],p[1],0)} {check(v[2],p[2],0)}")

    # ------------------------------------------------------------ set overlaps
    header("SECTION 4.3  Never-solved / always-solved set sizes")
    never = {m: set(succ_cnt[m][succ_cnt[m] == 0].index) for m in MODEL_ORDER}
    always = {m: set(succ_cnt[m][succ_cnt[m] == 10].index) for m in MODEL_ORDER}
    inter = never[G5] & never[CS4]
    univ = set.intersection(*[never[m] for m in CORR_MODELS])
    for name, v, p in [
        ("|never GPT-5|", len(never[G5]), 26),
        ("|never Claude-S4|", len(never[CS4]), 29),
        ("|never GPT-5 and Claude-S4|", len(inter), 22),
        ("universally unsolved (7 models)", len(univ), 20),
        ("  as % of 180", len(univ) / 1.8, 11.1),
        ("of the intersection, solved by another model", len(inter - univ), 2),
        ("|always GPT-5|", len(always[G5]), 106),
        ("|always Claude-S4|", len(always[CS4]), 115),
        ("|always GPT-5 and Claude-S4|", len(inter and always[G5] & always[CS4]), 88),
        ("sometimes solved GPT-5 (1-9/10)", int(((succ_cnt[G5] >= 1) & (succ_cnt[G5] <= 9)).sum()), 48),
        ("sometimes solved Claude-S4 (1-9/10)", int(((succ_cnt[CS4] >= 1) & (succ_cnt[CS4] <= 9)).sum()), 36),
    ]:
        print(f"  {name:<46}{v:>8.4g}  paper {p:>5}   {check(v, p, 0.05)}")
    print(f"\n  tasks in (GPT-5 never & Claude never) but solved elsewhere: "
          f"{sorted(inter - univ)}")
    print(f"  GPT-5 tasks solved exactly 1/10: "
          f"{sorted(succ_cnt[G5][succ_cnt[G5] == 1].index)}")
    print(f"  Claude-S4 tasks solved exactly 1/10: "
          f"{sorted(succ_cnt[CS4][succ_cnt[CS4] == 1].index)}")

    # ---------------------------------------------------------------- T9/T10
    header("TABLES 9 & 10  Pairwise correlations")
    stab = pd.DataFrame({m: succ_cnt[m].apply(lambda c: 0 if c == 0 else (2 if c == 10 else 1))
                         for m in CORR_MODELS})
    rates = pd.DataFrame({m: succ_cnt[m] / 10.0 for m in CORR_MODELS})
    paper9 = {("Llama-33","Qwen-25C"):.56,("Llama-33","Qwen-3C"):.55,("Llama-33","GPT-OSS20"):.47,
              ("Llama-33","GPT-OSS120"):.50,("Llama-33","GPT-5"):.41,("Llama-33","Claude-S4"):.36,
              ("Qwen-25C","Qwen-3C"):.43,("Qwen-25C","GPT-OSS20"):.45,("Qwen-25C","GPT-OSS120"):.43,
              ("Qwen-25C","GPT-5"):.33,("Qwen-25C","Claude-S4"):.32,("Qwen-3C","GPT-OSS20"):.45,
              ("Qwen-3C","GPT-OSS120"):.40,("Qwen-3C","GPT-5"):.38,("Qwen-3C","Claude-S4"):.39,
              ("GPT-OSS20","GPT-OSS120"):.61,("GPT-OSS20","GPT-5"):.54,("GPT-OSS20","Claude-S4"):.40,
              ("GPT-OSS120","GPT-5"):.61,("GPT-OSS120","Claude-S4"):.51,("GPT-5","Claude-S4"):.58}
    paper10 = {("Llama-33","Qwen-25C"):.59,("Llama-33","Qwen-3C"):.60,("Llama-33","GPT-OSS20"):.61,
               ("Llama-33","GPT-OSS120"):.61,("Llama-33","GPT-5"):.43,("Llama-33","Claude-S4"):.38,
               ("Qwen-25C","Qwen-3C"):.45,("Qwen-25C","GPT-OSS20"):.54,("Qwen-25C","GPT-OSS120"):.52,
               ("Qwen-25C","GPT-5"):.34,("Qwen-25C","Claude-S4"):.33,("Qwen-3C","GPT-OSS20"):.55,
               ("Qwen-3C","GPT-OSS120"):.51,("Qwen-3C","GPT-5"):.41,("Qwen-3C","Claude-S4"):.42,
               ("GPT-OSS20","GPT-OSS120"):.73,("GPT-OSS20","GPT-5"):.60,("GPT-OSS20","Claude-S4"):.45,
               ("GPT-OSS120","GPT-5"):.70,("GPT-OSS120","Claude-S4"):.56,("GPT-5","Claude-S4"):.64}
    for label, table, pv_map, fn in [
        ("Table 9   Kendall tau-b on the 3-level stability class", stab, paper9, kendalltau),
        ("Table 10  Spearman rho on Level-2 success rates", rates, paper10, spearmanr),
    ]:
        print(f"\n  --- {label} ---")
        print(f"  {'pair':<26}{'recomputed':>11}{'paper':>7}{'p-value':>12}   status")
        vals, pmax = {}, 0.0
        for a, b in combinations(CORR_MODELS, 2):
            r, pv = fn(table[a], table[b])
            vals[(AB[a], AB[b])] = r
            pmax = max(pmax, pv)
            pp = pv_map.get((AB[a], AB[b]))
            print(f"  {AB[a]+' / '+AB[b]:<26}{r:>11.3f}{pp:>7.2f}{pv:>12.1e}   "
                  f"{check(r, pp, 0.005)}")
        lo = min(vals, key=vals.get)
        hi = max(vals, key=vals.get)
        print(f"  min = {vals[lo]:.3f} ({lo[0]} / {lo[1]}),  "
              f"max = {vals[hi]:.3f} ({hi[0]} / {hi[1]}),  "
              f"largest p = {pmax:.2e},  Bonferroni alpha = {0.05/21:.5f}")

    # ----------------------------------------------------------------- T11
    header("TABLE 11  Tasks never solved by either GPT-5 or Claude-S4, per category")
    paper = {"String Handling": 5, "List or Array Operation": 21,
             "Mathematical Calculation": 13, "Logical Condition": 13,
             "ABAP Database Operation": 1}
    print(f"  {'Category':<28}{'never':>7}{'pap':>5}{'total':>7}{'pct':>8}"
          f"{'univ':>7}{'univ%':>8}   status")
    for c in CATS:
        ic = set(tasks.index[tasks[c]])
        n, u, t = len(inter & ic), len(univ & ic), len(ic)
        print(f"  {c:<28}{n:>7}{paper[c]:>5}{t:>7}{n/t*100:>7.1f}%"
              f"{u:>7}{u/t*100:>7.1f}%   {check(n, paper[c], 0)}")
    print("\n  'univ' = the 20 tasks unsolved by every model; section 4.3 quotes "
          "17.6% (19/108)\n  from this column but compares it against the 6.6% "
          "and 10.4% of the 'never' column.")

    # -------------------------------------------------------------- Figure 5
    header("FIGURE 5 / SECTION 4.3  Level-2 success rate p2@1(5) by category")
    print(f"  {'Model':<12}" + "".join(f"{c[:12]:>14}" for c in CATS))
    for m in MODEL_ORDER:
        d = per[m]
        print(f"  {AB[m]:<12}" +
              "".join(f"{(d[d[c]]['success_round'] <= 5).mean()*100:>13.1f}%" for c in CATS))
    print("\n  paper: GPT-5 68.1% (TA) .. 81.8% (TS); "
          "Claude-S4 'even smaller variation', 64.0% (TL) .. 66.3% (TA)")

    # -------------------------------------------------------------- Figure 6
    header("FIGURE 6 / SECTION 4.4  Final execution state (% of all 1800 trials)")
    stages = ["success", "syntax", "unittest", "class"]
    print(f"  {'Model':<12}" + "".join(f"{g:>13}" for g in stages) +
          f"{'class|failed':>14}")
    for m in MODEL_ORDER:
        st = per[m]["final_stage"]
        failed = st[st != "success"]
        cf = (failed == "class").mean() * 100 if len(failed) else 0.0
        print(f"  {AB[m]:<12}" + "".join(f"{(st == g).mean()*100:>12.1f}%" for g in stages) +
              f"{cf:>13.1f}%")
    print("\n  fine-grained terminating message (% of all trials):")
    events = sorted(df["final_event"].unique())
    print(f"  {'Model':<12}" + "".join(f"{e[:11]:>13}" for e in events))
    for m in MODEL_ORDER:
        fe = per[m]["final_event"]
        print(f"  {AB[m]:<12}" + "".join(f"{(fe == e).mean()*100:>12.1f}%" for e in events))
    print("\n  paper: Code-22 93.9% of failed trials end at class creation; "
          "GPT-5 17.9% syntax / 4.9%\n  unit test; Claude-S4 18.9% / 6.4%")

    # ----------------------------------------------------------------- T12
    header("TABLE 12  Distribution of categorised syntax errors")
    paper = {"Llama-33": (25.6, 23.3, 6.6, 13.1, 31.3), "Code-22": (0.4, 38.9, 0.0, 0.0, 60.8),
             "Qwen-25C": (51.0, 9.9, 17.8, 7.4, 14.0), "Qwen-3C": (46.0, 9.3, 23.3, 7.2, 14.1),
             "GPT-OSS20": (48.1, 12.7, 13.2, 5.3, 20.7), "GPT-OSS120": (39.3, 8.4, 3.1, 4.5, 44.7),
             "GPT-5": (41.4, 6.3, 7.5, 1.8, 43.0), "Claude-S4": (16.6, 9.1, 55.2, 5.9, 13.3)}
    with open(os.path.join(DATA, "syntax_errors.json")) as f:
        se = json.load(f)
    all_cats = sorted({c for m in se for c in se[m]})
    order = ["Lexical and Token Errors", "Structural and Formatting Errors",
             "Type and Conversion Errors", "OOP Errors", "Declaration Errors"]
    order = [c for c in order if c in all_cats] + \
            [c for c in all_cats if c not in order and c != "Uncategorized"]
    print("  categories in syntax_errors.json:", all_cats)
    print(f"\n  {'Model':<12}" + "".join(f"{c[:11]:>18}" for c in order) +
          f"{'n':>8}{'catch-all':>11}   status")
    for m in MODEL_ORDER:
        cnt = {c: sum(len(v) for v in se.get(m, {}).get(c, {}).values()) for c in all_cats}
        tot = sum(cnt[c] for c in order)
        catch = len(se.get(m, {}).get("Declaration Errors", {}).get(".*", []))
        vals = [cnt[c] / tot * 100 if tot else 0.0 for c in order]
        # 0.1 pp = one unit in the last printed digit; the two recovered
        # patterns are inferred, so a single-count difference is expected.
        st = " ".join(check(v, pv, 0.1) for v, pv in zip(vals, paper[AB[m]]))
        print(f"  {AB[m]:<12}" +
              "".join(f"{v:>8.1f}/{pv:<9.1f}" for v, pv in zip(vals, paper[AB[m]])) +
              f"{tot:>8}{catch:>11}   {st}")
    print("\n  'catch-all' counts errors matched only by the Error(\"Other\", \".*\") rule at the\n"
          "  end of Declaration Errors; they inflate that column and are not really\n"
          "  declaration errors. Syntax-check warnings (type \"W\") are excluded, as in the paper.")

    # ----------------------------------------------------------------- T13
    header("TABLE 13  Median code-size metrics")
    paper = {"Llama-33": (375, 30, 28, 22, 0.81), "Code-22": (0, None, None, None, None),
             "Qwen-25C": (234, 38, 29, 20, 0.84), "Qwen-3C": (377, 40, 31, 22, 0.90),
             "GPT-OSS20": (528, 31, 29, 23, 0.84), "GPT-OSS120": (831, 32, 30, 24, 0.87),
             "GPT-5": (1388, 36, 33, 27, 0.96), "Claude-S4": (1344, 50, 37, 26, 1.07),
             "Baseline": (180, 44, 34, 24, 1.00)}
    cs = pd.read_csv(os.path.join(DATA, "code_size_metrics.csv")).set_index("Model")
    print(f"  {'Model':<12}{'N':>6}{'pap':>6}{'LOC':>6}{'pap':>5}{'SLOC':>6}{'pap':>5}"
          f"{'LLOC':>6}{'pap':>5}{'ratio':>8}{'pap':>6}   status")
    for m in MODEL_ORDER + ["Baseline"]:
        name = "Baseline" if m == "Baseline" else AB[m]
        if m not in cs.index:
            print(f"  {name:<12}missing from code_size_metrics.csv")
            continue
        r = cs.loc[m]
        v = (r["N"], r["Median LOC"], r["Median SLOC"], r["Median LLOC"], r["SLOC vs Baseline"])
        p = paper[name]
        st = " ".join(check(v[i], p[i], (0, .5, .5, .5, .006)[i]) for i in range(5))
        f = lambda x: "-" if pd.isna(x) else f"{x:.0f}"
        print(f"  {name:<12}{v[0]:>6.0f}{p[0]:>6}{f(v[1]):>6}{str(p[1]):>5}{f(v[2]):>6}"
              f"{str(p[2]):>5}{f(v[3]):>6}{str(p[3]):>5}{v[4]:>8.3f}{str(p[4]):>6}   {st}")
    print(f"\n  baseline median SLOC is {cs.loc['Baseline','Median SLOC']:.1f}, "
          f"printed as 34 in the paper;\n  the ratio column divides by the unrounded value.")
    print("  N should equal Level-2 successes after 5 cycles:")
    for m in MODEL_ORDER:
        n2 = int((per[m]["success_round"] <= 5).sum())
        print(f"    {AB[m]:<12}{n2:>6}   csv N = {int(cs.loc[m,'N']) if m in cs.index else '-':>6}   "
              f"{check(int(cs.loc[m,'N']) if m in cs.index else None, n2, 0)}")

    # ---------------------------------------------------------------- text
    header("OTHER NUMERIC CLAIMS IN THE TEXT")
    g5_0, g5_2 = p_at_1(G5, "l1_round", 0), p_at_1(G5, "l1_round", 2)
    for name, v, p in [
        ("T x M x (N+1)", 180 * 10 * 6, 10800),
        ("GPT-5 p1@1(2)", g5_2, 52.8),
        ("GPT-5 p1@1(2)/p1@1(0)", g5_2 / g5_0, 2.7),
        ("GPT-OSS120 p1@1(2)", p_at_1("gpt-oss_120b", "l1_round", 2), 26.0),
        ("GPT-OSS120 p1@1(5)", p_at_1("gpt-oss_120b", "l1_round", 5), 39.6),
        ("1 - p2@10(5) GPT-5", 100 - p_at_10(G5, "success_round", 5), 13.9),
        ("1 - p2@10(5) Claude-S4", 100 - p_at_10(CS4, "success_round", 5), 15.6),
        ("Llama-33 p1@1(5)", p_at_1("llama-3.3-70b-instruct", "l1_round", 5), 16.4),
        ("GPT-OSS20 p1@1(5)", p_at_1("gpt-oss_20b", "l1_round", 5), 26.0),
    ]:
        print(f"  {name:<32}{v:>10.2f}  paper {p:>7}   {check(v, p, 0.06)}")


if __name__ == "__main__":
    main()
