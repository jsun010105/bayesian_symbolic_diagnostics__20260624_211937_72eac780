# Resources Catalog

## Summary
Resources gathered for **Bayesian Symbolic Diagnostics for Interpreting Null Results in AI Alignment
Experiments**. The framework must fuse (Bayesian evidence quantification) × (symbolic intervention/
assumption logic) to classify the cause of a null result as one of {genuine robustness, weak
intervention, design flaw} — and beat Bayesian-only and symbolic-only baselines.

- **Papers downloaded:** 18 (in `papers/`)
- **Datasets:** 1 primary synthetic (generated) + 1 real anchor (HarmBench, in `code/`)
- **Code repositories:** 2 cloned (`code/`)

---

## Papers (18)
Organized by the four framework pillars. Full details in `papers/README.md`; synthesis in
`literature_review.md`. `★` = deep-read (full methodology).

| # | Title | Year | arXiv | Pillar | File |
|---|-------|------|-------|--------|------|
| 1 ★ | The Posterior Predictive Null | 2022 | 2112.03333 | A: Bayesian criticism | `papers/2112.03333_*.pdf` |
| 2 | Calibrated Model Criticism Using Split Predictive Checks | 2022 | 2203.15897 | A | `papers/2203.15897_*.pdf` |
| 3 | Recommendations for Visual Predictive Checks in Bayesian Workflow | 2025 | 2503.01509 | A | `papers/2503.01509_*.pdf` |
| 4 | Bayes Factors or Relative Belief Ratios? | 2023 | 2301.08994 | A | `papers/2301.08994_*.pdf` |
| 5 | The Expected Demise of the Bayes Factor | 2015 | 1506.08292 | A | `papers/1506.08292_*.pdf` |
| 6 | Bayes Factor Hypothesis Testing in Meta-Analyses | 2025 | 2511.22535 | A | `papers/2511.22535_*.pdf` |
| 7 | Two-Sample Bayesian Nonparametric Hypothesis Testing | 2009 | 0910.5060 | A | `papers/0910.5060_*.pdf` |
| 8 ★ | Confirming the Null: Equivalence Testing & Topology of Confirmation | 2024 | 2405.16331 | B: Null logic | `papers/2405.16331_*.pdf` |
| 9 ★ | Reasoning in Neurosymbolic AI (Logical Boltzmann Machines) | 2025 | 2505.20313 | C: Neurosymbolic | `papers/2505.20313_*.pdf` |
| 10 | Sound & Complete Neurosymbolic Reasoning w/ LLM-Grounded Interpretations | 2025 | 2507.09751 | C | `papers/2507.09751_*.pdf` |
| 11 | Priors for Symbolic Regression | 2023 | 2304.06333 | C | `papers/2304.06333_*.pdf` |
| 12 ★ | On the Limits of Behavioral Alignment / Alignment Verifiability | 2026 | 2602.05656 | D: Alignment eval | `papers/2602.05656_*.pdf` |
| 13 | HarmBench: Standardized Automated Red-Teaming | 2024 | 2402.04249 | D | `papers/2402.04249_*.pdf` |
| 14 | Learning-Based Automated Adversarial Red-Teaming | 2025 | 2512.20677 | D | `papers/2512.20677_*.pdf` |
| 15 | Gradient-Based Language Model Red Teaming (GBRT) | 2024 | 2401.16656 | D | `papers/2401.16656_*.pdf` |
| 16 | Towards Trustworthy Agentic AI (survey) | 2026 | 2605.23989 | D | `papers/2605.23989_*.pdf` |
| 17 | Revisiting Sanity Checks for Saliency Maps | 2021 | 2110.14297 | E: Diagnostics | `papers/2110.14297_*.pdf` |
| 18 | Resolving Spurious Correlations via Interventions | 2020 | 2002.05217 | E | `papers/2002.05217_*.pdf` |

## Datasets
| Name | Source | Size | Task | Location | Notes |
|------|--------|------|------|----------|-------|
| Synthetic Labeled Null-Results | generated (this repo) | 3k rows (~0.4 MB), scalable | 3-class cause classification | `datasets/synthetic_null_results/` | PRIMARY. Ground-truth labels; emits raw obs (Bayesian) + symbolic features. Regenerable via `generate.py`. |
| HarmBench behaviors | github.com/centerforaisafety/HarmBench | 400 behaviors + 18 attacks | red-teaming / robustness | `code/HarmBench/data/` | Real ANCHOR for intervention-strength realism; ASR structure for semi-synthetic grounding. |

See `datasets/README.md` for download/loading/regeneration instructions.

## Code Repositories
| Name | URL | Purpose | Location | Notes |
|------|-----|---------|----------|-------|
| ppn-code | github.com/gemoran/ppn-code | Posterior Predictive Null reference (R) | `code/ppn-code/` | Algorithmic reference for the core comparative Bayesian criticism; reimplement in Python. |
| HarmBench | github.com/centerforaisafety/HarmBench | Automated red-teaming framework (Python) | `code/HarmBench/` | Trimmed to 19 MB (removed .git, multimodal images, copyright hashes). |

See `code/README.md` for structure, key files, and the pip-package tooling note (pymc/arviz,
pingouin/statsmodels for TOST, sympy/pysat/z3 for the symbolic layer).

---

## Resource Gathering Notes

### Search strategy
The `paper-finder` service was unavailable (not running on localhost:8000), so I fell back to the
arXiv API (`arxiv` Python client). I ran 14 queries across the four pillars (Bayesian model
selection/evidence, null-result interpretation/equivalence testing, neurosymbolic reasoning, alignment
eval/red-teaming, plus statistical power, sanity checks, symbolic regression), collected 114 unique
candidates, scored them by a keyword-relevance heuristic + multi-query co-occurrence, and downloaded
the top curated set spanning all pillars. The 4 most central papers were deep-read via the PDF chunker.

### Selection criteria
Coverage of every pillar the hypothesis requires; preference for recent (2023–2026) state-of-the-art
plus a few foundational/cautionary references (Bayes-factor critiques, 2009 nonparametric two-sample
test). Priority on papers that operationalize the *exact* distinctions in the hypothesis
(identifiability/indistinguishability = robustness vs weak intervention; confirmability topology =
which nulls are interpretable).

### Challenges encountered
- paper-finder service down → manual arXiv pipeline (required installing `httpx`, `arxiv`).
- No dataset labels null-result *causes* (the core literature gap) → built a grounded synthetic
  generator with ground-truth labels.
- HarmBench clone was 480 MB (model/copyright assets) → trimmed to 19 MB keeping only the text
  behaviors, attack code, and configs.

### Gaps and workarounds
- **No cause-labeled benchmark** → `datasets/synthetic_null_results/` (regenerable, ablation-ready).
- **Symbolic/Bayesian fusion not pre-implemented** → documented the pip-package toolchain
  (pymc/arviz, pingouin TOST, sympy/pysat) and the PPN reference code for the experiment runner.

---

## Recommendations for Experiment Design
1. **Primary dataset:** `datasets/synthetic_null_results/` (3-way labeled). Anchor realism on
   HarmBench intervention strengths; add positive/negative controls (sanity-check style, E1).
2. **Baselines (the required ablation):** NHST-naive ("fail to reject ⇒ robust"); TOST/equivalence-only;
   Bayesian-only (Bayes factor + relative belief ratio + PPN); symbolic-only (topology/identifiability
   rules). The **hybrid** must beat all four on 3-way macro-F1 — the hypothesis's core claim.
3. **Bayesian layer:** Bayes factor + relative belief ratio (A4) with prior-sensitivity (A5); split
   predictive checks for calibration (A2); Pólya-tree two-sample evidence (A7); sequential aggregation
   (A6). Reuse PPN logic (A1, `code/ppn-code/`).
4. **Symbolic layer:** encode hypothesis topology + equivalence margin (B1) and assumptions/intervention
   logic as weighted constraints (C1), with bilateral/paraconsistent truth for evidence-for vs against
   (C2); identifiability check per D1; optional MDL-scored prior over symbolic cause-explanations (C3).
5. **Fusion:** symbolic layer gates *confirmability/identifiability* first; Bayesian layer quantifies
   evidence within the admissible structure; combine → 3-way cause label.
6. **Metrics:** 3-way cause macro-F1 (headline), calibration/ECE (A2), robustness↔weak-intervention
   confusion rate, detection-vs-effect-size curves. Always report Bayesian-only/symbolic-only ablations.
