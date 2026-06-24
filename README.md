# Bayesian–Symbolic Diagnostics for Null Results in AI Alignment

A diagnostic framework that classifies *why* an AI-alignment experiment produced a **null result** —
**genuine robustness** vs **weak intervention** vs **design flaw** — by fusing Bayesian evidence/power
quantification with symbolic reasoning about experimental structure, with interpretable reasoning chains.

## Key findings

- **The hybrid wins decisively.** 3-way macro-F1 on 3,000 held-out scenarios: **Hybrid 0.991**
  [0.987, 0.994] ≫ Symbolic-only 0.871 > Bayesian-only 0.489 > TOST-only 0.326 > NHST-naive 0.244.
  All gaps significant (McNemar exact, Holm-corrected p ≪ 0.001), non-overlapping bootstrap CIs.
- **The gain is mechanistic.** Bayesian-only is blind to design flaws (**DESIGN_FLAW F1 = 0.00**);
  Symbolic-only is blind to sample size/noise and mislabels 371/989 underpowered cases as robustness.
  The hybrid is the only method with the inputs to fix *both*.
- **Beats a frontier LLM given the same info.** A real **GPT-4.1** expert judge (via OpenRouter)
  scored macro-F1 = 0.888 (κ = 0.83 vs truth) — competitive but below the Hybrid's 0.993 on the
  identical subset. Structure adds value a strong general reasoner does not supply for free.
- **Robust & interpretable.** Stable across Bayes-factor prior scales (macro-F1 ∈ [0.989, 0.993]);
  every diagnosis is a short reasoning chain naming the operative evidence/failed check.

See **[REPORT.md](REPORT.md)** for the full write-up.

## Reproduce

```bash
source .venv/bin/activate                      # uv-managed env (deps in pyproject.toml)
# 1) (re)generate held-out test set
python datasets/synthetic_null_results/generate.py --n 3000 --seed 7 \
    --out datasets/synthetic_null_results/null_results_test.csv \
    --jsonl datasets/synthetic_null_results/null_results_test.jsonl
# 2) main ablation + analysis + sensitivity (CPU, ~9 s)
PYTHONPATH=. python src/run_experiments.py
# 3) real-LLM expert judge (needs OPENROUTER_API_KEY; ~7 min, cached)
PYTHONPATH=. python src/llm_judge.py --n 150 --workers 8
# 4) interpretability examples + combined figure
PYTHONPATH=. python src/interpret_and_combine.py
```

## File structure

```
planning.md                     Phase-0/1 motivation, novelty, design, analysis plan
REPORT.md                       Full research report (primary deliverable)
src/framework.py                Bayesian + symbolic + hybrid diagnostics & baselines
src/run_experiments.py          E1 ablation, E3 mechanism, E4 sensitivity, figures, stats
src/llm_judge.py                E2 real-LLM (GPT-4.1) expert-judge baseline
src/interpret_and_combine.py    Reasoning-chain dump + combined figure
results/                        main_results.json, llm_judge_results.json, predictions.npz,
                                example_reasoning_chains.json, llm_cache.json
figures/                        fig1 macro-F1 · fig2 confusion · fig3 sensitivity · fig4 all-methods
datasets/synthetic_null_results/  ground-truth-labelled generator + data (regenerable)
literature_review.md, papers/, code/   pre-gathered resources (18 papers, HarmBench, PPN ref)
```

**Compute:** CPU-only. Framework + analysis ≈ 9 s; LLM judge ≈ 7 min (150 API calls). Seeds fixed (42).
