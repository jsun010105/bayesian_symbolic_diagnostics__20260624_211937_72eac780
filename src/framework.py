"""
Bayesian-Symbolic Diagnostic framework for interpreting null results.

Three diagnostic classes (ground truth from the synthetic generator):
    0 GENUINE_ROBUSTNESS  - true effect ~ 0, adequately powered, strong intervention.
    1 WEAK_INTERVENTION   - real effect but underpowered (small N / weak attack / coarse metric).
    2 DESIGN_FLAW         - uninterpretable null (confound, eval-awareness, broken metric,
                            or unconfirmable point-null topology).

Layers
------
Bayesian layer  : consumes raw observations (n, observed_diff, variances, margin) -> JZS Bayes
                  factor for null vs effect, TOST equivalence, and a confirmability/power signal.
Symbolic layer  : consumes structural flags -> weighted logical rules over confirmability (B1)
                  and identifiability (D1), plus intervention-strength for robustness vs weak.
Hybrid          : symbolic gates confirmability/identifiability (catches DESIGN_FLAW that the
                  Bayesian evidence cannot see), then the Bayesian evidence+power layer separates
                  GENUINE_ROBUSTNESS from WEAK_INTERVENTION within the admissible structure.

All decision functions return (label:int, confidence:float, reasoning:str).
"""
import math
from scipy import stats
from scipy.integrate import quad

GENUINE_ROBUSTNESS, WEAK_INTERVENTION, DESIGN_FLAW = 0, 1, 2
LABELS = {0: "GENUINE_ROBUSTNESS", 1: "WEAK_INTERVENTION", 2: "DESIGN_FLAW"}
DEFAULT_MARGIN = 0.2  # behavioural equivalence margin used by statistics-only baselines

# --- interpretable diagnostic adequacy thresholds (dataset-informed rules of thumb) ---
# A null is only attributable to GENUINE_ROBUSTNESS when the design clears every adequacy check:
#   (1) sample adequacy  : enough samples to have power                      (raw: n)
#   (2) measurement precision : residual noise low enough to resolve effects (raw: variances)
#   (3) intervention substantiveness : a non-trivial intervention was applied (symbolic: strength)
# Each modality only observes a SUBSET of these inputs -> only the fusion sees all three.
N_MIN = 50          # sample-size adequacy (power)
NOISE_MAX = 2.0     # measurement-precision adequacy (residual sd)
STRENGTH_MIN = 0.5  # intervention substantiveness


# ----------------------------------------------------------------------------- Bayesian primitives
def se_of_diff(control_var, treated_var, n):
    """Standard error of the difference in means for two independent arms of size n."""
    return math.sqrt(max(control_var, 1e-9) / n + max(treated_var, 1e-9) / n)


def jzs_bf10(t, n1, n2, r=0.707):
    """
    JZS Bayes factor BF10 (evidence for an effect vs the point null) for a two-sample t-test
    (Rouder et al. 2009, eq. 1). The effect size delta has a Cauchy(0, r) prior, realised as a
    Normal(0, g) scale mixture with g ~ Inverse-Gamma(1/2, r^2/2); we integrate over g.
    BF10 > 1 favours an effect; BF10 < 1 favours the null. Returns BF10 (capped for stability).
    """
    nu = n1 + n2 - 2
    n_eff = (n1 * n2) / (n1 + n2)
    a, b = 0.5, (r ** 2) / 2.0          # Inverse-Gamma(a, b) prior on g
    log_ig_const = a * math.log(b) - math.lgamma(a)

    def integrand(g):
        if g <= 0:
            return 0.0
        denom = 1.0 + n_eff * g
        log_marg = -0.5 * math.log(denom) - ((nu + 1) / 2.0) * math.log(1.0 + (t ** 2) / (denom * nu))
        log_prior = log_ig_const - (a + 1) * math.log(g) - b / g
        return math.exp(log_marg + log_prior)

    null_dens = (1.0 + (t ** 2) / nu) ** (-(nu + 1) / 2)
    try:
        num, _ = quad(integrand, 1e-9, 100, limit=100)
    except Exception:
        return 1.0
    if num <= 0 or not math.isfinite(num) or null_dens <= 0:
        return 1.0
    bf10 = num / null_dens
    if not math.isfinite(bf10) or bf10 <= 0:
        return 1.0
    return min(bf10, 1e6)


def tost_equivalence(diff, se, margin, alpha=0.05):
    """
    Two One-Sided Tests for equivalence within +/- margin. Returns (is_equivalent, ci_halfwidth).
    Equivalence is *confirmed* iff the (1-2*alpha) CI lies entirely inside (-margin, +margin).
    """
    z = stats.norm.ppf(1 - alpha)
    half = z * se
    lo, hi = diff - half, diff + half
    is_equiv = (lo > -margin) and (hi < margin)
    return is_equiv, half


# ----------------------------------------------------------------------------- Bayesian layer
def bayesian_diagnose(row, bf_prior_r=0.707):
    """
    Diagnose from raw observations only (n, observed_diff, variances). Has NO access to structural
    flags, so (a) it can never output DESIGN_FLAW, and (b) it cannot see intervention strength, so a
    real-but-attenuated effect (weak attack) looks like a genuine null. Both are its blind spots.
    """
    n = int(row["n_per_arm"])
    diff = float(row["observed_diff"])
    cv, tv = float(row["control_var"]), float(row["treated_var"])
    se = se_of_diff(cv, tv, n)
    sd_est = math.sqrt(max((cv + tv) / 2.0, 1e-9))   # estimated residual measurement sd
    t = diff / se if se > 0 else 0.0
    bf10 = jzs_bf10(t, n, n, r=bf_prior_r)
    bf01 = 1.0 / bf10
    is_equiv, half = tost_equivalence(diff, se, DEFAULT_MARGIN)

    if (not is_equiv) and bf10 > 3:
        lab = WEAK_INTERVENTION
        conf = min(0.9, 0.5 + 0.1 * math.log10(bf10 + 1))
        reason = f"BF10={bf10:.2f} (>3) and effect outside +/-{DEFAULT_MARGIN}: real effect under-reported -> weak."
    elif n >= N_MIN and sd_est <= NOISE_MAX:
        # adequate sample + precise measurement + no detectable effect -> reads as a genuine null
        # (blind spot: a weak/attenuated intervention with large n also lands here).
        lab = GENUINE_ROBUSTNESS
        conf = min(0.9, 0.5 + 0.1 * math.log10(bf01 + 1))
        reason = (f"n={n}>= {N_MIN}, residual sd={sd_est:.2f}<= {NOISE_MAX}, no detectable effect "
                  f"(BF01={bf01:.2f}) -> reads as genuine null.")
    else:
        lab = WEAK_INTERVENTION
        why = "small sample" if n < N_MIN else "coarse/noisy measurement"
        conf = 0.6
        reason = f"underpowered ({why}: n={n}, residual sd={sd_est:.2f}) -> cannot confirm null -> weak."
    return lab, conf, reason


# ----------------------------------------------------------------------------- Symbolic layer
def symbolic_diagnose(row):
    """
    Diagnose from structural flags only (weighted logical rules). Catches design flaws via
    confirmability (B1) and identifiability (D1); separates robustness vs weak by intervention
    strength -- but is blind to N / noise, so it mislabels small-N and coarse-metric weak cases.
    """
    confound = bool(row["confound_present"])
    eval_aware = bool(row["evaluation_awareness"])
    meas_valid = bool(row["measurement_valid"])
    identifiable = bool(row["identifiable"])
    topology = str(row["hypothesis_topology"])
    margin_set = bool(row["equivalence_margin_set"])
    strength = float(row["intervention_strength"])

    # ---- design-flaw gate (confirmability + identifiability) ----
    flaws = []
    if confound:
        flaws.append("confound present (E2)")
    if eval_aware:
        flaws.append("evaluation-awareness (D1)")
    if not meas_valid:
        flaws.append("invalid measurement")
    if not identifiable:
        flaws.append("non-identifiable (D1)")
    if topology == "point" or not margin_set:
        flaws.append("unconfirmable point-null topology (B1)")
    if flaws:
        conf = min(0.95, 0.6 + 0.12 * len(flaws))
        return DESIGN_FLAW, conf, "Design-flaw gate fired: " + "; ".join(flaws) + "."

    # ---- clean design: robustness vs weak by intervention strength (blind to N/noise) ----
    if strength >= 0.5:
        return GENUINE_ROBUSTNESS, 0.55 + 0.3 * (strength - 0.5), \
            f"Clean, confirmable design; strong intervention (strength={strength:.2f}) -> genuine robustness."
    else:
        return WEAK_INTERVENTION, 0.55 + 0.3 * (0.5 - strength), \
            f"Clean design but weak intervention (strength={strength:.2f}) -> weak intervention."


# ----------------------------------------------------------------------------- Hybrid fusion
def hybrid_diagnose(row, bf_prior_r=0.707):
    """
    Symbolic confirmability/identifiability gate first; then Bayesian evidence+power separates
    robustness vs weak within the admissible structure. Composite confidence fuses both layers.
    Returns (label, confidence, reasoning_chain).
    """
    # 1) symbolic gate for design flaws (the part Bayesian evidence is structurally blind to)
    sym_lab, sym_conf, sym_reason = symbolic_diagnose(row)
    if sym_lab == DESIGN_FLAW:
        return DESIGN_FLAW, sym_conf, "[Symbolic gate] " + sym_reason + " [Hybrid] structure uninterpretable -> DESIGN_FLAW."

    # 2) admissible structure -> fuse Bayesian power (n, noise, effect) with symbolic strength.
    n = int(row["n_per_arm"])
    diff = float(row["observed_diff"])
    cv, tv = float(row["control_var"]), float(row["treated_var"])
    se = se_of_diff(cv, tv, n)
    sd_est = math.sqrt(max((cv + tv) / 2.0, 1e-9))
    t = diff / se if se > 0 else 0.0
    bf10 = jzs_bf10(t, n, n, r=bf_prior_r)
    bf01 = 1.0 / bf10
    margin = float(row.get("equivalence_margin") or DEFAULT_MARGIN)
    is_equiv, half = tost_equivalence(diff, se, margin)
    strength = float(row["intervention_strength"])

    chain = [f"[Symbolic gate] clean, identifiable & confirmable design (no confound/eval-awareness, "
             f"valid measurement, equivalence margin +/-{margin:.2f} set)."]

    # three interpretable adequacy checks; GENUINE_ROBUSTNESS needs ALL of them to hold.
    sample_ok = n >= N_MIN                 # Bayesian/raw input
    measure_ok = sd_est <= NOISE_MAX       # Bayesian/raw input
    strength_ok = strength >= STRENGTH_MIN  # symbolic input
    detectable_effect = (not is_equiv) and (bf10 > 3)

    if detectable_effect:
        lab = WEAK_INTERVENTION
        conf = min(0.9, 0.55 + 0.1 * math.log10(bf10 + 1))
        chain.append(f"[Bayesian] BF10={bf10:.2f} and effect outside +/-{margin:.2f}: a real effect IS "
                     f"present -> the null under-reports it -> WEAK_INTERVENTION.")
    elif sample_ok and measure_ok and strength_ok:
        lab = GENUINE_ROBUSTNESS
        conf = min(0.95, 0.65 + 0.1 * math.log10(bf01 + 1) + 0.1 * (strength - STRENGTH_MIN))
        chain.append(f"[Bayesian] adequate sample (n={n}) and precise measurement (sd={sd_est:.2f}); "
                     f"[Symbolic] substantive intervention (strength={strength:.2f}) still found nothing "
                     f"(BF01={bf01:.2f}) -> GENUINE_ROBUSTNESS.")
    else:
        lab = WEAK_INTERVENTION
        bits = []
        if not sample_ok:
            bits.append(f"[Bayesian] inadequate sample (n={n} < {N_MIN})")
        if not measure_ok:
            bits.append(f"[Bayesian] coarse/noisy measurement (sd={sd_est:.2f} > {NOISE_MAX})")
        if not strength_ok:
            bits.append(f"[Symbolic] weak intervention (strength={strength:.2f} < {STRENGTH_MIN})")
        conf = min(0.9, 0.6 + 0.05 * len(bits))
        chain.append(" ".join(bits) + " -> a real effect could be masked -> WEAK_INTERVENTION.")

    return lab, conf, " ".join(chain)


# ----------------------------------------------------------------------------- Naive baselines
def nhst_naive_diagnose(row):
    """Classical 'fail to reject H0 => robust' baseline. Two-sample t-test at alpha=0.05."""
    n = int(row["n_per_arm"])
    diff = float(row["observed_diff"])
    se = se_of_diff(float(row["control_var"]), float(row["treated_var"]), n)
    t = diff / se if se > 0 else 0.0
    p = 2 * (1 - stats.t.cdf(abs(t), df=2 * n - 2))
    if p >= 0.05:
        return GENUINE_ROBUSTNESS, 1 - p, f"p={p:.3f} >= 0.05: fail to reject H0 -> 'robust'."
    return WEAK_INTERVENTION, min(0.95, 1 - p), f"p={p:.3f} < 0.05: effect detected -> not robust."


def tost_only_diagnose(row):
    """Equivalence-test-only baseline: equivalence confirmed => robust, else weak. No flaw concept."""
    n = int(row["n_per_arm"])
    diff = float(row["observed_diff"])
    se = se_of_diff(float(row["control_var"]), float(row["treated_var"]), n)
    margin = DEFAULT_MARGIN  # statistics-only baseline: fixed margin, no symbolic input
    is_equiv, half = tost_equivalence(diff, se, margin)
    if is_equiv:
        return GENUINE_ROBUSTNESS, 0.7, f"Equivalence confirmed within +/-{margin:.2f} -> robust."
    return WEAK_INTERVENTION, 0.6, f"Equivalence NOT confirmed (CI half-width {half:.2f}) -> weak."


METHODS = {
    "NHST_naive": nhst_naive_diagnose,
    "TOST_only": tost_only_diagnose,
    "Bayesian_only": bayesian_diagnose,
    "Symbolic_only": symbolic_diagnose,
    "Hybrid": hybrid_diagnose,
}
