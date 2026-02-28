"""
analysis_1_descriptives.py
Script 1 — Descriptive Statistics + Demographic / Scene-setter Charts

Charts produced (saved to ./charts/):
  1. Age group distribution (Pie)
  2. Residency duration (Bar)
  3. Floor level distribution (Bar)
  4. Site distribution (Pie)
  5. Main noise sources Q5 (Horizontal Bar — multi-choice split)
  6. QoL outcome Q11 (Bar)

Run AFTER create_clean_csv.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

# ── Config ─────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(__file__)
CSV    = os.path.join(BASE, "survey_clean.csv")
OUTDIR = os.path.join(BASE, "charts")
os.makedirs(OUTDIR, exist_ok=True)

PALETTE = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
           "#59a14f", "#edc948", "#b07aa1", "#ff9da7"]

plt.rcParams.update({
    "font.family":  "DejaVu Sans",
    "font.size":    11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

df = pd.read_csv(CSV)

# ── Helper ─────────────────────────────────────────────────────────────────────
def save(name):
    path = os.path.join(OUTDIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {name}")


# ══════════════════════════════════════════════════════════════════════════════
# 1. Age group — Pie
# ══════════════════════════════════════════════════════════════════════════════
age_order = ["18 – 25", "26 – 40", "41 – 59", "60+"]
age_counts = df["age_group"].value_counts().reindex(age_order, fill_value=0)

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    age_counts,
    labels=age_counts.index,
    autopct="%1.0f%%",
    colors=PALETTE[:len(age_counts)],
    startangle=140,
    pctdistance=0.75,
)
for t in autotexts:
    t.set_fontweight("bold")
ax.set_title("Age Group Distribution\n(n = 20)", fontsize=13, fontweight="bold", pad=15)
save("1_age_distribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Residency duration — Bar
# ══════════════════════════════════════════════════════════════════════════════
dur_order  = ["Less than 1 year", "1 - 5 years", "5 - 10 years", "More than 10 years"]
dur_counts = df["residency_duration"].value_counts().reindex(dur_order, fill_value=0)

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(dur_counts.index, dur_counts.values, color=PALETTE[1], edgecolor="white", width=0.55)
ax.bar_label(bars, padding=3, fontweight="bold")
ax.set_title("Residency Duration of Respondents\n(n = 20)", fontsize=13, fontweight="bold")
ax.set_ylabel("Number of Respondents")
ax.set_xlabel("")
ax.set_ylim(0, dur_counts.max() + 3)
plt.xticks(rotation=15, ha="right")
save("2_residency_duration.png")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Floor level — Bar
# ══════════════════════════════════════════════════════════════════════════════
floor_order  = ["Low Rise (Floors 1–5)", "Mid Rise (Floors 6–10)", "High Rise (Floors 11+)"]
floor_counts = df["floor_level"].value_counts().reindex(floor_order, fill_value=0)

fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(floor_counts.index, floor_counts.values, color=PALETTE[2], edgecolor="white", width=0.55)
ax.bar_label(bars, padding=3, fontweight="bold")
ax.set_title("Floor Level Distribution\n(n = 20)", fontsize=13, fontweight="bold")
ax.set_ylabel("Number of Respondents")
ax.set_ylim(0, floor_counts.max() + 3)
plt.xticks(rotation=10, ha="right")
save("3_floor_distribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# 4. Site distribution — Pie
# ══════════════════════════════════════════════════════════════════════════════
site_counts = df["site"].value_counts()

fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    site_counts,
    labels=site_counts.index,
    autopct="%1.0f%%",
    colors=PALETTE[3:3+len(site_counts)],
    startangle=90,
    pctdistance=0.78,
)
for t in autotexts:
    t.set_fontweight("bold")
ax.set_title("Site Distribution\n(n = 20, 5 per site)", fontsize=13, fontweight="bold", pad=15)
save("4_site_distribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# 5. Noise sources Q5 — Horizontal Bar (multi-choice)
# ══════════════════════════════════════════════════════════════════════════════
source_keywords = {
    "Road Traffic / MRT":              "Road Traffic / MRT",
    "Religious Activities":            "Religious Activities",
    "Commercial Events":               "Commercial Events\n(Busking, Festivals)",
    "Construction / Renovation":       "Construction / Renovation",
}

counts = {label: 0 for label in source_keywords.values()}
for src in df["Q5_noise_sources"]:
    for key, label in source_keywords.items():
        if key.lower() in src.lower():
            counts[label] += 1

labels  = list(counts.keys())
values  = list(counts.values())
sorted_pairs = sorted(zip(values, labels))
values, labels = zip(*sorted_pairs)

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.barh(labels, values, color=PALETTE[0], edgecolor="white", height=0.55)
ax.bar_label(bars, padding=3, fontweight="bold")
ax.set_title("Main Noise Sources Identified (Q5)\n(multi-select, n = 20)", fontsize=13, fontweight="bold")
ax.set_xlabel("Number of Respondents")
ax.set_xlim(0, max(values) + 3)
save("5_noise_sources_Q5.png")

# ══════════════════════════════════════════════════════════════════════════════
# 6. QoL outcome Q11 — Bar
# ══════════════════════════════════════════════════════════════════════════════
qol_order  = ["Improves significantly", "Neutral", "Reduces slightly", "Reduces significantly"]
qol_colors = ["#59a14f", "#bab0ac", "#f28e2b", "#e15759"]
qol_counts = df["Q11_QoL_raw"].value_counts().reindex(qol_order, fill_value=0)

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(qol_counts.index, qol_counts.values,
              color=qol_colors[:len(qol_counts)], edgecolor="white", width=0.55)
ax.bar_label(bars, padding=3, fontweight="bold")
ax.set_title("Overall Quality of Life Perception (Q11)\n(n = 20)", fontsize=13, fontweight="bold")
ax.set_ylabel("Number of Respondents")
ax.set_ylim(0, qol_counts.max() + 2)
plt.xticks(rotation=10, ha="right")
save("6_QoL_Q11.png")

# ══════════════════════════════════════════════════════════════════════════════
# Print summary table
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*55)
print("DESCRIPTIVE SUMMARY")
print("="*55)
print(f"\nTotal respondents : {len(df)}")
print(f"Sites             : {df['site'].nunique()} (n=5 each)")

print("\n── Q4 Noise Rating (1–10) ──")
print(df["Q4_noise_rating"].describe().round(2).to_string())

print("\n── Q8 Air Quality (1–10) ──")
print(df["Q8_air_quality"].describe().round(2).to_string())

print("\n── Q7 Concentration Impact (encoded 1–6) ──")
print(df["Q7_concentration"].describe().round(2).to_string())

print("\n── Q11 QoL (encoded 1–4) ──")
print(df["Q11_QoL"].describe().round(2).to_string())

print("\n── Site × Q4 Noise Mean ──")
print(df.groupby("site")["Q4_noise_rating"].mean().round(2).to_string())

print("\nAll charts saved to ./charts/")
