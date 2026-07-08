# Data — NBA Player Stats

Multi-season historical NBA player statistics used by the scorecard's
player-stat metrics (hallucination rate, calibration ground truth, etc.).

## Files
| File | Contents |
|------|----------|
| `nba_player_stats.csv` | All seasons stacked; one row per player-season |
| `nba_player_stats_<SEASON>.csv` | Per-season split (e.g. `nba_player_stats_2023-24.csv`) |
| `fetch_nba_stats.py` | Script that regenerates the CSVs |

## Provenance
- **Source:** `stats.nba.com` via the [`nba_api`](https://github.com/swar/nba_api)
  package — endpoint `LeagueDashPlayerStats`, `Regular Season`, `PerGame`.
- **Seasons:** 2019-20 through 2023-24 (5 seasons, 2,785 player-season rows).
- **Fetched:** 2026-07-08.
- **Key columns:** `SEASON, PLAYER_ID, PLAYER_NAME, TEAM_ABBREVIATION, AGE, GP,
  MIN, PTS, REB, AST, STL, BLK, TOV, FG_PCT, FG3_PCT, FT_PCT, PLUS_MINUS` (plus
  rank columns). Full schema is the CSV header.

## Regenerate / extend
```bash
pip install nba_api pandas
python data/fetch_nba_stats.py                    # default: 2019-20..2023-24, PerGame
python data/fetch_nba_stats.py --start 2015 --end 2024
python data/fetch_nba_stats.py --per-mode Totals  # season totals instead of per-game
```
`stats.nba.com` is unofficial and rate-limited; the script sleeps between
requests. If it hangs, re-run — partial per-season CSVs are written as it goes.

## ⚠️ Verify before a graded run
Per the top-level README: **verify every ground-truth `truth` value** derived
from this data against its source before scoring. stats.nba.com occasionally
revises historical numbers; a wrong ground-truth entry turns a correct model
answer into a false "hallucination."
