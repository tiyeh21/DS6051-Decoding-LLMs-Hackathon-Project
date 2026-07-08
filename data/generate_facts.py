#!/usr/bin/env python3
"""Generate fact sets (trap + college + numeric) from the repo CSVs.

Pure pandas. Runs locally in a plain Python env or Jupyter — no GPU, no
HuggingFace, no login. Output is generated_facts.json, which you hand back
to be pasted into the notebook.

Usage:
    python data/generate_facts.py
"""
import pandas as pd
import re
import json

bios = pd.read_csv("nba_player_bios.csv")

# Part A --- trap questions from bio data -----------------------------------

# nba_api tags pre-college schools with HS / prep-academy keywords. NOTE: a
# plain "(XX)" state suffix is NOT a reliable trap signal --- real universities
# like "St. John's (NY)" and "St. Joseph's (PA)" carry it too --- so match on
# HS/prep keywords instead. Verified to catch only genuine pre-college schools
# for the USA cohort in this dataset.
PRECOLLEGE_PAT = r"\bHS\b|Academy|Prep|High School"


def school_stem(school: str) -> str:
    """'Oak Hill Academy (VA)' -> 'Oak Hill Academy' (drop trailing state paren)."""
    return re.sub(r"\s*\([A-Z]{2}\)\s*$", "", school).strip()


# Trap set: players who went pro with no college (US high school / prep)
hs_trap = bios[bios["SCHOOL"].str.contains(PRECOLLEGE_PAT, na=False, regex=True)]

trap_facts = []
for _, row in hs_trap.sample(min(10, len(hs_trap)), random_state=42).iterrows():
    trap_facts.append({
        "question": f"What college did {row['DISPLAY_FIRST_LAST']} attend before entering the NBA?",
        "ground_truth": "None — went pro directly from high school",
        "trap": True,
        "forbidden_terms": ["University", "College", "State", school_stem(row["SCHOOL"])],
        "type": "trap",
    })

# Positive set: players who DID attend a real university
college_facts_pool = bios[~bios["SCHOOL"].str.contains(PRECOLLEGE_PAT, na=False, regex=True)]
college_facts_pool = college_facts_pool[college_facts_pool["COUNTRY"] == "USA"]

college_facts = []
for _, row in college_facts_pool.sample(min(10, len(college_facts_pool)), random_state=42).iterrows():
    college_facts.append({
        "question": f"What college did {row['DISPLAY_FIRST_LAST']} attend before entering the NBA?",
        "ground_truth": row["SCHOOL"],
        "type": "string",
    })

# Part B --- numeric stat facts from per-game stats -------------------------

stats = pd.read_csv("nba_player_stats.csv")

# stick to PTS, AST, REB only --- safest columns, skip fantasy columns
stat_cols = ["PTS", "AST", "REB"]

# GP filter avoids tiny-sample noise rows
sample = stats[stats["GP"] >= 20].sample(15, random_state=42)

stat_facts = []
for _, row in sample.iterrows():
    col = stat_cols[len(stat_facts) % len(stat_cols)]  # rotate through the three columns
    stat_name = {"PTS": "points per game", "AST": "assists per game", "REB": "rebounds per game"}[col]
    stat_facts.append({
        "question": f"How many {stat_name} did {row['PLAYER_NAME']} average in the {row['SEASON']} season?",
        "ground_truth": str(row[col]),
        "type": "numeric",
        "tolerance": 0.5,
    })

all_facts = trap_facts + college_facts + stat_facts
with open("generated_facts.json", "w") as f:
    json.dump(all_facts, f, indent=2)

print(f"Generated {len(all_facts)} facts: {len(trap_facts)} trap, "
      f"{len(college_facts)} college, {len(stat_facts)} numeric")
