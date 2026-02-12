# Climate Benford Analysis — CLAUDE.md

## Project Overview

This project applies the **Benford's Law analytical framework** developed in the Benford_Fun research program to **climate and environmental datasets**. The goal is to use Benford conformance as a "flashlight" — a filtering tool that narrows infinite theoretical possibilities down to the ones nature actually uses.

The core idea: Benford's distribution is evident in every natural dataset we've tested. When competing climate models produce outputs, the ones that conform to Benford's Law are more likely to reflect real physical processes. Those that deviate may have structural flaws, reporting biases, or measurement artifacts worth investigating.

**Parent project:** `~/Desktop/Benford_Fun/` — contains the core analysis engine, papers, and the complete monotonicity framework.

**Website:** https://benfordslawasalensforquantum.netlify.app

---

## Architecture

```
Climate_Benford/
├── CLAUDE.md               ← You are here (agent instructions)
├── data/
│   ├── test_queue.json     ← Master list of all climate tests
│   └── sources/            ← Cached raw data per dataset
├── results/
│   ├── summary.json        ← Aggregated results
│   └── individual/         ← Per-test detailed JSON results
├── scripts/
│   ├── benford_core.py     ← Core analysis engine (copy from Benford_Fun)
│   ├── climate_fetchers.py ← Dataset acquisition functions
│   └── run_test.py         ← Single-test runner
└── website/                ← Dashboard (future)
```

---

## Priority Datasets (Ranked by Benford Suitability)

### Tier A — Strong Candidates (3+ orders of magnitude, large N)

| # | Dataset | Orders of Mag | Data Points | Source |
|---|---------|:------------:|:-----------:|--------|
| 1 | **U.S. Wildfire Acreage** (individual fire sizes) | 5-6 | 100,000s | NIFC |
| 2 | **Storm Event Property Damage** | 7-8 | 1,000,000s | NOAA NCEI |
| 3 | **River Discharge / Streamflow** | 6-7 | Billions | USGS NWIS |
| 4 | **Tropical Cyclone Track Distances** | 4 | 300,000+ | NOAA IBTrACS |
| 5 | **Facility-Level GHG Emissions** | 3-4 | 100,000+ | EPA GHGRP |
| 6 | **Daily Precipitation** (global, excl. zeros) | 3-4 | Billions | NOAA GHCNd |
| 7 | **CO2 Emissions by Country** | 6 | 10,000+ | Our World in Data |
| 8 | **Earthquake Energy Release** | 15 | Millions | USGS |

### Tier C — Negative Controls (should deviate — narrow range)

| # | Dataset | Why it deviates |
|---|---------|----------------|
| 9 | Ice Core CO2 (800kyr) | Range: 170-420 ppm (<1 order) |
| 10 | Mauna Loa CO2 monthly | Range: 313-427 ppm (<1 order) |
| 11 | Surface Temperature anomalies | Range: -2 to +2 C (<1 order) |
| 12 | Sea Ice Extent | Range: 3.5-16.5 M km² (<1 order) |

---

## Analysis Protocol

Use the same protocol as Benford_Fun. For each dataset:

### Step 1: Data Collection
- Fetch from public source (API, CSV download, web scrape)
- Extract positive real numbers only (strip units, discard zeros/negatives)
- Cache raw data to `data/sources/<test_id>.json`
- Require >= 50 data points; flag < 100 as `low_confidence`

### Step 2: First-Digit Extraction
```python
import math
def first_digit(x):
    if x <= 0:
        return None
    return int(str(f"{x:.15e}")[0])
```
Also extract first two digits if n > 500.

### Step 3: Statistical Tests

Run ALL of:
- **Chi-Squared Test** — observed vs Benford expected, df=8, report p-value
- **MAD** — Mean Absolute Deviation (Nigrini thresholds: <0.006 close, <0.012 acceptable, <0.015 marginal, >=0.015 nonconformity)
- **Kolmogorov-Smirnov** — D-statistic and p-value
- **delta_B (Euclidean deviation)** — primary metric: sqrt(sum((P_obs - P_benford)^2))
- **Per-digit deviation epsilon(d)** — signed, all 9 digits

### Step 4: Classification

| Verdict | Criteria |
|---------|----------|
| **CONFORMS** | p_chi2 > 0.05 AND MAD < 0.012 AND delta_B < 0.03 |
| **MARGINAL** | p_chi2 > 0.01 OR MAD 0.012-0.015 OR delta_B 0.03-0.06 |
| **DEVIATES** | p_chi2 < 0.01 AND MAD > 0.015 AND delta_B > 0.06 |
| **INTERESTING** | Deviates in a scientifically notable pattern |

### Step 5: Write Results
Save to `results/individual/<test_id>.json` and update `results/summary.json`.

---

## Agent Orchestration

Agents should work through `data/test_queue.json`:
1. Claim next `"queued"` test (set to `"in_progress"`)
2. Fetch dataset
3. Run full analysis pipeline
4. Write results
5. Move to next test

Use `fcntl.flock()` for file locking on shared JSON files.

---

## Key Questions We're Asking

1. **Do real climate observations conform to Benford's Law?** (Expected: yes for Tier A datasets)
2. **Which climate models produce Benford-conforming outputs?** (Future work: compare CMIP6 models)
3. **Can Benford deviation detect data quality issues?** (e.g., fabricated emissions reports)
4. **Do the deviation patterns tell us anything about the underlying physics?** (Like they did for quantum statistics)

---

## Dependencies

```bash
pip install numpy scipy pandas matplotlib requests beautifulsoup4 plotly
```

---

## Important Notes

- This is a NEW project. Start fresh with climate data.
- Reuse the analytical framework from Benford_Fun but don't mix results.
- The negative controls (Tier C) are just as important as the conforming datasets — they validate that the method correctly identifies when Benford's Law shouldn't apply.
- For datasets that DEVIATE, explain WHY: narrow range, selection bias, human rounding, etc.
- Be conservative in claims. We're investigating, not asserting.
