#!/usr/bin/env python3
"""Fetch multi-season historical NBA player stats via nba_api and save to CSV.

Pulls league-wide per-game player stats for a range of seasons from
stats.nba.com (LeagueDashPlayerStats endpoint) and writes:

  data/nba_player_stats.csv            all seasons stacked (one row per player-season)
  data/nba_player_stats_<SEASON>.csv   one file per season

Usage:
    python data/fetch_nba_stats.py                      # last 5 seasons, per-game
    python data/fetch_nba_stats.py --start 2015 --end 2024
    python data/fetch_nba_stats.py --per-mode Totals    # season totals instead

Notes:
    - Seasons are identified by their starting year; e.g. 2023 -> "2023-24".
    - stats.nba.com is unofficial and rate-limits; we sleep between calls.
    - Requires: nba_api, pandas.  (pip install nba_api pandas)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

try:
    from nba_api.stats.endpoints import leaguedashplayerstats
except ImportError:
    sys.exit("nba_api is not installed. Run: pip install nba_api")

DATA_DIR = Path(__file__).resolve().parent


def season_str(start_year: int) -> str:
    """2023 -> '2023-24'."""
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def fetch_season(start_year: int, per_mode: str, sleep: float) -> pd.DataFrame:
    season = season_str(start_year)
    print(f"  fetching {season} ({per_mode}) ...", flush=True)
    resp = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed=per_mode,
        season_type_all_star="Regular Season",
        timeout=60,
    )
    df = resp.get_data_frames()[0]
    df.insert(0, "SEASON", season)
    time.sleep(sleep)  # be polite to the unofficial endpoint
    return df


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--start", type=int, default=2019,
                   help="first season start year (default: 2019)")
    p.add_argument("--end", type=int, default=2023,
                   help="last season start year, inclusive (default: 2023)")
    p.add_argument("--per-mode", default="PerGame",
                   choices=["PerGame", "Totals", "Per36"],
                   help="stat aggregation mode (default: PerGame)")
    p.add_argument("--sleep", type=float, default=1.0,
                   help="seconds to sleep between season requests")
    args = p.parse_args()

    if args.end < args.start:
        sys.exit("--end must be >= --start")

    print(f"Fetching NBA player stats {season_str(args.start)}..{season_str(args.end)} "
          f"[{args.per_mode}]")

    frames = []
    for year in range(args.start, args.end + 1):
        df = fetch_season(year, args.per_mode, args.sleep)
        per_season_path = DATA_DIR / f"nba_player_stats_{season_str(year)}.csv"
        df.to_csv(per_season_path, index=False)
        print(f"    wrote {per_season_path.name}  ({len(df)} players)")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    combined_path = DATA_DIR / "nba_player_stats.csv"
    combined.to_csv(combined_path, index=False)
    print(f"\nDone. {len(combined)} player-season rows across "
          f"{combined['SEASON'].nunique()} seasons -> {combined_path}")


if __name__ == "__main__":
    main()
