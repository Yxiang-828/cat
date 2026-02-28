"""
analysis_final.py
─────────────────────────────────────────────────────────────────────────
Two sections:

  A) CORRELATIONS — where a logical X→Y pair exists
       Q4 (noise) ↔ Q7 (distraction / rest impact)
       Q4 (noise) ↔ Q11 (QoL)
       Q8 (air)   ↔ Q11 (QoL)
       Q10 (community) ↔ Q11 (QoL)
     → ρ magnitudes shown side-by-side so you can compare at a glance

  B) INDIVIDUAL DISTRIBUTIONS — variables with no natural pairing
       Q5 main noise sources  (horizontal bar)
       Q6 noise spike         (bar)

Run AFTER create_clean_csv.py
─────────────────────────────────────────────────────────────────────────
"""

import os, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

warnings.filterwarnings("ignore")

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

def save(name):
    p = os.path.join(OUTDIR, name)
    plt.tight_layout()
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓  {name}")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION A — CORRELATIONS
# ═══════════════════════════════════════════════════════════════════════════

PAIRS = [
    # (x_col,              y_col,             label_x,            label_y,                    group,       color)
    ("Q4_noise_rating",  "Q7_concentration", "Q4 Noise Level",   "Q7 Distraction/Rest Impact","Noise",     "#e15759"),
    ("Q4_noise_rating",  "Q11_QoL",          "Q4 Noise Level",   "Q11 Quality of Life",       "Noise",     "#c1121f"),
    ("Q8_air_quality",   "Q11_QoL",          "Q8 Air Quality",   "Q11 Quality of Life",       "Air",       "#f28e2b"),
    ("Q10_community",    "Q11_QoL",          "Q10 Community",    "Q11 Quality of Life",       "Community", "#59a14f"),
]

Q7_YTICKS = {1:"Not at all",2:"Neutral",3:"Slightly",4:"Moderately",5:"Highly",6:"Severely"}
Q11_YTICKS = {1:"Improves\nsig.",2:"Neutral",3:"Reduces\nsl.",4:"Reduces\nsig."}
Q10_XTICKS = {0:"No",1:"Maybe/\nNeutral",2:"Yes"}

SITE_COLORS = {
    "Waterloo Centre":    "#4e79a7",
    "Cheng Yan Court":    "#e15759",
    "Albert Centre":      "#59a14f",
    "Bras Basah Complex": "#f28e2b",
}

print("=" * 60)
print("SECTION A — SPEARMAN CORRELATIONS")
print("=" * 60)

rho_records = []

# ── 4 scatter plots in a 2×2 grid ──────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 10))
axes = axes.flatten()

for idx, (xv, yv, xlbl, ylbl, grp, col) in enumerate(PAIRS):
    ax = axes[idx]
    sub = df[[xv, yv, "site"]].dropna()
    rho, p = stats.spearmanr(sub[xv], sub[yv])
    sig_str = "p < 0.001" if p < 0.001 else (f"p = {p:.3f}" + (" ✓" if p < 0.05 else " (ns)"))

    # scatter, coloured by site
    for site, grpdf in sub.groupby("site"):
        ax.scatter(grpdf[xv], grpdf[yv],
                   color=SITE_COLORS.get(site, "#aaa"), s=65,
                   alpha=0.85, edgecolors="white", lw=0.5, label=site)

    # trend line
    z  = np.polyfit(sub[xv], sub[yv], 1)
    xs = np.linspace(sub[xv].min() - 0.2, sub[xv].max() + 0.2, 200)
    ax.plot(xs, np.polyval(z, xs), "--", color="#444", lw=1.4, alpha=0.65)

    # annotation
    ax.text(0.97, 0.05,
            f"Spearman ρ = {rho:+.3f}\n{sig_str}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="#ccc", alpha=0.92))

    ax.set_xlabel(xlbl, labelpad=6)
    ax.set_ylabel(ylbl, labelpad=6)
    title_color = col
    ax.set_title(f"[{grp}]  {xlbl}  →  {ylbl}",
                 fontweight="bold", fontsize=10.5, color=title_color, pad=10)

    # custom tick labels where useful
    if yv == "Q7_concentration":
        ax.set_yticks(list(Q7_YTICKS.keys()))
        ax.set_yticklabels(list(Q7_YTICKS.values()), fontsize=8)
    if yv == "Q11_QoL":
        ax.set_yticks(list(Q11_YTICKS.keys()))
        ax.set_yticklabels(list(Q11_YTICKS.values()), fontsize=8)
    if xv == "Q10_community":
        ax.set_xticks(list(Q10_XTICKS.keys()))
        ax.set_xticklabels(list(Q10_XTICKS.values()), fontsize=9)

    # legend only on first plot
    if idx == 0:
        ax.legend(loc="upper left", fontsize=7.5, framealpha=0.7)

    print(f"  [{grp}]  {xlbl} ↔ {ylbl}")
    print(f"         ρ = {rho:+.3f}   {sig_str}")
    rho_records.append((f"{xlbl}\n↔ {ylbl}", grp, rho, p, col))

plt.suptitle("Correlation Scatter Plots\n(Spearman ρ — coloured by site)",
             fontsize=13, fontweight="bold", y=1.01)
save("A_correlations_scatter.png")


# ── ρ magnitude comparison bar (the "noise wins" chart) ─────────────────────
fig, ax = plt.subplots(figsize=(9, 4.5))

labels_r = [r[0] for r in rho_records]
rhos_r   = [abs(r[2]) for r in rho_records]   # magnitude
ps_r     = [r[3] for r in rho_records]
cols_r   = [r[4] for r in rho_records]
grps_r   = [r[1] for r in rho_records]

order = sorted(range(len(rhos_r)), key=lambda i: rhos_r[i], reverse=True)
labels_r = [labels_r[i] for i in order]
rhos_r   = [rhos_r[i]   for i in order]
ps_r     = [ps_r[i]     for i in order]
cols_r   = [cols_r[i]   for i in order]
grps_r   = [grps_r[i]   for i in order]

bars = ax.barh(labels_r, rhos_r, color=cols_r, edgecolor="white", height=0.5)
for bar, rho_v, p_v, grp in zip(bars, rhos_r, ps_r, grps_r):
    sig = "✓ sig." if p_v < 0.05 else "ns"
    ax.text(rho_v + 0.01, bar.get_y() + bar.get_height() / 2,
            f"|ρ| = {rho_v:.3f}  [{grp}]  {sig}",
            va="center", fontsize=9.5, fontweight="bold")

ax.set_xlim(0, 1.15)
ax.set_xlabel("|Spearman ρ|  (correlation magnitude)")
ax.set_title("Correlation Magnitude Comparison\n"
             "Which factor has the strongest relationship with its paired outcome?",
             fontweight="bold")
ax.axvline(0.5, color="grey", lw=1, linestyle="--", alpha=0.5, label="ρ = 0.5 reference")
ax.legend(fontsize=9, framealpha=0.5)
ax.invert_yaxis()
save("A_rho_magnitude_comparison.png")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION B — INDIVIDUAL DISTRIBUTIONS (no natural pairing)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SECTION B — INDIVIDUAL DISTRIBUTIONS")
print("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# ── B1: Q5 Main noise sources ───────────────────────────────────────────────
ax = axes[0]
source_map = {
    "Road Traffic / MRT":        "Road Traffic / MRT",
    "Religious Activities":       "Religious Activities",
    "Commercial Events":          "Commercial Events\n(Busking, Festivals)",
    "Construction / Renovation":  "Construction /\nRenovation",
}
counts = {lbl: 0 for lbl in source_map.values()}
for src in df["Q5_noise_sources"]:
    for key, lbl in source_map.items():
        if key.lower() in str(src).lower():
            counts[lbl] += 1

pairs_b1 = sorted(counts.items(), key=lambda x: x[1])
lbls_b1, vals_b1 = zip(*pairs_b1)
bars_b1 = ax.barh(lbls_b1, vals_b1, color="#e15759", edgecolor="white", height=0.55)
ax.bar_label(bars_b1, padding=3, fontweight="bold")
ax.set_xlim(0, max(vals_b1) + 3)
ax.set_xlabel("Number of Respondents (multi-select)")
ax.set_title("[Noise]  Q5 — Main Noise Sources\n(n=20, multi-select)",
             fontweight="bold", color="#e15759")
print(f"  Q5 noise sources: {dict(zip(lbls_b1, vals_b1))}")

# ── B2: Q6 Noise spike ─────────────────────────────────────────────────────
ax = axes[1]
spike_counts = df["Q6_noise_spike"].value_counts().reindex([1, 0], fill_value=0)
spike_labels = ["Yes — noise spikes\nat specific times", "No — constant / baseline"]
spike_colors = ["#e15759", "#aaaaaa"]
bars_b2 = ax.bar(spike_labels, spike_counts.values,
                 color=spike_colors, edgecolor="white", width=0.45)
ax.bar_label(bars_b2, padding=3, fontweight="bold")
ax.set_ylim(0, spike_counts.max() + 4)
ax.set_ylabel("Number of Respondents")
ax.set_title("[Noise]  Q6 — Does Noise Spike at Specific Times?\n(n=20)",
             fontweight="bold", color="#e15759")
print(f"  Q6 spike: Yes={spike_counts[1]}, No={spike_counts[0]}")

save("B_individual_distributions.png")


# ── Console summary ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("RESULT SUMMARY")
print("=" * 60)
for lbl, grp, rho, p, _ in sorted(rho_records, key=lambda x: -abs(x[2])):
    sig = "✓ SIGNIFICANT" if p < 0.05 else "not significant"
    print(f"  [{grp}]  ρ={rho:+.3f}  {sig}   {lbl.replace(chr(10),' ')}")

print("""
Charts saved to ./charts/:
  A_correlations_scatter.png       — 4 scatter plots, one per pair
  A_rho_magnitude_comparison.png   — bar chart comparing all ρ magnitudes
  B_individual_distributions.png   — Q5 noise sources + Q6 spike
""")
