# Cloned Repositories

No code repositories were specified in the research topic spec, so these were selected to support the
two core layers of the proposed Bayesian–Symbolic diagnostic framework. Both have been **trimmed**
(see notes) to keep the workspace small; data files are excluded from git via `.gitignore`.

---

## 1. ppn-code — Posterior Predictive Null (reference implementation)
- **URL:** https://github.com/gemoran/ppn-code
- **Paper:** *The Posterior Predictive Null* (Moran, Cunningham, Blei, 2022) — `papers/2112.03333_*`
- **Location:** `code/ppn-code/`  (~1.9 MB, language: **R**)
- **Purpose:** Reference code for the PPN check — the central *comparative* Bayesian model-criticism
  tool in our framework (distinguishing whether intervention-model complexity is *necessary* vs only
  *sufficient* → real-but-undetected effect vs genuine robustness).
- **Key files / structure:**
  - `gaussian-mixture/` — PPN for choosing number of mixture components (`analysis.R`, `utils.R`,
    `out/`, `img/`). Cleanest worked example of a PPN study.
  - `factor-analysis/`, `regression/`, `multinomial-mixture/` — PPN across model classes
    (linear vs neural factor models, etc.).
- **How to use:** R scripts; `analysis.R` in each subdir runs the PPN study and writes to `out/`.
  We will most likely **reimplement the PPN logic in Python** (posterior-predictive draws → run
  model B's diagnostic on model A's simulated data → compare distributions) using these scripts as
  the algorithmic reference. No special deps beyond base R + standard Bayesian R packages.
- **Notes:** Small, self-contained, MIT-style academic code. The algorithm (not the R runtime) is
  what matters for our Python pipeline.

## 2. HarmBench — standardized automated red-teaming framework
- **URL:** https://github.com/centerforaisafety/HarmBench
- **Paper:** *HarmBench* (Mazeika, Phan, Yin, Zou, Wang, et al., 2024) — `papers/2402.04249_*`
- **Location:** `code/HarmBench/`  (~19 MB after trimming, language: **Python**)
- **Purpose:** Source of **realistic graded interventions** (18 red-teaming attack methods) and
  **null-ish results** (attack failed ⇒ "model robust") for grounding our semi-synthetic null-result
  generator. Provides the controlled "weak vs strong intervention" axis with a standardized harness.
- **Key files / structure:**
  - `data/behavior_datasets/harmbench_behaviors_text_all.csv` — **400 harmful behaviors**
    (cols: `Behavior, FunctionalCategory, SemanticCategory, Tags, ContextString, BehaviorID`;
    Functional = {standard 200, copyright 100, contextual 100}; Semantic spans
    cybercrime/illegal/misinfo/chem-bio/harassment/harmful). Plus `_val.csv` (40), `_test.csv` (160),
    and `extra_behavior_datasets/` (AdvBench, TDC2023, adv-training behaviors).
  - `baselines/` — implementations of the 18 attack methods (GCG, PAIR, AutoDAN, TAP, GBDA, etc.) =
    interventions of varying strength.
  - `configs/`, `generate_test_cases.py`, `generate_completions.py`, `evaluate_completions.py` —
    the eval pipeline (generate attacks → run on target → classify success).
  - `notebooks/`, `docs/`, `eval_utils.py`.
- **How to use:** See `requirements.txt`. Full pipeline needs GPU + target-model access; for our
  purposes the **behavior CSVs + the attack-method taxonomy + reported ASR structure** are the
  reusable assets (no GPU needed to use the behavior prompts and attack-strength labels).
- **⚠️ Trimming applied (to keep workspace small):** removed `.git` (113 MB),
  `data/multimodal_behavior_images/` (62 MB), and `data/copyright_classifier_hashes/` (287 MB) —
  none are needed for the text-based null-result diagnostics. Re-clone the full repo from the URL if
  the multimodal/copyright assets are ever required.
- **License:** MIT (see `code/HarmBench/LICENSE`). Behavior data is for safety-research use.

---

## Tooling note (no clone needed — pip packages)
The remaining framework components are best obtained as libraries rather than repos and will be added
to the workspace `pyproject.toml` by the experiment runner:
- **Bayesian:** `pymc` / `arviz` / `scipy.stats` (Bayes factors, posterior predictive, calibration).
- **Equivalence testing (TOST):** `pingouin` or `statsmodels` (operationalizes the confirmable-null
  / equivalence-margin logic from `papers/2405.16331_*`).
- **Symbolic / logic:** `sympy`, a SAT/SMT layer (`pysat` / `z3-solver`), or a small custom
  weighted-constraint reasoner inspired by the Logical Boltzmann Machine (`papers/2505.20313_*`).
