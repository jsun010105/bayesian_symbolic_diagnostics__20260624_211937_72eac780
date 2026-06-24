"""
Interpretability dump (example reasoning chains, one correct case per class) + combined figure
placing the real-LLM judge alongside the framework methods.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.framework import hybrid_diagnose, LABELS

df = pd.read_csv("datasets/synthetic_null_results/null_results_test.csv")
main = json.load(open("results/main_results.json"))
llm = json.load(open("results/llm_judge_results.json"))

# ---- example reasoning chains (first correctly-classified case of each class) ----
examples = []
for c in [0, 1, 2]:
    for _, row in df[df["label"] == c].iterrows():
        lab, conf, chain = hybrid_diagnose(row.to_dict())
        if lab == c:
            examples.append({"true": LABELS[c], "predicted": LABELS[lab],
                             "confidence": round(conf, 2), "reasoning_chain": chain})
            break
json.dump(examples, open("results/example_reasoning_chains.json", "w"), indent=2)
print("=== Example interpretable diagnoses (Hybrid) ===")
for e in examples:
    print(f"\n[{e['true']}] (conf {e['confidence']}):\n  {e['reasoning_chain']}")

# ---- combined figure: macro-F1 across all methods incl. real-LLM judge ----
order = ["NHST_naive", "TOST_only", "Bayesian_only", "Symbolic_only", "LLM_judge\n(GPT-4.1)", "Hybrid"]
vals = [main["methods"]["NHST_naive"]["macro_f1"],
        main["methods"]["TOST_only"]["macro_f1"],
        main["methods"]["Bayesian_only"]["macro_f1"],
        main["methods"]["Symbolic_only"]["macro_f1"],
        llm["LLM_judge"]["macro_f1"],
        main["methods"]["Hybrid"]["macro_f1"]]
colors = ["#bbb", "#bbb", "#6aa", "#a86", "#d68", "#27a"]
fig, ax = plt.subplots(figsize=(7.6, 4.3))
ax.bar(range(len(order)), vals, color=colors)
for i, v in enumerate(vals):
    ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=9)
ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=15, ha="right", fontsize=9)
ax.set_ylabel("3-way macro-F1"); ax.set_ylim(0, 1.08)
ax.set_title("Diagnostic accuracy across methods (LLM judge on stratified n=150 subset)")
ax.axhline(main["methods"]["Hybrid"]["macro_f1"], ls="--", color="gray", lw=0.7)
plt.tight_layout(); plt.savefig("figures/fig4_all_methods.png", dpi=130); plt.close()
print("\nWrote results/example_reasoning_chains.json + figures/fig4_all_methods.png")
