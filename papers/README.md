# Downloaded Papers

18 papers, organized by the framework's four pillars. Each entry: title, authors, year, arXiv id, file, relevance.


## A. Bayesian evidence quantification & model criticism

- **The Posterior Predictive Null** (2021)
  - Authors: Gemma E. Moran, John P. Cunningham, David M. Blei
  - arXiv: 2112.03333 | File: `papers/2112.03333_2021_posterior_predictive_null.pdf`
  - Relevance: PPN check = comparative Bayesian criticism; separates 'sufficient' from 'necessary' complexity = robustness vs undetected effect. CORE.
- **Calibrated Model Criticism Using Split Predictive Checks** (2022)
  - Authors: Jiawei Li, Jonathan H. Huggins
  - arXiv: 2203.15897 | File: `papers/2203.15897_2022_calibrated_model_criticism_split_predictive_checks.pdf`
  - Relevance: Calibrated (split) predictive checks; fixes PPC miscalibration that biases toward false robustness.
- **Recommendations for visual predictive checks in Bayesian workflow** (2025)
  - Authors: Teemu Säilynoja, Andrew R. Johnson, Osvaldo A. Martin, Aki Vehtari
  - arXiv: 2503.01509 | File: `papers/2503.01509_2025_visual_predictive_checks_bayesian_workflow.pdf`
  - Relevance: Bayesian-workflow visual predictive check guidance; checks have assumptions that, if violated, mislead.
- **How to Measure Evidence and Its Strength: Bayes Factors or Relative Belief Ratios?** (2023)
  - Authors: see PDF
  - arXiv: 2301.08994 | File: `papers/2301.08994_2023_bayes_factors_vs_relative_belief_ratios.pdf`
  - Relevance: Menu of evidence scalars (Bayes factor vs relative belief ratio) for evidence *for* the null.
- **The expected demise of the Bayes factor** (2015)
  - Authors: see PDF
  - arXiv: 1506.08292 | File: `papers/1506.08292_2017_expected_demise_of_bayes_factor.pdf`
  - Relevance: Critique of default Bayes factors (prior sensitivity, Jeffreys-Lindley); motivates hybrid + sensitivity analysis.
- **Bayes Factor Hypothesis Testing in Meta-Analyses: Practical Advantages and Methodological Considerations** (2025)
  - Authors: see PDF
  - arXiv: 2511.22535 | File: `papers/2511.22535_2025_bayes_factor_meta_analyses.pdf`
  - Relevance: Sequential/cumulative Bayes-factor evidence; aggregating 'no effect' across many experiments/seeds.
- **Two-sample Bayesian Nonparametric Hypothesis Testing** (2009)
  - Authors: Chris C. Holmes, François Caron, Jim E. Griffin, David A. Stephens
  - arXiv: 0910.5060 | File: `papers/0910.5060_2009_two_sample_bayesian_nonparametric_hypothesis_testing.pdf`
  - Relevance: Nonparametric Bayesian two-sample test (F1==F2); evidence that pre/post-intervention distributions are equal.

## B. Logic of confirming the null

- **Confirming the Null: Remarks on Equivalence Testing and the Topology of Confirmation** (2024)
  - Authors: Reid Dale
  - arXiv: 2405.16331 | File: `papers/2405.16331_2024_confirming_the_null_equivalence_testing.pdf`
  - Relevance: Confirmable iff nonempty interior: point nulls NOT confirmable, equivalence hypotheses ARE. Symbolic backbone for when a null can mean robustness. CORE.

## C. Neurosymbolic representation & reasoning

- **Reasoning in Neurosymbolic AI** (2025)
  - Authors: Son Tran, Edjard Mota, Artur d'Avila Garcez
  - arXiv: 2505.20313 | File: `papers/2505.20313_2025_reasoning_in_neurosymbolic_ai.pdf`
  - Relevance: Logical Boltzmann Machines: encode propositional logic as energy-based net with weighted constraints; neurosymbolic template.
- **Sound and Complete Neurosymbolic Reasoning with LLM-Grounded Interpretations** (2025)
  - Authors: Bradley P. Allen, Prateek Chhikara, Thomas Macaulay Ferguson, Filip Ilievski
  - arXiv: 2507.09751 | File: `papers/2507.09751_2025_sound_complete_neurosymbolic_llm_grounded.pdf`
  - Relevance: LLM-grounded paraconsistent logic; bilateral truth (evidence-for vs evidence-against) — directly addresses the null-result fallacy.
- **Priors for symbolic regression** (2023)
  - Authors: Deaglan J. Bartlett, Harry Desmond, Pedro G. Ferreira
  - arXiv: 2304.06333 | File: `papers/2304.06333_2023_priors_for_symbolic_regression.pdf`
  - Relevance: Bayesian priors over symbolic expressions (n-gram structure prior + MDL); the literal Bayesian-symbolic fusion template.

## D. AI alignment evaluation, robustness & red-teaming

- **Alignment Verifiability in Large Language Models: Normative Indistinguishability under Behavioral Evaluation** (2026)
  - Authors: Igor Santos-Grueiro
  - arXiv: 2602.05656 | File: `papers/2602.05656_2026_alignment_verifiability_llm.pdf`
  - Relevance: Alignment verifiability as identifiability; compliance identifies an equivalence/indistinguishability class, not latent alignment. CORE problem statement.
- **HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal** (2024)
  - Authors: Mantas Mazeika, Long Phan, Xuwang Yin, Andy Zou
  - arXiv: 2402.04249 | File: `papers/2402.04249_2024_harmbench_red_teaming_eval.pdf`
  - Relevance: HarmBench: standardized automated red-teaming, 18 methods x 33 models; source of realistic graded interventions & null cells.
- **Learning-Based Automated Adversarial Red-Teaming for Robustness Evaluation of Large Language Models** (2025)
  - Authors: Zhang Wei, Hanxuan Chen, Peilu Hu, Zhenyuan Wei
  - arXiv: 2512.20677 | File: `papers/2512.20677_2025_learning_based_automated_adversarial_redteaming.pdf`
  - Relevance: Red-teaming as structured adversarial search; intervention strength = search effort/coverage.
- **Gradient-Based Language Model Red Teaming** (2024)
  - Authors: Nevan Wichers, Carson Denison, Ahmad Beirami
  - arXiv: 2401.16656 | File: `papers/2401.16656_2024_gradient_based_lm_red_teaming.pdf`
  - Relevance: GBRT: gradient-based, tunable differentiable red-teaming attack (controllable strength).
- **Towards trustworthy agentic AI: a comprehensive survey of safety, robustness, privacy, and system security** (2026)
  - Authors: Jinhu Qi, Muzhi Li, Jiahong Liu, Yuqin Shu
  - arXiv: 2605.23989 | File: `papers/2605.23989_2026_trustworthy_agentic_ai_survey.pdf`
  - Relevance: Survey of agentic-AI safety/robustness failure modes; scopes intervention/assumption space.

## E. Diagnostics & sanity checks

- **Revisiting Sanity Checks for Saliency Maps** (2021)
  - Authors: see PDF
  - arXiv: 2110.14297 | File: `papers/2110.14297_2021_revisiting_sanity_checks_saliency.pdf`
  - Relevance: Sanity checks for saliency: distinguishing 'correctly found nothing' from 'broken/uninformative'; positive/negative control design.
- **Resolving Spurious Correlations in Causal Models of Environments via Interventions** (2020)
  - Authors: Sergei Volodin, Nevan Wichers, Jeremy Nixon
  - arXiv: 2002.05217 | File: `papers/2002.05217_2020_spurious_correlations_via_interventions.pdf`
  - Relevance: Causal interventions to expose spurious correlations / wrong causal models = design-flaw diagnosis loop.
