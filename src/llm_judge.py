"""
E2: Real-LLM expert-judge baseline.

A state-of-the-art LLM (via OpenRouter) is shown each scenario in natural language -- with BOTH the
raw statistics AND the structural design notes the framework uses -- and asked to diagnose the cause
of the null result as GENUINE_ROBUSTNESS / WEAK_INTERVENTION / DESIGN_FLAW with a one-line rationale.
This tests whether a strong general reasoner already solves the task, and yields framework<->LLM
Cohen's kappa. Runs on a stratified subset; responses are cached to results/llm_cache.json.
"""
import os, json, time, random, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score, cohen_kappa_score, confusion_matrix

from src.framework import hybrid_diagnose, symbolic_diagnose, bayesian_diagnose, LABELS

MODEL = "openai/gpt-4.1"
TEST = "datasets/synthetic_null_results/null_results_test.csv"
CACHE = "results/llm_cache.json"
NAME2LAB = {"GENUINE_ROBUSTNESS": 0, "WEAK_INTERVENTION": 1, "DESIGN_FLAW": 2}
KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")

SYSTEM = (
    "You are an expert methodologist diagnosing the CAUSE of a NULL/ambiguous result in an AI "
    "alignment experiment (an intervention that appeared to have no effect). Classify the cause as "
    "exactly one of:\n"
    "- GENUINE_ROBUSTNESS: the effect truly is ~0; the model is genuinely invariant, and the study "
    "was adequately powered with a substantive intervention.\n"
    "- WEAK_INTERVENTION: a real effect likely exists but the experiment was underpowered to detect "
    "it (too few samples, a weak/low-budget intervention, or a noisy/coarse metric).\n"
    "- DESIGN_FLAW: the null is uninterpretable due to a confound, evaluation-awareness/leakage, an "
    "invalid measurement, or a logically unconfirmable hypothesis (point null / no equivalence margin).\n"
    'Respond ONLY with compact JSON: {"label": "<ONE_OF_THE_THREE>", "reason": "<one sentence>"}.'
)


def render(row):
    sd = ((float(row["control_var"]) + float(row["treated_var"])) / 2) ** 0.5
    margin = row["equivalence_margin"]
    margin_s = f"{float(margin):.2f}" if pd.notna(margin) and margin not in (None, "") else "NOT SPECIFIED"
    return (
        f"Experiment report:\n"
        f"- Samples per arm (N): {int(row['n_per_arm'])}\n"
        f"- Observed mean difference (treated - control): {float(row['observed_diff']):.3f}\n"
        f"- Estimated measurement noise (sd): {sd:.2f}\n"
        f"- Intervention strength / attack budget (0=none, 1=maximal): {float(row['intervention_strength']):.2f}\n"
        f"- Hypothesis topology: {row['hypothesis_topology']} (equivalence margin: +/- {margin_s})\n"
        f"- Confound present: {bool(row['confound_present'])}\n"
        f"- Evaluation-awareness/leakage: {bool(row['evaluation_awareness'])}\n"
        f"- Measurement valid: {bool(row['measurement_valid'])}\n"
        f"- Effect identifiable: {bool(row['identifiable'])}\n"
        f"What is the most likely CAUSE of this null result?"
    )


def call(prompt, retries=4):
    for a in range(retries):
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                json={"model": MODEL, "temperature": 0.0, "max_tokens": 120,
                      "messages": [{"role": "system", "content": SYSTEM},
                                   {"role": "user", "content": prompt}]},
                timeout=60)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            time.sleep(2 * (a + 1))
        except Exception:
            time.sleep(2 * (a + 1))
    return None


def parse(txt):
    if not txt:
        return None, ""
    try:
        s = txt[txt.index("{"):txt.rindex("}") + 1]
        o = json.loads(s)
        return NAME2LAB.get(str(o.get("label", "")).strip().upper()), o.get("reason", "")
    except Exception:
        for k, v in NAME2LAB.items():
            if k in txt.upper():
                return v, txt[:120]
        return None, txt[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    assert KEY, "No OpenRouter API key in environment"

    df = pd.read_csv(TEST)
    # stratified subset: equal per class, deterministic
    rng = np.random.default_rng(0)
    per = args.n // 3
    idx = []
    for c in [0, 1, 2]:
        ci = df.index[df["label"] == c].to_numpy()
        idx.extend(rng.choice(ci, size=per, replace=False).tolist())
    sub = df.loc[idx].reset_index(drop=True)

    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    t0 = time.time()

    def work(i):
        row = sub.iloc[i].to_dict()
        ck = str(int(idx[i]))
        if ck in cache:
            return i, cache[ck]
        txt = call(render(row))
        lab, reason = parse(txt)
        return i, {"label": lab, "reason": reason, "raw": txt}

    out = [None] * len(sub)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for fut in as_completed([ex.submit(work, i) for i in range(len(sub))]):
            i, res = fut.result()
            out[i] = res
            cache[str(int(idx[i]))] = res
    json.dump(cache, open(CACHE, "w"), indent=2)

    y = sub["label"].to_numpy()
    llm = np.array([o["label"] if o["label"] is not None else 1 for o in out])  # default weak if unparsed
    n_unparsed = sum(1 for o in out if o["label"] is None)

    # framework predictions on the SAME subset for paired comparison
    hyb = np.array([hybrid_diagnose(sub.iloc[i].to_dict())[0] for i in range(len(sub))])
    sym = np.array([symbolic_diagnose(sub.iloc[i].to_dict())[0] for i in range(len(sub))])
    bay = np.array([bayesian_diagnose(sub.iloc[i].to_dict())[0] for i in range(len(sub))])

    res = {
        "model": MODEL, "n": int(len(sub)), "n_unparsed": int(n_unparsed),
        "runtime_sec": round(time.time() - t0, 1),
        "LLM_judge": {
            "accuracy": float(accuracy_score(y, llm)),
            "macro_f1": float(f1_score(y, llm, average="macro", labels=[0, 1, 2], zero_division=0)),
            "per_class_f1": dict(zip(["GR", "WI", "DF"],
                                     [float(x) for x in f1_score(y, llm, average=None, labels=[0, 1, 2], zero_division=0)])),
            "kappa_vs_truth": float(cohen_kappa_score(y, llm)),
            "confusion": confusion_matrix(y, llm, labels=[0, 1, 2]).tolist(),
        },
        "on_subset": {
            "Hybrid_macro_f1": float(f1_score(y, hyb, average="macro", labels=[0, 1, 2], zero_division=0)),
            "Symbolic_macro_f1": float(f1_score(y, sym, average="macro", labels=[0, 1, 2], zero_division=0)),
            "Bayesian_macro_f1": float(f1_score(y, bay, average="macro", labels=[0, 1, 2], zero_division=0)),
            "Hybrid_acc": float(accuracy_score(y, hyb)),
        },
        "agreement_kappa": {
            "LLM_vs_Hybrid": float(cohen_kappa_score(llm, hyb)),
            "LLM_vs_truth": float(cohen_kappa_score(y, llm)),
            "Hybrid_vs_truth": float(cohen_kappa_score(y, hyb)),
        },
    }
    json.dump(res, open("results/llm_judge_results.json", "w"), indent=2)
    print(json.dumps({k: res[k] for k in ["model", "n", "n_unparsed", "runtime_sec"]}, indent=2))
    print("LLM judge:", {k: round(v, 3) if isinstance(v, float) else v
                         for k, v in res["LLM_judge"].items() if k != "confusion"})
    print("LLM confusion[GR,WI,DF]:", res["LLM_judge"]["confusion"])
    print("On subset:", {k: round(v, 3) for k, v in res["on_subset"].items()})
    print("Agreement kappa:", {k: round(v, 3) for k, v in res["agreement_kappa"].items()})


if __name__ == "__main__":
    main()
