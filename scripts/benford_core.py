"""
Benford's Law Core Analysis Engine for Climate Data.

Implements the full analysis pipeline from CLAUDE.md:
- First-digit and first-two-digit extraction
- Chi-squared, MAD, KS, delta_B, per-digit epsilon tests
- Classification: CONFORMS / MARGINAL / DEVIATES / INTERESTING
"""

import math
import numpy as np
from scipy import stats
from collections import Counter


# Benford's Law expected probabilities for first digit (1-9)
BENFORD_FIRST = {d: math.log10(1 + 1/d) for d in range(1, 10)}

# Benford's Law expected probabilities for first two digits (10-99)
BENFORD_FIRST_TWO = {d: math.log10(1 + 1/d) for d in range(10, 100)}

# Nigrini MAD thresholds
MAD_THRESHOLDS = {
    "close": 0.006,
    "acceptable": 0.012,
    "marginal": 0.015,
}


def first_digit(x):
    """Extract the first significant digit of a positive number."""
    if x <= 0:
        return None
    return int(str(f"{x:.15e}")[0])


def first_two_digits(x):
    """Extract the first two significant digits of a positive number."""
    if x <= 0:
        return None
    s = f"{x:.15e}"
    # First char is the leading digit, skip the decimal point, second significant digit follows
    d1 = s[0]
    d2 = s[2]  # character after the decimal point
    return int(d1 + d2)


def extract_positive(data):
    """Filter to positive real numbers only."""
    return [x for x in data if isinstance(x, (int, float)) and x > 0 and math.isfinite(x)]


def digit_counts(data, digit_func, digit_range):
    """Count occurrences of each digit/digit-pair in the data."""
    digits = [digit_func(x) for x in data]
    digits = [d for d in digits if d is not None]
    counts = Counter(digits)
    return {d: counts.get(d, 0) for d in digit_range}, len(digits)


def chi_squared_test(observed_counts, expected_probs, n):
    """Chi-squared goodness-of-fit test against Benford distribution."""
    digits = sorted(observed_counts.keys())
    observed = np.array([observed_counts[d] for d in digits])
    expected = np.array([expected_probs[d] * n for d in digits])

    # Avoid division by zero
    mask = expected > 0
    chi2 = np.sum((observed[mask] - expected[mask])**2 / expected[mask])
    df = np.sum(mask) - 1
    p_value = 1 - stats.chi2.cdf(chi2, df)

    return {"chi2_statistic": float(chi2), "df": int(df), "p_value": float(p_value)}


def mean_absolute_deviation(observed_counts, expected_probs, n):
    """Calculate MAD (Nigrini's Mean Absolute Deviation)."""
    digits = sorted(observed_counts.keys())
    observed_props = {d: observed_counts[d] / n for d in digits}
    deviations = [abs(observed_props[d] - expected_probs[d]) for d in digits]
    mad = np.mean(deviations)

    if mad < MAD_THRESHOLDS["close"]:
        label = "close"
    elif mad < MAD_THRESHOLDS["acceptable"]:
        label = "acceptable"
    elif mad < MAD_THRESHOLDS["marginal"]:
        label = "marginal"
    else:
        label = "nonconformity"

    return {"mad": float(mad), "label": label}


def ks_test(data, digit_func, expected_probs, digit_range):
    """Kolmogorov-Smirnov test comparing empirical CDF to Benford CDF."""
    digits = [digit_func(x) for x in data]
    digits = [d for d in digits if d is not None]
    n = len(digits)
    if n == 0:
        return {"d_statistic": None, "p_value": None}

    sorted_range = sorted(digit_range)

    # Build empirical CDF
    counts = Counter(digits)
    empirical_cdf = []
    cumsum = 0
    for d in sorted_range:
        cumsum += counts.get(d, 0) / n
        empirical_cdf.append(cumsum)

    # Build Benford CDF
    benford_cdf = []
    cumsum = 0
    for d in sorted_range:
        cumsum += expected_probs[d]
        benford_cdf.append(cumsum)

    empirical_cdf = np.array(empirical_cdf)
    benford_cdf = np.array(benford_cdf)

    d_stat = float(np.max(np.abs(empirical_cdf - benford_cdf)))

    # Approximate p-value using Kolmogorov distribution
    # For discrete distributions this is conservative
    sqrt_n = math.sqrt(n)
    lambda_val = (sqrt_n + 0.12 + 0.11 / sqrt_n) * d_stat
    # Kolmogorov survival function approximation
    if lambda_val < 0.001:
        p_value = 1.0
    else:
        p_value = float(stats.kstwobign.sf(lambda_val))

    return {"d_statistic": d_stat, "p_value": p_value}


def delta_b(observed_counts, expected_probs, n):
    """Euclidean deviation (delta_B) — primary metric."""
    digits = sorted(observed_counts.keys())
    observed_props = np.array([observed_counts[d] / n for d in digits])
    expected = np.array([expected_probs[d] for d in digits])
    return float(np.sqrt(np.sum((observed_props - expected)**2)))


def per_digit_epsilon(observed_counts, expected_probs, n):
    """Signed per-digit deviation epsilon(d) for all digits."""
    digits = sorted(observed_counts.keys())
    result = {}
    for d in digits:
        obs_prop = observed_counts[d] / n
        exp_prop = expected_probs[d]
        result[d] = float(obs_prop - exp_prop)
    return result


def classify(chi2_result, mad_result, db):
    """Classify the result per CLAUDE.md criteria."""
    p = chi2_result["p_value"]
    mad = mad_result["mad"]

    if p > 0.05 and mad < 0.012 and db < 0.03:
        return "CONFORMS"
    elif p < 0.01 and mad > 0.015 and db > 0.06:
        return "DEVIATES"
    elif p > 0.01 or 0.012 <= mad <= 0.015 or 0.03 <= db <= 0.06:
        return "MARGINAL"
    else:
        return "MARGINAL"  # Edge cases default to MARGINAL


def run_analysis(data, test_id="unknown", metadata=None):
    """
    Run the complete Benford analysis pipeline on a dataset.

    Args:
        data: list of raw numbers
        test_id: identifier for this test
        metadata: optional dict of extra info about the dataset

    Returns:
        dict with complete analysis results
    """
    # Step 1: Extract positive values
    positive = extract_positive(data)
    n = len(positive)

    if n < 50:
        return {
            "test_id": test_id,
            "error": f"Insufficient data: {n} positive values (need >= 50)",
            "n_raw": len(data),
            "n_positive": n,
        }

    low_confidence = n < 100

    # Step 2: First-digit analysis
    fd_counts, fd_n = digit_counts(positive, first_digit, range(1, 10))

    # Step 3: Statistical tests (first digit)
    chi2 = chi_squared_test(fd_counts, BENFORD_FIRST, fd_n)
    mad = mean_absolute_deviation(fd_counts, BENFORD_FIRST, fd_n)
    ks = ks_test(positive, first_digit, BENFORD_FIRST, range(1, 10))
    db = delta_b(fd_counts, BENFORD_FIRST, fd_n)
    epsilon = per_digit_epsilon(fd_counts, BENFORD_FIRST, fd_n)

    # Step 4: Classification
    verdict = classify(chi2, mad, db)

    # Observed proportions for reporting
    observed_props = {d: fd_counts[d] / fd_n for d in range(1, 10)}
    expected_props = {d: float(BENFORD_FIRST[d]) for d in range(1, 10)}

    result = {
        "test_id": test_id,
        "n_raw": len(data),
        "n_positive": n,
        "low_confidence": low_confidence,
        "first_digit": {
            "observed_counts": fd_counts,
            "observed_proportions": observed_props,
            "expected_proportions": expected_props,
            "chi_squared": chi2,
            "mad": mad,
            "ks_test": ks,
            "delta_b": db,
            "per_digit_epsilon": epsilon,
        },
        "verdict": verdict,
    }

    # First-two-digit analysis if n > 500
    if n > 500:
        ftd_counts, ftd_n = digit_counts(positive, first_two_digits, range(10, 100))
        ftd_chi2 = chi_squared_test(ftd_counts, BENFORD_FIRST_TWO, ftd_n)
        ftd_mad = mean_absolute_deviation(ftd_counts, BENFORD_FIRST_TWO, ftd_n)
        ftd_db = delta_b(ftd_counts, BENFORD_FIRST_TWO, ftd_n)

        result["first_two_digits"] = {
            "observed_counts": {str(k): v for k, v in ftd_counts.items()},
            "chi_squared": ftd_chi2,
            "mad": ftd_mad,
            "delta_b": ftd_db,
        }

    if metadata:
        result["metadata"] = metadata

    return result
