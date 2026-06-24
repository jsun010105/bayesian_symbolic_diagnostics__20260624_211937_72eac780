"""
E1 (main ablation), E3 (mechanism/error analysis), E4 (sensitivity).
Runs all diagnostic methods on the held-out test set, computes macro-F1 with bootstrap CIs,
McNemar tests vs Hybrid, Cohen's kappa, confusion matrices, calibration (ECE), and a
prior/margin sensitivity sweep for the Hybrid. Saves JSON + figures.
"""
import json, math, random, time
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix, cohen_kappa_score
from scipy.stats import binomtest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.framework import METHODS, LABELS, hybrid_diagnose

SEED = 42
random.seed(SEED); np.random.seed(SEED)
TEST = "datasets/synthetic_null_results/null_results_test.csv"
CLASS_NAMES = ["GENUINE_ROB", "WEAK_INTERV", "DESIGN_FLAW"]


def predict(method_fn, df, **kw):
    preds, confs = [], []
    for _, r in df.iterrows():
        lab, conf, _ = method_fn(r.to_dict(), **kw) if kw else method_fn(r.to_dict())
        preds.append(lab); confs.append(conf)
    return np.array(preds), np.array(confs)


def bootstrap_macroF1(y, yhat, n_boot=1000, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(y); scores = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        scores.append(f1_score(y[idx], yhat[idx], average="macro", labels=[0, 1, 2], zero_division=0))
    lo, hi = np.percentile(scores, [2.5, 97.5])
    return float(np.mean(scores)), float(lo), float(hi)


def mcnemar(y, a, b):
    """Exact McNemar test on paired correctness of predictors a vs b."""
    ca, cb = (a == y), (b == y)
    n01 = int(np.sum(~ca & cb))   # a wrong, b right
    n10 = int(np.sum(ca & ~cb))   # a right, b wrong
    nd = n01 + n10
    if nd == 0:
        return 1.0, n01, n10
    p = binomtest(min(n01, n10), nd, 0.5, alternative="two-sided").pvalue
    return float(p), n01, n10


def ece(y, yhat, conf, n_bins=10):
    """Expected Calibration Error using predicted-class confidence as the probability."""
    correct = (y == yhat).astype(float)
    bins = np.linspace(0, 1, n_bins + 1)
    e = 0.0
    for i in range(n_bins):
        m = (conf > bins[i]) & (conf <= bins[i + 1])
        if m.sum() > 0:
            e += (m.sum() / len(y)) * abs(correct[m].mean() - conf[m].mean())
    return float(e)


def main():
    df = pd.read_csv(TEST)
    y = df["label"].to_numpy()
    print(f"Test set: {len(df)} scenarios, class balance {np.bincount(y).tolist()}")

    results = {"n_test": int(len(df)), "seed": SEED, "methods": {}}
    preds_all, confs_all = {}, {}
    t0 = time.time()
    for name, fn in METHODS.items():
        yhat, conf = predict(fn, df)
        preds_all[name] = yhat; confs_all[name] = conf
        mf1, lo, hi = bootstrap_macroF1(y, yhat)
        per_class = f1_score(y, yhat, average=None, labels=[0, 1, 2], zero_division=0)
        results["methods"][name] = {
            "macro_f1": mf1, "macro_f1_ci": [lo, hi],
            "accuracy": float(accuracy_score(y, yhat)),
            "per_class_f1": {CLASS_NAMES[i]: float(per_class[i]) for i in range(3)},
            "kappa_vs_truth": float(cohen_kappa_score(y, yhat)),
            "ece": ece(y, yhat, conf),
            "confusion": confusion_matrix(y, yhat, labels=[0, 1, 2]).tolist(),
        }
        print(f"  {name:14s} macroF1={mf1:.3f} [{lo:.3f},{hi:.3f}] acc={results['methods'][name]['accuracy']:.3f}")

    # McNemar: Hybrid vs each baseline (+ Holm correction)
    results["mcnemar_vs_hybrid"] = {}
    pvals = {}
    for name in METHODS:
        if name == "Hybrid":
            continue
        p, n01, n10 = mcnemar(y, preds_all[name], preds_all["Hybrid"])
        pvals[name] = p
        results["mcnemar_vs_hybrid"][name] = {"p_raw": p, "hybrid_better_minus_worse": n01 - n10}
    # Holm correction
    ordered = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(ordered)
    for rank, (name, p) in enumerate(ordered):
        results["mcnemar_vs_hybrid"][name]["p_holm"] = min(1.0, p * (m - rank))

    results["runtime_sec"] = round(time.time() - t0, 1)

    with open("results/main_results.json", "w") as f:
        json.dump(results, f, indent=2)
    np.savez("results/predictions.npz", y=y, **{f"pred_{k}": v for k, v in preds_all.items()},
             **{f"conf_{k}": v for k, v in confs_all.items()})

    # ---- E4: sensitivity to Bayes-factor prior scale and equivalence margin (Hybrid only) ----
    sens = {"bf_prior_r": {}, "note": "Hybrid macro-F1 under prior/margin perturbations"}
    for r in [0.354, 0.5, 0.707, 1.0, 1.414]:
        yhat, _ = predict(lambda row: hybrid_diagnose(row, bf_prior_r=r), df)
        sens["bf_prior_r"][str(r)] = float(f1_score(y, yhat, average="macro", labels=[0, 1, 2]))
    results["sensitivity"] = sens
    with open("results/main_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Sensitivity (BF prior r):", {k: round(v, 3) for k, v in sens["bf_prior_r"].items()})

    make_figures(results, preds_all, y)
    print(f"Done in {results['runtime_sec']}s. Wrote results/main_results.json + figures/.")


def make_figures(results, preds_all, y):
    order = ["NHST_naive", "TOST_only", "Bayesian_only", "Symbolic_only", "Hybrid"]
    # Fig 1: macro-F1 with bootstrap CIs
    fig, ax = plt.subplots(figsize=(7, 4.2))
    xs = range(len(order))
    mf = [results["methods"][m]["macro_f1"] for m in order]
    los = [results["methods"][m]["macro_f1"] - results["methods"][m]["macro_f1_ci"][0] for m in order]
    his = [results["methods"][m]["macro_f1_ci"][1] - results["methods"][m]["macro_f1"] for m in order]
    colors = ["#bbb", "#bbb", "#6aa", "#a86", "#27a"]
    ax.bar(xs, mf, yerr=[los, his], capsize=5, color=colors)
    for i, v in enumerate(mf):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=9)
    ax.set_xticks(list(xs)); ax.set_xticklabels(order, rotation=20, ha="right")
    ax.set_ylabel("3-way macro-F1"); ax.set_ylim(0, 1.05)
    ax.set_title("Diagnostic accuracy: Hybrid vs baselines (95% bootstrap CI)")
    plt.tight_layout(); plt.savefig("figures/fig1_macroF1.png", dpi=130); plt.close()

    # Fig 2: confusion matrices
    fig, axes = plt.subplots(1, len(order), figsize=(3.0 * len(order), 3.1))
    for ax, m in zip(axes, order):
        cm = np.array(results["methods"][m]["confusion"])
        cmn = cm / cm.sum(axis=1, keepdims=True).clip(min=1)
        im = ax.imshow(cmn, vmin=0, vmax=1, cmap="Blues")
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{cmn[i,j]:.2f}", ha="center", va="center",
                        color="white" if cmn[i, j] > 0.5 else "black", fontsize=8)
        ax.set_title(m, fontsize=9)
        ax.set_xticks(range(3)); ax.set_yticks(range(3))
        ax.set_xticklabels(["GR", "WI", "DF"], fontsize=8); ax.set_yticklabels(["GR", "WI", "DF"], fontsize=8)
        ax.set_xlabel("pred", fontsize=8)
    axes[0].set_ylabel("true", fontsize=8)
    plt.suptitle("Row-normalised confusion matrices (GR=robustness, WI=weak, DF=design flaw)", fontsize=10)
    plt.tight_layout(); plt.savefig("figures/fig2_confusion.png", dpi=130); plt.close()

    # Fig 3: sensitivity
    fig, ax = plt.subplots(figsize=(6, 3.8))
    s = results["sensitivity"]["bf_prior_r"]
    ks = sorted(s.keys(), key=float)
    ax.plot([float(k) for k in ks], [s[k] for k in ks], "o-", color="#27a")
    ax.set_xlabel("Bayes-factor prior scale r (Cauchy)"); ax.set_ylabel("Hybrid macro-F1")
    ax.set_ylim(0, 1.05); ax.axhline(results["methods"]["Hybrid"]["macro_f1"], ls="--", color="gray", lw=0.8)
    ax.set_title("E4: Hybrid robustness to Bayes-factor prior specification")
    plt.tight_layout(); plt.savefig("figures/fig3_sensitivity.png", dpi=130); plt.close()


if __name__ == "__main__":
    main()
