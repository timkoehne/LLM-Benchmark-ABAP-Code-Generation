import numpy as np
import matplotlib.pyplot as plt

COLORS = [
    '#A9D6E5',
    '#89C2D9',
    '#61A5C2',
    '#468FAF',
    '#2C7DA0',
    '#2A6F97',
    '#014F86',
    '#012A4A'
]

KM_COLORS = COLORS
LINE_STYLES = ['-', '--', '-.', ':']

def apply_plot_style():
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 13,
        'lines.linewidth': 2.5,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'axes.grid.axis': 'y',
        'grid.alpha': 0.3,
        'grid.linestyle': '--'
    })

MODEL_ABBREVIATIONS = {
    'llama-3.3-70b-instruct': 'Llama-33',
    'codestral-22b': 'Code-22',
    'qwen2.5-coder-32b-instruct': 'Qwen-25C',
    'qwen3-coder': 'Qwen-3C',
    'gpt-oss_20b': 'GPT-OSS20',
    'gpt-oss_120b': 'GPT-OSS120',
    'gpt-5-2025-08-07': 'GPT-5',
    'claude-sonnet-4-20250514': 'Claude-S4'
}


def wilson_halfwidths(p_percent, n, z=1.959963984540054):
    """Asymmetric 95% Wilson score half-widths, in percentage points.

    Returns (lower, upper) suitable for matplotlib's yerr.  The captions of
    Figures 3 and 5 specify the Wilson interval; the Wald interval that was
    used before collapses to zero width at p = 0, which is why models with no
    successes showed no error bar at all.
    """
    p_percent = np.asarray(p_percent, dtype=float)
    n = np.asarray(n, dtype=float)
    p = p_percent / 100.0
    with np.errstate(divide="ignore", invalid="ignore"):
        denom = 1 + z * z / n
        centre = (p + z * z / (2 * n)) / denom
        half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
        lo = np.clip(centre - half, 0, 1)
        hi = np.clip(centre + half, 0, 1)
    # clamp: at p = 0 the two bounds coincide and float error can make the
    # half-width a tiny negative number, which matplotlib rejects.
    lo = np.maximum(np.where(n > 0, (p - lo) * 100, 0.0), 0.0)
    hi = np.maximum(np.where(n > 0, (hi - p) * 100, 0.0), 0.0)
    return np.vstack([lo, hi])
