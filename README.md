# NBA Front-Office Safety Scorecard

A safety-evaluation scorecard for `gemma-4-E2B` / `gemma-4-E2B-it` deployed as a
**decision-support assistant for an NBA front office** (player valuation,
contract/cap situations, trade-proposal assessment).

The central risk we evaluate: a model that states stats, contract terms, or CBA
mechanics with **unearned confidence**, or that **validates a bad roster move**
instead of pushing back — failures that cause real financial/competitive harm
exactly when the output looks most authoritative. We test whether the model knows
what it doesn't know, and stays honest under user pressure.

## Metrics
1. CBA / contract factual accuracy (automated)
2. Player-stat hallucination rate (automated + 3-judge panel)
3. Calibration — ECE / Brier / overconfidence gap
4. Sycophancy — 2-turn pressure test, 3-judge panel
5. Steerability — constraint-prompt re-run, deltas vs baseline
6. **Cross-lingual safety shift** — en + es + **sw** (low-resource) *(required)*
7. **Sandbagging / evaluation-awareness** *(bonus)*
- Run on **both** base and instruction-tuned models and compared.

## Quick start
```bash
pip install -r requirements.txt

# 1) Dry-run the entire harness with NO GPU / NO API keys (get plumbing green):
MOCK_MODE=1 python run_scorecard.py && python aggregate_results.py

# 2) Real run: set model IDs + judge keys, then:
export GEMMA_BASE_ID=...            # confirm exact Hub IDs from organizers
export GEMMA_IT_ID=...
export OPENAI_API_KEY=...  TOGETHER_API_KEY=...  GROQ_API_KEY=...   # 3 judges
python run_scorecard.py            # writes results/results_{base,it}.json
python aggregate_results.py        # writes results/scorecard_results.{md,csv}
```
`MOCK_MODE=1` returns deterministic fake answers (a realistic mix of correct /
hallucinated / sycophantic) so you can validate the pipeline in minutes, then
swap in real models. Judges are OpenAI-compatible — point `base_url` at OpenAI,
Together, Groq, or a local vLLM server in `config.py`.

## Layout
```
config.py              models, judges, languages, run control
src/inference.py       target-model loading + generation (+ mock)
src/judges.py          3-judge panel, JSON parsing, agreement, Krippendorff α
src/prompts.py         personas, constraint prompt, judge rubrics
src/utils.py           fuzzy grading, ECE/Brier, bootstrap CIs, IO
src/metrics/*.py       one module per metric
run_scorecard.py       runs all metrics on both models
aggregate_results.py   builds the results table (md + csv)
data/                  eval datasets + provenance (VERIFY before graded run)
docs/                  scorecard pitch, methodology, results template, rubric map
```

## Read these
- `docs/scorecard.md` — the metric pitch (what/why/how/limits)
- `docs/methodology.md` — datasets + judge pipeline + limitations
- `docs/rubric_map.md` — every graded item ↔ where it's delivered (start here)
- `docs/results_discussion.md` — fill after your run
- `data/README.md` — **verify ground truth before running**

## Important
Confirm the exact model Hub IDs and **verify every `truth` value** against its
source before your graded run — a wrong ground-truth entry turns a correct model
answer into a false "hallucination" and undermines the whole scorecard.
