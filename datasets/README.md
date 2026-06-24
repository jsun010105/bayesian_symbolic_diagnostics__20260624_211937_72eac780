# Datasets

Data files are **not committed to git** (see `.gitignore`); the synthetic data is deterministically
regenerable and the HarmBench anchor lives under `code/`. Below are the datasets gathered/created and
how to (re)produce them.

---

## Dataset 1 (PRIMARY): Synthetic Labeled Null-Result Scenarios

### Overview
- **Source:** generated locally by `datasets/synthetic_null_results/generate.py` (this repo).
- **Why synthetic:** A systematic literature search (see `../literature_review.md`) found **no public
  dataset that labels the *cause* of a null result**. All alignment-eval datasets diagnose
  models/methods, not the epistemic status of a "no-effect" finding. A ground-truth-labeled generator
  is therefore the only way to directly measure the hypothesis's headline claim (3-way cause accuracy)
  and to run the Bayesian-only vs symbolic-only vs hybrid ablation.
- **Size:** configurable; default 3,000 scenarios (~0.37 MB CSV, ~1.4 MB JSONL). Roughly balanced
  across the 3 classes (~33% each).
- **Format:** CSV and JSONL, one row per experiment.
- **Task:** 3-class classification of the cause of a null result.
- **Splits:** none predefined — split by seed in the experiment runner (e.g. 70/15/15).

### Labels (ground truth)
| label | name | meaning |
|---|---|---|
| 0 | `GENUINE_ROBUSTNESS` | true effect ≈ 0; model genuinely invariant (adequately powered, strong intervention still found nothing) |
| 1 | `WEAK_INTERVENTION` | a real effect exists but underpowered (small N, weak attack/search budget, or coarse metric) |
| 2 | `DESIGN_FLAW` | uninterpretable null: confound, broken/leaky measurement, evaluation-awareness, or unconfirmable hypothesis topology (point null, no equivalence margin) |

### Columns
**Raw observations (feed the Bayesian layer):** `n_per_arm`, `noise_sd`, `control_mean`,
`treated_mean`, `observed_diff`, `control_var`, `treated_var`, `true_effect` *(latent; analysis-only,
do not use as a feature)*.

**Symbolic / structural features (feed the symbolic layer):** `hypothesis_topology`
(`equivalence`|`point`), `equivalence_margin_set`, `equivalence_margin`, `intervention_strength`,
`confound_present`, `evaluation_awareness`, `measurement_valid`, `identifiable`.

**Targets:** `label`, `label_name`.

> Design note: by construction, raw `observed_diff` alone separates `GENUINE_ROBUSTNESS`
> (small) from the other two (larger), but **cannot** separate `WEAK_INTERVENTION` from
> `DESIGN_FLAW` — that requires the symbolic/structural features. This is the intended pressure that
> makes the *hybrid* framework beat either single-modality baseline.

### Generation / regeneration
```bash
cd datasets/synthetic_null_results
python generate.py --n 3000 --seed 0 --out null_results.csv --jsonl null_results.jsonl
```
Options: `--n` (count), `--seed` (reproducibility), `--out`, `--jsonl`.

### Loading
```python
import pandas as pd
df = pd.read_csv("datasets/synthetic_null_results/null_results.csv")
X_raw = df[["n_per_arm","noise_sd","observed_diff","control_var","treated_var"]]
X_sym = df[["hypothesis_topology","equivalence_margin_set","equivalence_margin",
            "intervention_strength","confound_present","evaluation_awareness",
            "measurement_valid","identifiable"]]
y = df["label"]
```

### Sample data
See `synthetic_null_results/samples.jsonl` (first 10 rows, committed for reference).

### Grounding in the literature
Parameters map to reviewed work: effect-size/N/power → A2,A6; equivalence margin & topology → B1
(`2405.16331`, confirmable iff nonempty interior); intervention strength/search budget → D2,D3,D4
(red-teaming as graded search); confound/eval-awareness → D1 (`2602.05656`, identifiability), E2
(`2002.05217`, spurious correlations).

---

## Dataset 2 (ANCHOR, real): HarmBench behaviors & red-teaming results

### Overview
- **Source:** https://github.com/centerforaisafety/HarmBench (cloned to `code/HarmBench/`).
- **What:** 400 harmful "behaviors" (prompts) across functional categories {standard, copyright,
  contextual} and 7 semantic categories, plus 18 attack-method implementations and the eval harness.
- **Role here:** real, graded **interventions** (attacks of varying strength) producing real
  **null-ish results** (attack fails ⇒ "model robust"). Used to (a) sanity-check that the synthetic
  generator's intervention-strength axis is realistic, and (b) optionally produce *semi-synthetic*
  scenarios anchored on real attack-success-rate (ASR) structure.
- **Format:** CSV. Key file:
  `code/HarmBench/data/behavior_datasets/harmbench_behaviors_text_all.csv`
  (cols: `Behavior, FunctionalCategory, SemanticCategory, Tags, ContextString, BehaviorID`).
- **License:** MIT (safety-research use).

### Download / loading
Already present under `code/HarmBench/` (large `.git`, multimodal images, and copyright hashes were
removed — see `code/README.md`). To get the full original assets:
```bash
git clone https://github.com/centerforaisafety/HarmBench.git
```
```python
import pandas as pd
beh = pd.read_csv("code/HarmBench/data/behavior_datasets/harmbench_behaviors_text_all.csv")
```

### Notes
- Running attacks end-to-end requires GPU + target-model access; the **behavior prompts + attack
  taxonomy + ASR structure** are usable with no GPU.
- AdvBench / TDC2023 / adv-training behavior sets are under
  `code/HarmBench/data/behavior_datasets/extra_behavior_datasets/`.
