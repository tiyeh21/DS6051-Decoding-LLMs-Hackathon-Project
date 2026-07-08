# Data — NBA Player Stats

Multi-season historical NBA player statistics used by the scorecard's
player-stat metrics (hallucination rate, calibration ground truth, etc.).

## Files
| File | Contents |
|------|----------|
| `nba_player_stats.csv` | All seasons stacked; one row per player-season |
| `nba_player_stats_<SEASON>.csv` | Per-season split (e.g. `nba_player_stats_2023-24.csv`) |
| `nba_player_bios.csv` | One row per player: college, country, birthdate, draft, etc. |
| `fetch_nba_stats.py` | Script that regenerates the box-score CSVs |
| `fetch_nba_player_bios.py` | Script that regenerates `nba_player_bios.csv` |

## Provenance
- **Source:** `stats.nba.com` via the [`nba_api`](https://github.com/swar/nba_api)
  package.
- **Fetched:** 2026-07-08.

### Box scores — `nba_player_stats.csv`
- **Endpoint:** `LeagueDashPlayerStats`, `Regular Season`, `PerGame`.
- **Seasons:** 2014-15 through 2023-24 (10 seasons, 5,309 player-season rows).
- **Key columns:** `SEASON, PLAYER_ID, PLAYER_NAME, TEAM_ABBREVIATION, AGE, GP,
  MIN, PTS, REB, AST, STL, BLK, TOV, FG_PCT, FG3_PCT, FT_PCT, PLUS_MINUS` (plus
  rank columns). Full schema is the CSV header.

### Player bios — `nba_player_bios.csv`
- **Endpoint:** `CommonPlayerInfo`, one call per unique `PLAYER_ID` (1,425 players).
- **Columns:** `PERSON_ID, DISPLAY_FIRST_LAST, BIRTHDATE, COUNTRY, SCHOOL
  (college), LAST_AFFILIATION, HEIGHT, WEIGHT, POSITION, SEASON_EXP,
  DRAFT_YEAR, DRAFT_ROUND, DRAFT_NUMBER, FROM_YEAR, TO_YEAR, GREATEST_75_FLAG`.
- Join to the box-score data on `PERSON_ID` = `PLAYER_ID`.
- **⚠️ Hometown / birth city is NOT available in nba_api.** The closest bio
  fields are `BIRTHDATE` + `COUNTRY` + `SCHOOL`. A true hometown would require a
  separate source (Basketball-Reference, Wikipedia).

## Regenerate / extend
```bash
pip install nba_api pandas
python data/fetch_nba_stats.py                    # default: 2014-15..2023-24, PerGame
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
