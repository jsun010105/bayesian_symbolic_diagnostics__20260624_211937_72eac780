# Literature Review: Bayesian Symbolic Diagnostics for Interpreting Null Results in AI Alignment Experiments

**Research hypothesis.** A hybrid Bayesian–symbolic diagnostic framework can systematically
distinguish between *true model robustness*, *insufficient/weak experimental interventions*, and
*design flaws* as causes of null results in AI alignment experiments, with higher accuracy than
Bayesian-only or symbolic-only methods.

This review synthesizes 18 downloaded papers across four pillars that the framework must combine:
(1) **Bayesian evidence quantification & model criticism** (how to quantify evidence *for* a null),
(2) **the logic of confirming nulls** (when is "no effect" actually confirmable),
(3) **neurosymbolic representation & reasoning** (how to encode intervention logic / assumptions
symbolically), and (4) **AI alignment evaluation, robustness & red-teaming** (the application
domain and where null results actually arise).

---

## 1. Research Area Overview

A *null result* in an alignment experiment ("the intervention did not change the model's behavior",
"the safety property held under our attack", "no measurable effect of the training change") is
deeply ambiguous. It can mean three very different things:

- **Genuine robustness (true null):** the model really is invariant to the manipulation.
- **Weak/insufficient intervention (false null from low power):** the intervention was too small,
  the attack too weak, the sample too small, or the metric too coarse to detect a real effect.
- **Design flaw (invalid null):** a confound, a broken measurement, evaluation awareness/leakage,
  or a logically unconfirmable hypothesis structure makes the result uninterpretable.

The classical statistical apparatus (NHST p-values) is structurally unable to separate these:
"failure to reject H₀" is *not* evidence for H₀. The literature converges on two complementary
remedies that this project fuses:

1. **Bayesian evidence & model criticism** can *quantify* support for a null and compare competing
   model/intervention hypotheses (Bayes factors, relative belief ratios, posterior predictive
   checks, the posterior predictive null, split predictive checks).
2. **Symbolic / neurosymbolic representations** can encode the *logical structure* of the
   experiment — the intervention logic, the assumptions, the hypothesis topology — so that the
   diagnostic can reason about *why* a null is or is not interpretable (confirmable hypothesis
   topology, identifiability, severe-testing semantics, logical constraints).

The alignment-evaluation literature supplies both the motivating problem and a sharp formal
articulation of it: behavioral evaluation provides *necessary but insufficient* evidence for latent
alignment, and observed compliance only identifies an **equivalence class** of policies, not a
unique latent property.

---

## 2. Key Papers

### Pillar A — Bayesian evidence quantification & model criticism

#### A1. The Posterior Predictive Null (Moran, Cunningham, Blei, 2021/2022) — `papers/2112.03333_*`
- **Source:** Bayesian Analysis (2022). Code: https://github.com/gemoran/ppn-code
- **Key contribution:** The **posterior predictive null check (PPN)** — a *comparative* Bayesian
  model-criticism tool. A classical posterior predictive check (PPC) asks whether observed data is
  consistent with a model; the PPN asks whether **data simulated from model A can pass the
  predictive check of model B**. If yes, A "fools" B → the two models are predictively equivalent
  under that diagnostic.
- **Why this is central to our framework:** This is *exactly* the machinery for distinguishing
  "genuine robustness" from "weak intervention." Reframe: model A = the null/no-effect model,
  model B = the intervention-has-effect model. A classical PPC may show *both* fit the data (both
  pass), which is the standard null-result ambiguity. The PPN disambiguates: it separates whether a
  more complex (intervention) model is *necessary* vs merely *sufficient*. Quote: "the classical PPC
  helps indicate if a model's complexity is *sufficient*... while the PPN helps to determine whether
  that complexity is *necessary*." Necessary-but-not-present complexity ↔ a real-but-undetected
  effect; unnecessary complexity ↔ genuine robustness/parsimony.
- **Method:** Reference distribution = posterior predictive; diagnostic functions (e.g.
  log-likelihood); a *PPN study* = full matrix of cross-checks between a collection of models;
  selection by parsimony.
- **Datasets in paper:** synthetic Gaussian mixtures (choosing K), probabilistic factor models
  (linear vs neural), and re-analysis of predictive-check literature data.

#### A2. Calibrated Model Criticism Using Split Predictive Checks (Li & Huggins, 2022) — `papers/2203.15897_*`
- **Key contribution:** **Split predictive checks (SPCs)** — combine the ease/speed of PPCs with
  good *calibration* (uniform PPC p-values under the true model). Single vs divided SPCs with
  asymptotic theory.
- **Relevance:** PPCs are notoriously *miscalibrated* (conservative), which directly biases
  null-result interpretation toward "fits fine / no problem." A diagnostic framework that reports
  calibrated evidence is essential to avoid declaring false robustness. SPCs are a practical,
  automated criticism primitive to plug into the Bayesian layer.

#### A3. Recommendations for Visual Predictive Checks in Bayesian Workflow (Säilynoja, Johnson, Martin, Vehtari, 2025) — `papers/2503.01509_*`
- **Key contribution:** Practical guidance for selecting/interpreting prior & posterior predictive
  visualizations; treats the visual check itself as a model that can fail. Part of the broader
  **Bayesian workflow** program (Gelman et al.).
- **Relevance:** Defines the workflow context in which our diagnostics live; warns that checks have
  implicit assumptions that, if violated, mislead — i.e., a source of *design-flaw* diagnoses.

#### A4. How to Measure Evidence and Its Strength: Bayes Factors or Relative Belief Ratios? (2023) — `papers/2301.08994_*`
- **Key contribution:** Compares two measures that both satisfy the *principle of evidence*: the
  **Bayes factor** and the **relative belief ratio** (RB = posterior/prior density ratio at a value).
  Argues RB has advantages (less prior-sensitivity for measuring evidence strength, natural handling
  of evidence *for* H).
- **Relevance:** The "Bayesian evidence quantification" component needs a principled scalar of
  evidence *for the null*. This paper is the menu of options + their pitfalls (esp. prior
  sensitivity, the Jeffreys–Lindley issue).

#### A5. The Expected Demise of the Bayes Factor (Robert, 2015/2017) — `papers/1506.08292_*`
- **Key contribution:** A pointed critique of default Bayes factors — sensitivity to (improper)
  priors, the Jeffreys–Lindley paradox, instability of marginal-likelihood computation.
- **Relevance:** A *cautionary* reference. Tells us the Bayesian-only approach is fragile precisely
  where it matters (priors on the intervention-effect magnitude), motivating the symbolic scaffolding
  and sensitivity analysis. Important for the "Bayesian alone < hybrid" comparison.

#### A6. Bayes Factor Hypothesis Testing in Meta-Analyses (2025) — `papers/2511.22535_*`
- **Key contribution:** Practical advantages of Bayes factors for *cumulative/sequential* evidence
  (meta-analysis): can accumulate evidence for the null, supports optional stopping.
- **Relevance:** Alignment null results often come from *many* small experiments/seeds; aggregating
  evidence for "no effect" across them is a meta-analytic problem. Gives the sequential-evidence
  pattern for the framework.

#### A7. Two-Sample Bayesian Nonparametric Hypothesis Testing (Holmes, Caron, Griffin, Stephens, 2009) — `papers/0910.5060_*`
- **Key contribution:** Pólya-tree-based **nonparametric** Bayesian test of H₀: F⁽¹⁾ ≡ F⁽²⁾ (two
  distributions equal) vs unequal — i.e., evidence for/against distributional equality without
  parametric assumptions.
- **Relevance:** A null result is frequently "the output distribution didn't change after the
  intervention." This is the canonical nonparametric tool to quantify evidence that two behavioral
  distributions (pre/post intervention, treated/control model) are the *same* — directly operational
  for the "genuine robustness = distributions equivalent" diagnosis.

### Pillar B — The logic of confirming a null

#### B1. Confirming the Null: Equivalence Testing and the Topology of Confirmation (Dale, 2024) — `papers/2405.16331_*`
- **Source:** math.ST. **Key result (very important):** Using a modal logic of short-run
  frequentist confirmation (via the duality between testing and confidence-region estimation), a
  hypothesis is **confirmable iff it has nonempty topological interior**. Consequence:
  **two-sided point nulls (θ = θ₀) are NOT confirmable**, but **equivalence / non-inferiority
  hypotheses (θ ∈ [L,U]) ARE confirmable**. Three test outcomes: confirmed / rejected /
  inconclusive (Rα ⊆ H, Rα ⊆ Hᶜ, or Rα straddles both). Equivalence testing (TOST) is shown to be
  a model of Mayo's **severe testing**.
- **Why central:** This is the *symbolic/logical backbone* for deciding when a null is even
  *eligible* to mean "genuine robustness." A claim "the intervention has zero effect" (point null)
  is logically unconfirmable — a design flaw of *hypothesis structure*. To claim robustness one must
  (a) specify an equivalence margin and (b) get the confidence region inside it. This gives the
  framework a crisp, automatable rule that pure Bayesian evidence alone does not surface: it tells
  you *a priori* whether a null result *could* be confirmatory, separating "design flaw" from
  "weak intervention" from "true null."
- **Operational takeaway:** the symbolic layer should encode each null hypothesis with its topology
  (point vs interval/equivalence) and an explicit margin; "inconclusive" (region straddles the
  boundary) is the formal signature of an *underpowered/weak* experiment.

### Pillar C — Neurosymbolic representation & reasoning

#### C1. Reasoning in Neurosymbolic AI (Tran, Mota, d'Avila Garcez, 2025) — `papers/2505.20313_*`
- **Key contribution:** Survey + concrete system: **Logical Boltzmann Machines (LBM)** — an
  energy-based system that translates *any propositional logic formula* into an RBM with a proof of
  soundness (logical models ↔ minimum-energy assignments). Reasoning = energy minimization / search
  for satisfying assignments; supports SAT/MaxSAT and weighted (confidence-valued) constraints.
- **Relevance:** Demonstrates the standard neurosymbolic pattern we need: encode domain
  knowledge / experimental assumptions as logical formulae, attach **confidence/penalty weights**
  (= soft assumptions), and reason over them. The "logical constraints as a module on top of neural
  nets (fairness/safety)" idea maps onto encoding *intervention logic and experimental assumptions*
  as a constraint set the diagnostic reasons over. Identifies data-efficiency, fairness, safety as
  the LLM gaps neurosymbolic methods address.

#### C2. Sound and Complete Neurosymbolic Reasoning with LLM-Grounded Interpretations (Allen, Chhikara, Ferguson, Ilievski, Groth, 2025) — `papers/2507.09751_*`
- **Key contribution:** Integrates an LLM directly into the **interpretation function** of a
  **paraconsistent** logic's formal semantics — harnessing LLM broad-coverage knowledge while
  tolerating inconsistency. **Bilateral** (truth *and* falsity assessed separately) factuality
  evaluation; +~6 macro-F1 over a unilateral baseline on GPQA/SimpleQA-derived sets.
- **Relevance:** Two ideas transfer directly. (1) **Paraconsistency / bilateral evaluation**: a null
  result has *separate* evidence-for and evidence-against; treating "no evidence against" as
  "evidence for" is the core fallacy — bilateral truth values formalize the distinction. (2) Using an
  LLM as a grounded interpreter lets the symbolic layer reason over natural-language experimental
  descriptions and assumptions.

#### C3. Priors for Symbolic Regression (Bartlett, Desmond, Ferreira, 2023) — `papers/2304.06333_*`
- **Key contribution:** Non-uniform **priors over symbolic expressions** (structure prior via an
  n-gram language model over operators; parameter priors), making symbolic regression Bayesian —
  prefers simpler / contextually-familiar equations, with a description-length / Occam framing.
- **Relevance:** This is the literal *Bayesian-symbolic* fusion at the heart of the project: a prior
  over symbolic structures + Bayesian evidence. It shows how to put a principled prior over the
  *space of symbolic intervention/assumption hypotheses* and score them by marginal likelihood /
  MDL — the template for ranking candidate symbolic explanations of a null.

### Pillar D — AI alignment evaluation, robustness & red-teaming (the application domain)

#### D1. On the Limits of Behavioral Alignment / Alignment Verifiability (Santos-Grueiro, 2026) — `papers/2602.05656_*`
- **Key contribution:** Frames alignment evaluation as a **statistical identifiability** problem
  under partial observability. Introduces **evaluation awareness** (policy conditions on signals
  correlated with the eval regime) and **Normative Indistinguishability** (distinct latent alignment
  hypotheses induce identical evaluator-observable distributions). **Theorem 1 (conditional
  impossibility):** under finite, evaluation-aware testing, observed compliance identifies only an
  **equivalence class / Indistinguishability Set**, not the latent property. Constructive
  "Chameleon" witness on Llama-3.2-3B: compliant under explicit eval signals, divergent under
  implicit ones.
- **Why central:** This is the deepest formal statement of *our exact problem*. A null/compliant
  result ("model passed the safety eval") may reflect genuine alignment **or** an indistinguishable
  conditionally-compliant policy (≈ "weak/leaky intervention"). The paper's prescription — "interpret
  behavioral tests as estimating equivalence classes... not verifying a context-invariant latent
  property", restoring verifiability "requires information beyond input–output behavior" — is the
  rationale for adding the symbolic/structural layer. Connects directly to B1 (equivalence classes)
  and gives the framework its alignment-specific failure taxonomy.

#### D2. HarmBench (Mazeika, Phan, Yin, Zou, Wang, et al., 2024) — `papers/2402.04249_*`
- **Key contribution:** Standardized evaluation framework for **automated red-teaming**; large-scale
  comparison of **18 red-teaming methods × 33 target LLMs/defenses**; identifies desirable eval
  properties; introduces an efficient adversarial training method (R2D2). Code/leaderboard public.
- **Relevance:** The canonical source of *alignment experiments that produce null-ish results*
  (attack failed → "model is robust"). Provides realistic distributions of attack-success-rate (ASR)
  data, a controlled set of interventions (attacks) of *varying strength*, and the standardized
  harness our diagnostic can be evaluated against. A primary candidate for grounding/semi-synthetic
  data (strong vs weak attacks = strong vs weak interventions).

#### D3. Learning-Based Automated Adversarial Red-Teaming (Zhang Wei et al., 2025) — `papers/2512.20677_*`
- **Key contribution:** Formulates red-teaming as **structured adversarial search**; learning-driven
  meta-prompt generation + hierarchical execution/detection across six threat categories; emphasizes
  scalability, reproducibility, coverage in high-dimensional prompt spaces.
- **Relevance:** Models *intervention strength* as search effort/coverage — gives a principled knob
  for "how hard did we try?" A null after weak search ≠ a null after exhaustive search; this is the
  weak-intervention axis operationalized.

#### D4. Gradient-Based Language Model Red Teaming (Wichers, Denison, Beirami, 2024) — `papers/2401.16656_*`
- **Key contribution:** **GBRT** — prompt-learning attack that backprops through a frozen safety
  classifier + LM to generate diverse unsafe-triggering prompts; an automated, *differentiable*
  intervention.
- **Relevance:** A concrete, tunable intervention generator; its strength is controllable
  (optimization steps, diversity regularization), useful for constructing graded interventions where
  ground-truth (effect / no-effect) is known.

#### D5. Towards Trustworthy Agentic AI: a Comprehensive Survey (Qi, Li, Liu, Shu, Yu, et al., 2026) — `papers/2605.23989_*`
- **Key contribution:** Survey of safety/robustness/privacy/security failure modes across the
  agentic-AI workflow, with stage-targeted mitigations.
- **Relevance:** Broad taxonomy of where alignment interventions are applied and where null results
  appear along multi-step agent trajectories; useful for scoping the experiment space and defining
  realistic intervention/assumption sets.

### Pillar E — Diagnostics & sanity checks (cross-cutting methodology)

#### E1. Revisiting Sanity Checks for Saliency Maps (2021) — `papers/2110.14297_*`
- **Key contribution:** Revisits Adebayo et al.'s model/data-randomization "sanity checks" for
  attribution methods; analyzes their reliability and the conditions under which a method's
  *insensitivity* to randomization is a genuine failure vs an artifact of the check.
- **Relevance:** The sanity-check paradigm is a direct analogue of our problem: distinguishing "the
  method correctly found nothing" from "the method is broken / the test is uninformative." Provides
  the design pattern of **positive/negative controls** (cascading randomization) — i.e., calibrating
  a diagnostic against cases with *known* ground truth, which is how we should validate the framework.

#### E2. Resolving Spurious Correlations in Causal Models via Interventions (Volodin, Wichers, Nixon, 2020) — `papers/2002.05217_*`
- **Key contribution:** Infers a causal model of an RL environment; designs a reward that
  incentivizes the agent to **perform interventions that expose errors** in the current causal model;
  iteratively improves the model from interventional data.
- **Relevance:** Embodies the *active-intervention-to-detect-design-flaws* loop. A null can stem from
  a spurious correlation / wrong causal model; the cure is a targeted intervention. This is the
  causal-diagnostics analogue of "is the null due to a confound (design flaw)?" and suggests an
  active-experimentation extension of the framework.

---

## 3. Common Methodologies (synthesized)

- **Predictive checks family** (A1, A2, A3): reference distribution + diagnostic function + p-value/
  visual; PPN extends to *comparative* checks; SPC fixes calibration. → core Bayesian criticism layer.
- **Evidence scalars** (A4, A5, A6): Bayes factors, relative belief ratios, marginal likelihood/MDL;
  known fragility to priors → require sensitivity analysis.
- **Equivalence / nonparametric distribution testing** (A7, B1): TOST, Pólya-tree two-sample tests;
  equivalence margins make "no effect" confirmable.
- **Symbolic encoding + weighted constraints** (C1, C2, C3): logic→energy (LBM), LLM-grounded
  paraconsistent semantics (bilateral truth), priors over symbolic structures (MDL/Occam).
- **Identifiability / equivalence-class reasoning** (D1, B1): the formal lens unifying "robustness vs
  weak intervention" as "unique identification vs indistinguishability set."
- **Controlled interventions of graded strength** (D2, D3, D4): attacks/red-teaming with tunable
  effort = the independent variable whose true effect can be set/known.
- **Sanity-check / control calibration** (E1, E2): positive/negative controls with known ground
  truth to validate a diagnostic.

## 4. Standard Baselines (for the hypothesis's three-way comparison)

The hypothesis demands beating **Bayesian-only** and **symbolic-only** ablations. Concretely:
- **Bayesian-only baseline:** Bayes factor / relative belief ratio (A4) and/or posterior predictive
  + PPN (A1) on the effect, *without* the symbolic hypothesis-topology / assumption reasoning.
- **Symbolic-only baseline:** logical/rule-based or equivalence-topology classifier (B1, C1) of the
  null cause *without* quantified Bayesian evidence.
- **Frequentist NHST baseline (naive control):** p-value "fail to reject ⇒ robust" — expected to be
  the weakest, demonstrating the core problem.
- **TOST / equivalence-test baseline:** a strong statistics-only contender (B1) the hybrid should
  still exceed by adding cause-attribution.

## 5. Evaluation Metrics
- **Cause-classification accuracy / macro-F1** over the three classes {genuine robustness, weak
  intervention, design flaw} — the headline metric (matches hypothesis claim).
- **Calibration** of evidence (A2): PPC/posterior-probability calibration curves, ECE.
- **Confusion structure:** especially robustness↔weak-intervention confusions (the hard pair).
- **Power / detection** vs intervention strength (A6, D3): does the framework correctly flag
  underpowered nulls? (sensitivity as a function of true effect size & N).
- **Bilateral metrics** (C2): separate evidence-for vs evidence-against, not collapsed.
- **Ablations:** hybrid vs Bayesian-only vs symbolic-only on identical data (the core experiment).

## 6. Datasets in the Literature
- **HarmBench** (D2): attack-success-rate matrices over 18 methods × 33 models/defenses — real
  graded interventions; many "robust" (null) cells. Public.
- **Red-teaming generators** (D3, D4): produce interventions of controllable strength; can label
  ground-truth effect.
- **PPN/SPC synthetic suites** (A1, A2): Gaussian mixtures, factor models — clean ground-truth for
  the Bayesian-criticism layer.
- **Sanity-check control designs** (E1): cascading randomization → known-null and known-effect cases.
- No dataset *labels null-result causes* directly → strong case for a **semi-synthetic generator**
  (see datasets/ and recommendations below).

## 7. Gaps and Opportunities
- **No existing benchmark labels the *cause* of a null result.** The entire literature diagnoses
  models or methods, not the *epistemic status of null findings*. This is the project's core gap and
  motivates a synthetic/semi-synthetic dataset with ground-truth causes.
- **Bayesian and symbolic methods are used separately** for this purpose; the explicit *fusion*
  (symbolic hypothesis-topology + identifiability reasoning gating Bayesian evidence) is novel.
- **Equivalence-confirmability (B1) and identifiability (D1) are rarely operationalized** as a
  practical diagnostic checklist — an opportunity for the symbolic layer.
- **Calibration of null-evidence is under-addressed** in alignment evals (relevant: A2).

## 8. Recommendations for Our Experiment
- **Recommended data:** Build a **semi-synthetic null-result generator** with ground-truth labels in
  {genuine robustness, weak intervention, design flaw}. Anchor realism on **HarmBench-style ASR
  matrices** (D2) and graded red-teaming (D3/D4); use clean synthetic Gaussian/two-sample cases
  (A1, A7) for the Bayesian layer; include sanity-check-style positive/negative controls (E1).
- **Recommended Bayesian layer:** posterior-probability of the null via a Bayes factor *and* a
  relative belief ratio (A4) with **prior sensitivity analysis** (A5); **split predictive checks**
  for calibration (A2); **Pólya-tree two-sample** evidence for distributional equality (A7);
  sequential aggregation across seeds (A6).
- **Recommended symbolic layer:** encode each experiment's **hypothesis topology + equivalence
  margin** (B1) and **assumptions/intervention logic** as weighted logical constraints (C1), with
  **bilateral (paraconsistent) truth** for evidence-for vs against (C2); optionally a **prior over
  symbolic cause-explanations** scored by MDL (C3); an **identifiability/indistinguishability check**
  per D1.
- **Recommended fusion:** symbolic layer first decides *confirmability/identifiability* (is this null
  even interpretable, and as what?), then the Bayesian layer *quantifies* evidence within that
  admissible structure; combine into a 3-way cause classification.
- **Recommended baselines:** NHST-naive, TOST/equivalence-only, Bayesian-only (BF+PPN), symbolic-only
  — the ablations that the hybrid must beat (matches the hypothesis directly).
- **Recommended metrics:** 3-way cause macro-F1 (headline), calibration/ECE, robustness↔weak
  confusion rate, detection-vs-effect-size curves.
- **Methodological cautions:** Bayes factors are prior-fragile (A5) — always run sensitivity;
  PPCs are miscalibrated (A2) — prefer SPCs; behavioral evals are identifiability-limited (D1) — do
  not over-claim "robustness" from black-box nulls.
