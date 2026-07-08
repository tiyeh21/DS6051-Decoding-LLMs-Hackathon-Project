# NBA Front-Office Safety Scorecard

A safety-evaluation scorecard for `gemma-4-E2B` / `gemma-4-E2B-it` deployed as a
**decision-support assistant for an NBA front office** (player valuation,
contract/cap situations, trade-proposal assessment).

The central risk we evaluate: a model that states player facts or stats with
**unearned confidence**, or that **validates a bad roster move** instead of
pushing back — failures that cause real financial/competitive harm exactly
when the output looks most authoritative. We test whether the model knows
what it doesn't know, and stays honest under user pressure.

DS6051 hackathon submission — see `DISCUSSION.md` for full methodology,
results interpretation, and limitations.

## Metrics

1. **Player/career-fact hallucination rate** — does the model fabricate
   biographical or statistical facts, or honestly abstain when it doesn't
   know? Evaluated on 57 facts (base + instruction-tuned), stratified by
   player tier (star / role-player) and fact type (trap / string / numeric).
2. **Sycophancy** — does the model validate a proposed trade regardless of
   merit, or apply genuine critical reasoning? Evaluated on 16 matched trade
   proposals (8 clearly bad, 8 clearly fair), instruction-tuned model only.

Both models run with greedy decoding (`do_sample=False`) for reproducibility.
Sycophancy judged by a second instance of `gemma-4-E2B-it`, prompted
separately as a stance classifier (self-judge — see limitations in
`DISCUSSION.md`).

## Quick start

Everything runs from a single notebook — no separate scripts, no API keys
beyond a HuggingFace token (only required for loading `gemma-4-E2B-it` if
your environment doesn't already have it cached).

```bash
pip install -q transformers accelerate torch scipy pandas
```

Open `ds6051_hackathon.ipynb` in Colab or Jupyter and run top to bottom.
Requires a GPU with at least ~25GB VRAM to hold both models resident
(base + instruction-tuned Gemma 4 E2B, ~10.2GB each in bf16).

Outputs:
- `hallucination_results.csv` — per-fact results, both models
- `sycophancy_results.csv` — per-trade results, instruction-tuned model
- `results_table.md` / `results_table.csv` — aggregated scorecard

## Layout

```
ds6051_hackathon.ipynb   full pipeline: model loading, generation, scoring, export
DISCUSSION.md            methodology, results interpretation, limitations
results_table.md         aggregated results table
hallucination_results.csv   raw per-fact results (n=57, deduplicated)
sycophancy_results.csv      raw per-trade results (n=16)
data/                     evaluation datasets + provenance scripts
  README.md               dataset documentation — verify ground truth before re-running
  fetch_nba_stats.py       pulls per-game stats via nba_api
  fetch_nba_player_bios.py pulls player bio/draft/school data via nba_api
  generate_facts_tiered.py builds the stratified fact set from the above
```

## Important

Ground-truth values were sourced from `stats.nba.com` via `nba_api` and spot-
checked manually; see `data/README.md` for provenance and known verification
caveats. A wrong ground-truth entry would turn a correct model answer into a
false "hallucination" — this is flagged explicitly as a limitation in
`DISCUSSION.md`.
