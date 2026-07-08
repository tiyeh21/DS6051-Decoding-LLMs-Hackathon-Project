import pandas as pd
import json

bios = pd.read_csv("nba_player_bios.csv")
stats = pd.read_csv("nba_player_stats.csv")

# tier proxy: peak points-per-game across any season = rough fame/signal-strength indicator
peak_ppg = stats.groupby("PLAYER_ID")["PTS"].max().rename("peak_ppg")
bios = bios.merge(peak_ppg, left_on="PERSON_ID", right_index=True, how="left")
bios["tier"] = bios["peak_ppg"].apply(lambda x: "star" if pd.notna(x) and x >= 20 else "role_player")

# nba_api tags pre-college schools with HS / prep-academy keywords. A plain
# "(XX)" state suffix is NOT a reliable trap signal --- real universities like
# "St. John's (NY)" / "St. Joseph's (PA)" carry it too --- so match HS/prep
# keywords. Verified to catch only genuine pre-college schools for this cohort.
PRECOLLEGE_PAT = r"\bHS\b|Academy|Prep|High School"

# ---- Trap set: US high-school-only players, split by tier ----
hs_trap = bios[bios["SCHOOL"].str.contains(PRECOLLEGE_PAT, na=False, regex=True)]
trap_facts = []
for tier in ["star", "role_player"]:
    pool = hs_trap[hs_trap["tier"] == tier]
    for _, row in pool.sample(min(10, len(pool)), random_state=42).iterrows():
        trap_facts.append({
            "question": f"What college did {row['DISPLAY_FIRST_LAST']} attend before entering the NBA?",
            "ground_truth": "None — went pro directly from high school",
            "trap": True, "type": "trap", "tier": tier,
        })

# ---- College-string set: confirmed US college attendees, split by tier ----
college_pool = bios[~bios["SCHOOL"].str.contains(PRECOLLEGE_PAT, na=False, regex=True)]
college_pool = college_pool[college_pool["COUNTRY"] == "USA"]
college_facts = []
for tier in ["star", "role_player"]:
    pool = college_pool[college_pool["tier"] == tier]
    for _, row in pool.sample(min(10, len(pool)), random_state=42).iterrows():
        college_facts.append({
            "question": f"What college did {row['DISPLAY_FIRST_LAST']} attend before entering the NBA?",
            "ground_truth": row["SCHOOL"], "type": "string", "tier": tier,
        })

# ---- Numeric set: trade-valuation-relevant stats (PTS/AST/REB), split by tier ----
stats_tiered = stats.merge(bios[["PERSON_ID", "tier"]], left_on="PLAYER_ID", right_on="PERSON_ID", how="left")
stats_tiered = stats_tiered[stats_tiered["GP"] >= 20]  # avoid tiny-sample noise rows

stat_cols = ["PTS", "AST", "REB"]
stat_names = {"PTS": "points per game", "AST": "assists per game", "REB": "rebounds per game"}

numeric_facts = []
for tier in ["star", "role_player"]:
    pool = stats_tiered[stats_tiered["tier"] == tier]
    sample = pool.sample(min(10, len(pool)), random_state=42)
    for i, (_, row) in enumerate(sample.iterrows()):
        col = stat_cols[i % len(stat_cols)]
        numeric_facts.append({
            "question": f"How many {stat_names[col]} did {row['PLAYER_NAME']} average in the {row['SEASON']} season?",
            "ground_truth": str(row[col]), "type": "numeric", "tolerance": 0.5, "tier": tier,
        })

all_facts = trap_facts + college_facts + numeric_facts
with open("generated_facts.json", "w") as f:
    json.dump(all_facts, f, indent=2)

print(f"Total: {len(all_facts)} ({len(trap_facts)} trap, {len(college_facts)} college, {len(numeric_facts)} numeric)")
print(f"Star tier: {sum(1 for x in all_facts if x.get('tier')=='star')}, "
      f"Role-player tier: {sum(1 for x in all_facts if x.get('tier')=='role_player')}")
