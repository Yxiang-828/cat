"""
analysis_2_spearman.py
Script 2 — Spearman's Rank Correlation Analysis

Tests all 4 pairs from the problem statement:
  1. Q4 Noise rating ↔ Q7 Concentration impact   (Chain 1→2)
  2. Q4 Noise rating ↔ Q11 QoL                   (Chain 2→3)
  3. Q8 Air quality  ↔ Q11 QoL                   (supporting)
  4. Q4 Noise rating ↔ Q8 Air quality             (co-location)

Outputs:
  - Console table with ρ, p-value, interpretation
  - Scatter plots with Spearman ρ annotated → ./charts/spearman_*.png

Run AFTER create_clean_csv.py
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(__file__)
CSV    = os.path.join(BASE, "survey_clean.csv")
OUTDIR = os.path.join(BASE, "charts")
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(CSV)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size":   11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

SITE_COLORS = {
    "Waterloo Centre":   "#4e79a7",
    "Cheng Yan Court":   "#e15759",
    "Albert Centre":     "#59a14f",
    "Bras Basah Complex":"#f28e2b",
}

# ── Axis labels (for plots) ────────────────────────────────────────────────────
LABELS = {
    "Q4_noise_rating":   "Q4 Noise Rating (1=Quiet → 10=Loud)",
    "Q7_concentration":  "Q7 Concentration Impact\n(1=Not at all → 6=Severely affects rest)",
    "Q8_air_quality":    "Q8 Air Quality (1=Poor → 10=Excellent)",
    "Q11_QoL":           "Q11 Quality of Life\n(1=Improves significantly → 4=Reduces significantly)",
}

# ── Pairs to test ──────────────────────────────────────────────────────────────
PAIRS = [
    ("Q4_noise_rating", "Q7_concentration",
     "Chain 1→2: Noise Level vs Concentration Impact",
     "spearman_Q4_Q7.png"),
    ("Q4_noise_rating", "Q11_QoL",
     "Chain 2→3: Noise Level vs Quality of Life",
     "spearman_Q4_Q11.png"),
    ("Q8_air_quality",  "Q11_QoL",
     "Supporting: Air Quality vs Quality of Life",
     "spearman_Q8_Q11.png"),
    ("Q4_noise_rating", "Q8_air_quality",
     "Co-location: Noise Level vs Air Quality",
     "spearman_Q4_Q8.png"),
]


def interpret(rho, p, n=20):
    """Short plain-English interpretation."""
    sig = p < 0.05
    if abs(rho) >= 0.7:
        strength = "strong"
    elif abs(rho) >= 0.4:
        strength = "moderate"
    else:
        strength = "weak"
    direction = "positive" if rho > 0 else "negative"
    sig_str   = "statistically significant" if sig else "not statistically significant"
    caveat    = f" (⚠ n={n}: treat as indicative)" if not sig else ""
    return f"{strength} {direction} correlation, {sig_str}{caveat}"


def scatter_spearman(xvar, yvar, title, fname, rho, p):
    x = df[xvar]
    y = df[yvar]

    fig, ax = plt.subplots(figsize=(6.5, 5))

    for site, grp in df.groupby("site"):
        ax.scatter(grp[xvar], grp[yvar],
                   color=SITE_COLORS.get(site, "grey"),
                   s=70, alpha=0.85, edgecolors="white", linewidths=0.6,
                   label=site)

    # Trend line
    z   = np.polyfit(x, y, 1)
    xlo, xhi = x.min() - 0.3, x.max() + 0.3
    xs  = np.linspace(xlo, xhi, 200)
    ax.plot(xs, np.polyval(z, xs), color="#555555", lw=1.4,
            linestyle="--", alpha=0.7)

    # Annotation box
    sig_str = "p < 0.05 ✓" if p < 0.05 else f"p = {p:.3f}"
    ax.text(0.97, 0.05,
            f"Spearman ρ = {rho:+.3f}\n{sig_str}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="#cccccc", alpha=0.9))

    ax.set_xlabel(LABELS[xvar], labelpad=8)
    ax.set_ylabel(LABELS[yvar], labelpad=8)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.7)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.tight_layout()
    path = os.path.join(OUTDIR, fname)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {fname}")


# ── Run all pairs ──────────────────────────────────────────────────────────────
print("=" * 65)
print("SPEARMAN'S RANK CORRELATION RESULTS")
print("=" * 65)
print(f"{'Pair':<35} {'ρ':>7} {'p':>8}  Interpretation")
print("-" * 90)

results = []
for xvar, yvar, title, fname in PAIRS:
    sub = df[[xvar, yvar]].dropna()
    rho, p = stats.spearmanr(sub[xvar], sub[yvar])
    interp = interpret(rho, p, n=len(sub))
    print(f"{title:<35} {rho:>+7.3f} {p:>8.4f}  {interp}")
    results.append((xvar, yvar, title, fname, rho, p, interp))
    scatter_spearman(xvar, yvar, title, fname, rho, p)

print("-" * 90)
print("\nNote: n=20 overall; subgroups may be smaller after dropna.")
print("All Spearman scatter plots saved to ./charts/")

# ── Detailed narrative ─────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("DETAILED FINDINGS")
print("=" * 65)
for xvar, yvar, title, fname, rho, p, interp in results:
    print(f"\n[{title}]")
    print(f"  ρ = {rho:+.3f}, p = {p:.4f}")
    print(f"  → {interp}")
    if p < 0.05:
        print("  → This pair supports a statistically significant association.")
    else:
        print("  → Result is indicative only; do NOT over-claim given n=20.")
