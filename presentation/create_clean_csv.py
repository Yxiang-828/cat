"""
create_clean_csv.py
Generates survey_clean.csv from the raw Google Form export.
Run this FIRST before any analysis scripts.
"""

import csv, os

RAW = os.path.join(os.path.dirname(__file__),
                   "Site Analysis Google form  - Sheet1.csv")
OUT = os.path.join(os.path.dirname(__file__), "survey_clean.csv")

# ── Encoding maps ──────────────────────────────────────────────────────────────
Q7_MAP = {
    "not at all": 1,
    "neutral": 2,
    "slightly distracting": 3,
    "moderately distracting": 4,
    "highly distracting": 5,
    "severely affects rest quality": 6,
}

Q11_MAP = {
    "improves significantly": 1,
    "neutral": 2,
    "reduces slightly": 3,
    "reduces significantly": 4,
}

AGE_MAP = {
    "18 – 25": 1,
    "26 – 40": 2,
    "41 – 59": 3,
    "60+": 4,
}

DURATION_MAP = {
    "less than 1 year": 1,
    "1 - 5 years": 2,
    "5 - 10 years": 3,
    "more than 10 years": 4,
}

FLOOR_MAP = {
    "low rise (floors 1–5)": 1,
    "mid rise (floors 6–10)": 2,
    "high rise (floors 11+)": 3,
}

COMMUNITY_MAP = {
    "no": 0,
    "neutral": 1,
    "maybe": 1,          # treat maybe ≈ neutral for ordinal purposes
    "yes": 2,
    "yes, i feel a strong connection.": 2,
    "yes, very strong": 2,
}

NOISE_SPIKE_MAP = {
    "no": 0,
}  # anything non-"No" → 1


def encode(val: str, mapping: dict, default=None):
    return mapping.get(val.strip().lower(), default)


def noise_spike(val: str) -> int:
    return 0 if val.strip().lower() == "no" else 1


def main():
    rows_out = []
    with open(RAW, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            # Raw columns (strip to be safe)
            site      = row["12. Which site do you live in?"].strip()
            age_raw   = row["1. Which age group do you fall into?"].strip()
            dur_raw   = row["2. How long have you lived in this estate?"].strip()
            floor_raw = row["3. Which floor range is your unit located on?"].strip()
            q4        = row["4. On a normal day, how would you rate the noise level from 1 to 10?"].strip()
            q5        = row["5. What are the main noise sources you notice most often?"].strip()
            q6_raw    = row["6. Does the noise ever spike during specific hours / events?"].strip()
            q7_raw    = row["7. How does the noise level affect your ability to concentrate (studying, working)?"].strip()
            q8        = row["8. How do you find the quality of air in your living area?"].strip()
            q9_raw    = row["9. Convenience: When there are big festivals or religious practices, events etc, how does it affect your routine?"].strip()
            q10_raw   = row["10. Does living so close to these cultural/religious hubs make you feel more connected to the community?"].strip()
            q11_raw   = row["11. Overall, would you say living here improves or reduces your Quality of Life?"].strip()

            rows_out.append({
                "respondent_id":         idx,
                "site":                  site,
                "age_group":             age_raw,
                "age_numeric":           encode(age_raw, AGE_MAP),
                "residency_duration":    dur_raw,
                "residency_numeric":     encode(dur_raw, DURATION_MAP),
                "floor_level":           floor_raw,
                "floor_numeric":         encode(floor_raw, FLOOR_MAP),
                "Q4_noise_rating":       int(q4) if q4.isdigit() else None,
                "Q5_noise_sources":      q5,
                "Q6_noise_spike":        noise_spike(q6_raw),
                "Q6_spike_raw":          q6_raw,
                "Q7_concentration_raw":  q7_raw,
                "Q7_concentration":      encode(q7_raw, Q7_MAP),
                "Q8_air_quality":        int(q8) if q8.isdigit() else None,
                "Q9_convenience_raw":    q9_raw,
                "Q10_community_raw":     q10_raw,
                "Q10_community":         encode(q10_raw, COMMUNITY_MAP),
                "Q11_QoL_raw":           q11_raw,
                "Q11_QoL":               encode(q11_raw, Q11_MAP),
            })

    fieldnames = list(rows_out[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"✓  Written {len(rows_out)} rows → {OUT}")

    # ── Quick sanity check ─────────────────────────────────────────────────────
    print("\nSanity check — encoded values:")
    print(f"{'ID':>3}  {'Site':<22} {'Q4':>4} {'Q7':>4} {'Q8':>4} {'Q11':>4}")
    print("-" * 45)
    for r in rows_out:
        print(f"{r['respondent_id']:>3}  {r['site']:<22} "
              f"{str(r['Q4_noise_rating']):>4} "
              f"{str(r['Q7_concentration']):>4} "
              f"{str(r['Q8_air_quality']):>4} "
              f"{str(r['Q11_QoL']):>4}")


if __name__ == "__main__":
    main()
