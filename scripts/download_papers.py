import urllib.request, os, time, ssl, json

# Curated papers: (arxiv_id, filename_slug)
papers = [
    # Bayesian evidence / null / model criticism
    ("2112.03333", "2021_posterior_predictive_null"),
    ("2405.16331", "2024_confirming_the_null_equivalence_testing"),
    ("2301.08994", "2023_bayes_factors_vs_relative_belief_ratios"),
    ("1506.08292", "2017_expected_demise_of_bayes_factor"),
    ("2503.01509", "2025_visual_predictive_checks_bayesian_workflow"),
    ("2203.15897", "2022_calibrated_model_criticism_split_predictive_checks"),
    ("2511.22535", "2025_bayes_factor_meta_analyses"),
    ("0910.5060",  "2009_two_sample_bayesian_nonparametric_hypothesis_testing"),
    # Neurosymbolic / symbolic
    ("2505.20313", "2025_reasoning_in_neurosymbolic_ai"),
    ("2507.09751", "2025_sound_complete_neurosymbolic_llm_grounded"),
    ("2304.06333", "2023_priors_for_symbolic_regression"),
    # Alignment / eval / robustness / red teaming
    ("2402.04249", "2024_harmbench_red_teaming_eval"),
    ("2512.20677", "2025_learning_based_automated_adversarial_redteaming"),
    ("2602.05656", "2026_alignment_verifiability_llm"),
    ("2605.23989", "2026_trustworthy_agentic_ai_survey"),
    # Diagnostics / sanity checks / causal interventions
    ("2110.14297", "2021_revisiting_sanity_checks_saliency"),
    ("2002.05217", "2020_spurious_correlations_via_interventions"),
    ("2401.16656", "2024_gradient_based_lm_red_teaming"),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
os.makedirs("papers", exist_ok=True)
results=[]
for aid, slug in papers:
    fn = f"papers/{aid}_{slug}.pdf"
    if os.path.exists(fn) and os.path.getsize(fn) > 10000:
        print(f"SKIP exists {fn}")
        results.append((aid,fn,os.path.getsize(fn)))
        continue
    url = f"https://arxiv.org/pdf/{aid}.pdf"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 research"})
            with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
                data = r.read()
            with open(fn,"wb") as f:
                f.write(data)
            print(f"OK {fn} ({len(data)//1024} KB)")
            results.append((aid,fn,len(data)))
            break
        except Exception as e:
            print(f"  retry {attempt} {aid}: {e}")
            time.sleep(4)
    time.sleep(2)
print(f"\nDownloaded/present: {len(results)}/{len(papers)}")
