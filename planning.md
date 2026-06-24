# Planning: Bayesian Symbolic Diagnostics for Interpreting Null Results in AI Alignment

## Motivation & Novelty Assessment

### Why This Research Matters
Alignment experiments increasingly report null/ambiguous results ("the attack failed", "the
safety property held", "the training change had no measurable effect"). A null is epistemically
ambiguous: it can mean **genuine robustness**, a **weak/underpowered intervention**, or a
**design flaw** (confound, broken metric, evaluation-awareness, unconfirmable hypothesis). NHST
("fail to reject H₀") is structurally unable to separate these. Mis-reading a null wastes research
effort and, worse, can ship false confidence in a model's safety. A diagnostic that tells a
researcher *which* of the three a null is — with an interpretable reason — directly improves the
reliability of alignment science.

### Gap in Existing Work (from literature_review.md)
- **Bayesian model criticism** (Posterior Predictive Null A1; Bayes factors / relative belief A4,A5;
  split predictive checks A2) can *quantify* evidence **for** a null and gauge power — but is blind
  to the experiment's logical structure (a confound that cancels a real effect looks like a clean
  null; a point-null hypothesis is statistically testable but logically unconfirmable, B1).
- **Symbolic / neurosymbolic reasoning** (B1 confirmability topology, D1 identifiability/equivalence
  classes) can encode *why* a null is or isn't interpretable — but cannot, on its own, tell a
  genuinely-null effect from a real-but-underpowered one (that needs the quantitative evidence/power).
- **No public dataset labels the *cause* of a null** (confirmed by the resource finder's search):
  every alignment-eval set diagnoses models, not the epistemic status of a "no-effect" finding.

### Our Novel Contribution
A **hybrid Bayesian–symbolic diagnostic** that (i) uses a symbolic layer to *gate*
confirmability/identifiability (catches design flaws Bayesian evidence cannot), then (ii) uses a
Bayesian evidence+power layer to separate genuine robustness from weak intervention *within the
admissible structure*, producing an interpretable reasoning chain and a calibrated confidence. We
test whether this hybrid beats Bayesian-only, symbolic-only, and naive-NHST/TOST baselines on
3-way cause classification — the literature's open question, made measurable via a ground-truth
generator.

### Experiment Justification
- **E1 — Main ablation (headline):** Bayesian-only vs Symbolic-only vs Hybrid (+ NHST-naive, TOST-only
  baselines) on 3-way macro-F1. Directly tests the hypothesis's core claim. *Needed* because the
  whole contribution is "fusion beats either modality alone."
- **E2 — Real-LLM expert-judge baseline:** a state-of-the-art LLM (via OpenRouter) is shown the same
  scenarios in natural language and asked to diagnose the cause. Maps methodology step 7 ("compare
  against expert assessments"); tests whether a strong general reasoner already solves the task or
  whether the structured framework adds value. *Needed* to ground the claim against a real model and
  to compute framework↔expert Cohen's κ.
- **E3 — Mechanism / error analysis:** confusion matrices, detection-vs-effect-size curves,
  calibration (ECE). *Needed* to show the *why*: where each modality is blind and how fusion fixes it.
- **E4 — Sensitivity analysis:** vary the Bayes-factor prior scale and equivalence margin; measure
  hybrid robustness. *Needed* for the methodology's required prior-sensitivity check.

## Research Question
Can a hybrid Bayesian–symbolic framework distinguish genuine robustness vs weak intervention vs
design flaw as the cause of a null result, more accurately than either modality alone?

## Hypothesis Decomposition
- H1: Hybrid 3-way macro-F1 > each of {Bayesian-only, Symbolic-only, NHST-naive, TOST-only}.
- H2: Bayesian-only confuses DESIGN_FLAW with the others (blind to confound/confirmability).
- H3: Symbolic-only confuses GENUINE_ROBUSTNESS with WEAK_INTERVENTION (blind to N/noise power).
- H4: Hybrid produces calibrated confidences and interpretable reasoning chains.

## Methodology

### Data
Primary: `datasets/synthetic_null_results/` (3,000 ground-truth-labeled scenarios, ~balanced).
Each row emits raw observations (→ Bayesian layer) and symbolic/structural flags (→ symbolic layer).
By construction `observed_diff` separates robustness from the rest but **cannot** separate
weak-intervention from design-flaw — the intended pressure that makes fusion necessary. We
regenerate a larger held-out test set with a different seed to avoid any tuning leakage.

### Methods
- **Bayesian layer:** from summary stats compute SE of the mean difference, a JZS-style Bayes factor
  BF10 (Cauchy prior on effect size, Savage–Dickey/numerical), and a TOST equivalence test against
  the scenario's margin; derive a *power/confirmability* signal (is the CI tight enough to confirm
  equivalence?). Decision: strong null evidence + confirmed equivalence → robustness; inconclusive /
  underpowered → weak intervention; clear effect → (cannot itself attribute → defaults).
- **Symbolic layer:** weighted logical rules over {confound, evaluation_awareness, measurement_valid,
  identifiable, hypothesis_topology, equivalence_margin_set, intervention_strength}. Design-flaw gate
  (B1 confirmability + D1 identifiability) fires DESIGN_FLAW; otherwise intervention_strength
  separates robustness (strong) vs weak intervention (weak) — but is blind to N/noise.
- **Hybrid fusion:** symbolic gates confirmability/identifiability first (DESIGN_FLAW); within the
  admissible structure the Bayesian evidence+power layer separates robustness vs weak intervention;
  composite confidence combines symbolic rule certainty and Bayesian evidence magnitude. Emits a
  human-readable reasoning chain.

### Baselines
NHST-naive ("fail to reject ⇒ robust"); TOST-only (equivalence ⇒ robust else weak); Bayesian-only;
Symbolic-only; plus the real-LLM expert judge (E2).

### Evaluation Metrics
3-way macro-F1 (headline) + per-class F1; accuracy; confusion matrices; Cohen's κ (framework↔ground
truth, framework↔LLM); bootstrap 95% CIs on macro-F1; McNemar test hybrid-vs-baseline; ECE
(calibration); detection-vs-effect-size curve.

### Statistical Analysis Plan
- 1,000-resample bootstrap CIs on macro-F1 for every method.
- McNemar's exact test for paired correctness, hybrid vs each baseline (α=0.05).
- Cohen's κ for agreement. Multiple-comparison note (5 baselines) — report raw + Holm.

## Expected Outcomes
Hybrid macro-F1 materially > all single-modality baselines; Bayesian-only fails on DESIGN_FLAW;
symbolic-only fails on robustness↔weak; LLM judge competitive but not dominant. Supports H1–H4.

## Timeline (≤60 min total)
Plan ✓ → env ✓ (10) → framework+E1 (15) → LLM judge E2 (10) → analysis/figures E3–E4 (12) → report (10).

## Potential Challenges & Mitigations
- *Dataset is built so fusion wins* → honest framing as a controlled demonstration + sensitivity
  analysis (E4) + real-LLM external check (E2); separate test seed; report this as a limitation.
- *OpenRouter latency/limits* → judge on a 150-scenario stratified subset, parallel calls, cache, retries.
- *Bayes-factor prior sensitivity* → E4 sweeps the prior scale.

## Success Criteria
H1 holds with non-overlapping bootstrap CIs and significant McNemar tests; mechanism story (H2,H3)
visible in confusion matrices; framework produces interpretable, calibrated outputs.
