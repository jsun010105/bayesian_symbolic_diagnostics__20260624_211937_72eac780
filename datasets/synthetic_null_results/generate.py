"""
Semi-synthetic generator of *labeled* null-result scenarios for AI-alignment experiments.

Motivation (see ../../literature_review.md):
  No public dataset labels the CAUSE of a null result. Every alignment-eval dataset diagnoses
  models/methods, not the epistemic status of a "no-effect" finding. This generator fills that gap
  with ground-truth labels in three classes the framework must separate:

    0 GENUINE_ROBUSTNESS  - true effect ~ 0; the model really is invariant to the intervention.
    1 WEAK_INTERVENTION   - a real effect exists but the experiment is underpowered to detect it
                            (small effect, small N, or low intervention strength / attack budget).
    2 DESIGN_FLAW         - the null is uninterpretable: confound, measurement/leakage failure,
                            evaluation-awareness (D1: 2602.05656), or an unconfirmable hypothesis
                            topology (point null, no equivalence margin; B1: 2405.16331).

Each scenario emits BOTH:
  * raw observations (control vs treated measurements) -> the BAYESIAN layer (Bayes factor / TOST /
    posterior-predictive / two-sample evidence) consumes these.
  * symbolic / structural features (hypothesis topology, equivalence margin set?, intervention
    strength, confound present?, evaluation-awareness, identifiability) -> the SYMBOLIC layer.

This dual emission is what enables the core ablation: Bayesian-only vs symbolic-only vs hybrid.

Design parameters are grounded in the reviewed literature:
  - effect size / N / power            -> A2,A6 (calibration, sequential evidence)
  - equivalence margin & topology      -> B1 (confirmable iff nonempty interior)
  - intervention strength / search budget -> D2,D3,D4 (red-teaming as graded search)
  - confound / evaluation-awareness    -> D1 (identifiability), E2 (spurious correlations)
  - positive/negative controls         -> E1 (sanity checks)

Usage:
  python generate.py --n 3000 --seed 0 --out null_results.csv
"""
import argparse, json, csv, math, random

LABELS = {0: "GENUINE_ROBUSTNESS", 1: "WEAK_INTERVENTION", 2: "DESIGN_FLAW"}


def draw_scenario(rng):
    """Return (raw_dict, symbolic_dict, label) for one experiment."""
    label = rng.choice([0, 1, 2])

    # --- common experiment knobs ---
    n = rng.choice([10, 20, 30, 50, 100, 200, 500])          # samples per arm
    noise = rng.uniform(0.5, 2.0)                             # measurement sd
    intervention_strength = rng.uniform(0.0, 1.0)            # attack budget / search effort (D2-D4)

    # symbolic/structural flags (defaults = a clean, interpretable design)
    hypothesis_topology = "equivalence"   # 'equivalence' (interval, confirmable) | 'point' (not)
    equivalence_margin_set = True         # was a TOST margin specified? (B1)
    confound_present = False              # E2
    evaluation_awareness = False         # D1
    measurement_valid = True
    identifiable = True

    if label == 0:  # GENUINE ROBUSTNESS: true effect ~ 0, decent power
        true_effect = rng.gauss(0.0, 0.03)                   # essentially null
        n = rng.choice([100, 200, 500])                      # adequately powered
        intervention_strength = rng.uniform(0.6, 1.0)        # a *strong* intervention still found nothing
        equivalence_margin_set = True
        hypothesis_topology = "equivalence"

    elif label == 1:  # WEAK INTERVENTION: real effect, underpowered to detect
        true_effect = rng.uniform(0.15, 0.6) * rng.choice([-1, 1])  # genuine, non-trivial
        # underpowered via at least one mechanism:
        mech = rng.choice(["small_n", "weak_attack", "coarse_metric"])
        if mech == "small_n":
            n = rng.choice([10, 20, 30])
        elif mech == "weak_attack":
            intervention_strength = rng.uniform(0.0, 0.3)    # barely perturbed -> observed effect shrinks
            true_effect *= intervention_strength             # weak attack reveals only a fraction
        else:  # coarse_metric -> inflate noise
            noise = rng.uniform(2.0, 4.0)
        hypothesis_topology = "equivalence"
        equivalence_margin_set = True

    else:  # DESIGN FLAW: uninterpretable null
        true_effect = rng.uniform(0.0, 0.5) * rng.choice([-1, 1])
        flaw = rng.choice(["confound", "eval_aware", "broken_metric", "point_null"])
        if flaw == "confound":
            confound_present = True; identifiable = False
        elif flaw == "eval_aware":
            evaluation_awareness = True; identifiable = False   # D1: indistinguishability set
            true_effect = 0.0                                   # looks compliant under eval signal
        elif flaw == "broken_metric":
            measurement_valid = False; noise = rng.uniform(3.0, 6.0)
        else:  # point_null: hypothesis not confirmable (B1)
            hypothesis_topology = "point"; equivalence_margin_set = False

    # --- generate raw measurements (control vs treated) ---
    control = [rng.gauss(0.0, noise) for _ in range(n)]
    treated = [rng.gauss(true_effect, noise) for _ in range(n)]
    # confound injects a spurious shift correlated with the arm, masking/mimicking effect
    if confound_present:
        shift = rng.uniform(0.2, 0.5) * rng.choice([-1, 1])
        treated = [t + shift for t in treated]               # observed ~0 net effect by cancellation
        if abs(true_effect + shift) < 0.05:
            pass  # confound cancels real effect -> deceptive null

    obs_diff = (sum(treated) / n) - (sum(control) / n)

    raw = {
        "n_per_arm": n,
        "noise_sd": round(noise, 4),
        "control_mean": round(sum(control) / n, 4),
        "treated_mean": round(sum(treated) / n, 4),
        "observed_diff": round(obs_diff, 4),
        "control_var": round(_var(control), 4),
        "treated_var": round(_var(treated), 4),
        "true_effect": round(true_effect, 4),   # ground-truth latent (for analysis only)
    }
    symbolic = {
        "hypothesis_topology": hypothesis_topology,
        "equivalence_margin_set": equivalence_margin_set,
        "equivalence_margin": round(rng.uniform(0.1, 0.3), 3) if equivalence_margin_set else None,
        "intervention_strength": round(intervention_strength, 4),
        "confound_present": confound_present,
        "evaluation_awareness": evaluation_awareness,
        "measurement_valid": measurement_valid,
        "identifiable": identifiable,
    }
    return raw, symbolic, label


def _var(xs):
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / max(1, len(xs) - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="null_results.csv")
    ap.add_argument("--jsonl", default="null_results.jsonl")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    rows = []
    for _ in range(args.n):
        raw, sym, label = draw_scenario(rng)
        row = {**raw, **sym, "label": label, "label_name": LABELS[label]}
        rows.append(row)

    cols = list(rows[0].keys())
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    with open(args.jsonl, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    from collections import Counter
    dist = Counter(r["label_name"] for r in rows)
    print(f"Wrote {len(rows)} scenarios -> {args.out}, {args.jsonl}")
    print("Class balance:", dict(dist))


if __name__ == "__main__":
    main()
