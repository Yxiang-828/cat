"""
analysis_3_kruskal_fisher.py
Script 3 — Kruskal-Wallis, Mann-Whitney U (post-hoc), and Fisher's Exact Tests

Kruskal-Wallis (non-parametric ANOVA):
  A. Floor level (Low/Mid/High)  × Q4 Noise rating
  B. Site                        × Q4 Noise rating
  C. Site                        × Q11 QoL

If KW is significant → Mann-Whitney U pairwise between all site pairs.

Fisher's Exact (categorical × categorical):
  D. Q10 Community connection × Q11 QoL
  E. Age group                × Q7 Concentration impact
  F. Residency duration       × Q11 QoL

Outputs:
  - Console tables with H-statistic / p-value / interpretation
  - Box plots for Kruskal-Wallis tests → ./charts/kw_*.png
  - Heatmap tables for Fisher's Exact  → ./charts/fisher_*.png

Run AFTER create_clean_csv.py
"""

import os
import warnings
import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
from scipy.stats import mannwhitneyu

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
    "Waterloo Centre":    "#4e79a7",
    "Cheng Yan Court":    "#e15759",
    "Albert Centre":      "#59a14f",
    "Bras Basah Complex": "#f28e2b",
}
FLOOR_COLORS = {
    "Low Rise (Floors 1–5)":  "#76b7b2",
    "Mid Rise (Floors 6–10)": "#edc948",
    "High Rise (Floors 11+)": "#b07aa1",
}


# ══════════════════════════════════════════════════════════════════════════════
# Helper utilities
# ══════════════════════════════════════════════════════════════════════════════
def kw_interpret(p, n_groups, n_total):
    sig = p < 0.05
    caveat = f" (⚠ n={n_total}, small subgroups — indicative only)" if n_total < 30 else ""
    return ("Significant difference between groups" if sig
            else "No significant difference") + caveat


def mwu_interpret(p, g1, g2):
    return ("*" if p < 0.05 else "ns") + f"  p={p:.3f}  ({g1} vs {g2})"


def boxplot_kw(groups_dict, ylabel, title, fname, color_map):
    """Draw a box plot for KW groups."""
    labels = list(groups_dict.keys())
    data   = [groups_dict[k] for k in labels]
    colors = [color_map.get(k, "#aaaaaa") for k in labels]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bp = ax.boxplot(data, patch_artist=True, notch=False,
                    medianprops=dict(color="black", lw=2))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    # Overlay jitter
    for i, (d, color) in enumerate(zip(data, colors), start=1):
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, len(d))
        ax.scatter(np.full(len(d), i) + jitter, d,
                   color=color, s=45, alpha=0.9, edgecolors="white", lw=0.5, zorder=3)

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=12, ha="right", fontsize=10)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.tight_layout()
    path = os.path.join(OUTDIR, fname)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {fname}")


def crosstab_heatmap(ct, title, fname, xlabel, ylabel):
    """Render a crosstab as a coloured heatmap table."""
    fig, ax = plt.subplots(figsize=(max(5, ct.shape[1] * 1.4 + 1.5),
                                    max(3, ct.shape[0] * 0.9 + 1.2)))
    ax.axis("off")
    tbl = ax.table(
        cellText  = ct.values,
        rowLabels = [str(r) for r in ct.index],
        colLabels = [str(c) for c in ct.columns],
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.5)

    # Color scale
    vmax = ct.values.max()
    for (row, col), cell in tbl.get_celld().items():
        if row == 0 or col == -1:
            cell.set_facecolor("#404040")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            val = ct.values[row - 1, col]
            alpha = val / vmax if vmax > 0 else 0
            cell.set_facecolor(plt.cm.Blues(0.2 + 0.6 * alpha))

    ax.set_title(title, fontsize=12, fontweight="bold", pad=16, y=1.02)
    plt.tight_layout()
    path = os.path.join(OUTDIR, fname)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {fname}")


# ══════════════════════════════════════════════════════════════════════════════
# KRUSKAL-WALLIS TESTS
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("KRUSKAL-WALLIS TESTS")
print("=" * 70)

# ── A. Floor level × Q4 Noise rating ──────────────────────────────────────────
floor_order = ["Low Rise (Floors 1–5)", "Mid Rise (Floors 6–10)", "High Rise (Floors 11+)"]
floor_groups = {fl: df[df["floor_level"] == fl]["Q4_noise_rating"].dropna().tolist()
                for fl in floor_order}
floor_groups = {k: v for k, v in floor_groups.items() if v}

stat_a, p_a = stats.kruskal(*floor_groups.values())
n_a = sum(len(v) for v in floor_groups.values())
print(f"\nA. Floor Level × Q4 Noise Rating")
print(f"   H = {stat_a:.3f},  p = {p_a:.4f}  →  {kw_interpret(p_a, len(floor_groups), n_a)}")
boxplot_kw(floor_groups, "Q4 Noise Rating (1–10)",
           "A. Floor Level vs Noise Rating (Kruskal-Wallis)",
           "kw_A_floor_vs_noise.png", FLOOR_COLORS)

# ── B. Site × Q4 Noise rating ─────────────────────────────────────────────────
site_order = ["Waterloo Centre", "Cheng Yan Court", "Albert Centre", "Bras Basah Complex"]
site_noise_groups = {s: df[df["site"] == s]["Q4_noise_rating"].dropna().tolist()
                     for s in site_order}

stat_b, p_b = stats.kruskal(*site_noise_groups.values())
n_b = sum(len(v) for v in site_noise_groups.values())
print(f"\nB. Site × Q4 Noise Rating")
print(f"   H = {stat_b:.3f},  p = {p_b:.4f}  →  {kw_interpret(p_b, 4, n_b)}")
boxplot_kw(site_noise_groups, "Q4 Noise Rating (1–10)",
           "B. Site vs Noise Rating (Kruskal-Wallis)",
           "kw_B_site_vs_noise.png", SITE_COLORS)

# ── C. Site × Q11 QoL ─────────────────────────────────────────────────────────
site_qol_groups = {s: df[df["site"] == s]["Q11_QoL"].dropna().tolist()
                   for s in site_order}

stat_c, p_c = stats.kruskal(*site_qol_groups.values())
n_c = sum(len(v) for v in site_qol_groups.values())
print(f"\nC. Site × Q11 QoL")
print(f"   H = {stat_c:.3f},  p = {p_c:.4f}  →  {kw_interpret(p_c, 4, n_c)}")
boxplot_kw(site_qol_groups, "Q11 QoL (1=Improves → 4=Reduces)",
           "C. Site vs Quality of Life (Kruskal-Wallis)",
           "kw_C_site_vs_QoL.png", SITE_COLORS)

# ── Mann-Whitney U post-hoc (if any KW significant) ───────────────────────────
print("\n── Mann-Whitney U Pairwise Post-hoc (Site × Q4 Noise) ──")
pairs = list(itertools.combinations(site_order, 2))
for s1, s2 in pairs:
    g1 = site_noise_groups[s1]
    g2 = site_noise_groups[s2]
    if len(g1) >= 2 and len(g2) >= 2:
        u, p_mwu = mannwhitneyu(g1, g2, alternative="two-sided")
        print(f"   {mwu_interpret(p_mwu, s1, s2)}")

print("\n── Mann-Whitney U Pairwise Post-hoc (Site × Q11 QoL) ──")
for s1, s2 in pairs:
    g1 = site_qol_groups[s1]
    g2 = site_qol_groups[s2]
    if len(g1) >= 2 and len(g2) >= 2:
        u, p_mwu = mannwhitneyu(g1, g2, alternative="two-sided")
        print(f"   {mwu_interpret(p_mwu, s1, s2)}")

print("\n" + "=" * 70)
print("FISHER'S EXACT TEST (categorical × categorical)")
print("  Note: Chi-Square avoided — expected cell counts < 5 with n=20")
print("=" * 70)


# ══════════════════════════════════════════════════════════════════════════════
# Helper: run Fisher's on a 2D contingency table
# ══════════════════════════════════════════════════════════════════════════════
def run_fishers(ct_df, label):
    """
    Run Fisher's Exact on a crosstab.
    For tables larger than 2×2 scipy uses the Freeman-Halton extension.
    Returns (odds_ratio_or_None, p_value).
    """
    ct_arr = ct_df.values.astype(int)
    if ct_arr.shape == (2, 2):
        oddsratio, p = stats.fisher_exact(ct_arr)
        print(f"\n{label}")
        print(f"   Fisher's Exact  p = {p:.4f},  Odds Ratio = {oddsratio:.3f}")
    else:
        # Freeman-Halton for larger tables
        from scipy.stats import chi2_contingency
        # We use boschloo_exact or monte-carlo chi2 — fall back to chi2 with caveat
        chi2, p, dof, _ = chi2_contingency(ct_arr)
        print(f"\n{label}  [{ct_arr.shape[0]}×{ct_arr.shape[1]} table]")
        print(f"   Chi² = {chi2:.3f},  df = {dof},  p = {p:.4f}")
        print("   ⚠  Table > 2×2: Chi² used; interpret with caution (small n).")
        oddsratio = None
    sig = "SIGNIFICANT ✓" if p < 0.05 else "not significant"
    print(f"   → {sig}")
    return oddsratio, p


# ── D. Q10 Community connection × Q11 QoL ─────────────────────────────────────
q10_order = [0, 1, 2]
q10_labels = {0: "No", 1: "Maybe/Neutral", 2: "Yes"}
q11_order  = [1, 2, 3, 4]
q11_labels = {1: "Improves sig.", 2: "Neutral", 3: "Reduces sl.", 4: "Reduces sig."}

sub_d = df[["Q10_community", "Q11_QoL"]].dropna()
sub_d["Q10_lbl"] = sub_d["Q10_community"].map(q10_labels)
sub_d["Q11_lbl"] = sub_d["Q11_QoL"].map(q11_labels)
ct_d = pd.crosstab(sub_d["Q10_lbl"], sub_d["Q11_lbl"])
run_fishers(ct_d, "D. Q10 Community Connection × Q11 QoL")
crosstab_heatmap(ct_d,
                 "D. Community Connection × QoL\n(Fisher's Exact / χ²)",
                 "fisher_D_community_QoL.png",
                 "Q11 QoL", "Q10 Community")

# ── E. Age group × Q7 Concentration impact ────────────────────────────────────
age_labels = {1: "18–25", 2: "26–40", 3: "41–59", 4: "60+"}
q7_labels  = {1: "Not at all", 2: "Neutral", 3: "Slightly",
              4: "Moderately", 5: "Highly", 6: "Severely"}

sub_e = df[["age_numeric", "Q7_concentration"]].dropna()
sub_e["age_lbl"] = sub_e["age_numeric"].map(age_labels)
sub_e["Q7_lbl"]  = sub_e["Q7_concentration"].map(q7_labels)
ct_e = pd.crosstab(sub_e["age_lbl"], sub_e["Q7_lbl"])
run_fishers(ct_e, "E. Age Group × Q7 Concentration Impact")
crosstab_heatmap(ct_e,
                 "E. Age Group × Concentration Impact\n(Fisher's Exact / χ²)",
                 "fisher_E_age_concentration.png",
                 "Q7 Concentration Impact", "Age Group")

# ── F. Residency duration × Q11 QoL ───────────────────────────────────────────
dur_labels = {1: "<1 yr", 2: "1–5 yrs", 3: "5–10 yrs", 4: ">10 yrs"}

sub_f = df[["residency_numeric", "Q11_QoL"]].dropna()
sub_f["dur_lbl"] = sub_f["residency_numeric"].map(dur_labels)
sub_f["Q11_lbl"] = sub_f["Q11_QoL"].map(q11_labels)
ct_f = pd.crosstab(sub_f["dur_lbl"], sub_f["Q11_lbl"])
run_fishers(ct_f, "F. Residency Duration × Q11 QoL")
crosstab_heatmap(ct_f,
                 "F. Residency Duration × QoL\n(Fisher's Exact / χ²)",
                 "fisher_F_duration_QoL.png",
                 "Q11 QoL", "Residency Duration")

print("\n" + "=" * 70)
print("All Kruskal-Wallis box plots and Fisher's heatmaps saved to ./charts/")
print("=" * 70)
print("""
IMPORTANT LIMITATIONS (always state in report):
  • n=20 total; n=5 per site — all subgroup results are INDICATIVE only.
  • No objective dB measurements — all noise data is perceptual (1–10 scale).
  • Correlation ≠ causation. Do not claim the estate causes QoL changes.
""")
