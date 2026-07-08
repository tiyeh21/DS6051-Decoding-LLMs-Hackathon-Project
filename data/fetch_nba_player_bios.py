#!/usr/bin/env python3
"""Fetch per-player biographical info via nba_api and save to CSV.

For every unique PLAYER_ID in data/nba_player_stats.csv, pulls the
CommonPlayerInfo endpoint (college/school, country, birthdate, height, weight,
position, draft info, experience, etc.) and writes:

  data/nba_player_bios.csv

The run is RESUMABLE and INCREMENTAL: results are appended to the CSV as they
arrive, and players already present are skipped on re-run. If stats.nba.com
rate-limits or the process dies, just run it again to finish.

Usage:
    python data/fetch_nba_player_bios.py
    python data/fetch_nba_player_bios.py --sleep 0.8

Note:
    Hometown / birth city is NOT exposed by nba_api. The closest available bio
    fields are BIRTHDATE + COUNTRY + SCHOOL (college). Those are included.

Requires: nba_api, pandas.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

try:
    from nba_api.stats.endpoints import commonplayerinfo
except ImportError:
    sys.exit("nba_api is not installed. Run: pip install nba_api")

DATA_DIR = Path(__file__).resolve().parent
STATS_CSV = DATA_DIR / "nba_player_stats.csv"
BIOS_CSV = DATA_DIR / "nba_player_bios.csv"

# Columns we keep from CommonPlayerInfo (subset of a wider response).
KEEP = [
    "PERSON_ID", "DISPLAY_FIRST_LAST", "BIRTHDATE", "COUNTRY",
    "SCHOOL", "LAST_AFFILIATION", "HEIGHT", "WEIGHT", "POSITION",
    "SEASON_EXP", "DRAFT_YEAR", "DRAFT_ROUND", "DRAFT_NUMBER",
    "FROM_YEAR", "TO_YEAR", "GREATEST_75_FLAG",
]


def already_fetched() -> set[int]:
    if not BIOS_CSV.exists():
        return set()
    done = pd.read_csv(BIOS_CSV)
    return set(done["PERSON_ID"].astype(int).tolist())


def fetch_one(player_id: int, sleep: float) -> pd.DataFrame | None:
    try:
        df = commonplayerinfo.CommonPlayerInfo(
            player_id=player_id, timeout=60
        ).get_data_frames()[0]
    except Exception as exc:  # network / rate-limit / missing player
        print(f"    !! {player_id}: {exc}", flush=True)
        return None
    finally:
        time.sleep(sleep)
    cols = [c for c in KEEP if c in df.columns]
    return df[cols]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sleep", type=float, default=0.6,
                   help="seconds to sleep between requests (default: 0.6)")
    args = p.parse_args()

    if not STATS_CSV.exists():
        sys.exit(f"{STATS_CSV} not found. Run fetch_nba_stats.py first.")

    ids = sorted(pd.read_csv(STATS_CSV)["PLAYER_ID"].astype(int).unique())
    done = already_fetched()
    todo = [pid for pid in ids if pid not in done]
    print(f"{len(ids)} unique players, {len(done)} already fetched, "
          f"{len(todo)} to go.")

    header_written = BIOS_CSV.exists()
    for i, pid in enumerate(todo, 1):
        row = fetch_one(pid, args.sleep)
        if row is None:
            continue
        row.to_csv(BIOS_CSV, mode="a", index=False, header=not header_written)
        header_written = True
        if i % 25 == 0 or i == len(todo):
            print(f"    {i}/{len(todo)} fetched", flush=True)

    total = len(already_fetched())
    print(f"\nDone. {total} player bios -> {BIOS_CSV}")


if __name__ == "__main__":
    main()
