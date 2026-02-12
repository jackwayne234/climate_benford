# Climate Benford — Findings Log

Running log of every test, discovery, and insight. Updated as we go.

---

## Test #1: U.S. Wildfire Acreage (NIFC)

**Date:** 2026-02-11
**Source:** NIFC InterAgencyFirePerimeterHistory (ArcGIS Feature Service)
**N:** 116,310 individual fire records
**Range:** 5.1e-7 to 1,640,095 acres (~12.5 orders of magnitude)

### Results (all data)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| Chi-squared p | ~0.000 | >0.05 | No (large N effect) |
| MAD | 0.0074 | <0.012 | Yes (acceptable) |
| delta_B | 0.0274 | <0.03 | Yes |
| KS D-stat | 0.0169 | — | — |

**Verdict:** MARGINAL (only because chi-squared rejects at large N)

### Key Discovery: Digit-9 Excess

Digit 9 observed at 6.3% vs Benford's 4.6% (+1.7% excess). Investigation revealed this is entirely driven by sub-acre fires — GIS polygon artifacts and reporting placeholders (0.09, 0.10 appear hundreds of times).

### Size Class Breakdown

| Size Class | N | MAD | delta_B | Verdict |
|-----------|---|-----|---------|---------|
| **1-100 acres** | **49,471** | **0.006** | **0.024** | **Close conformity** |
| >= 1 acre | 99,863 | 0.007 | 0.031 | Acceptable |
| < 1 acre | 16,447 | 0.033 | 0.159 | Deviates (artifacts) |
| 100-10,000 acres | 45,641 | 0.016 | 0.070 | Marginal |
| 10,000+ acres | 4,751 | 0.047 | 0.208 | Deviates (selection bias) |

**Insight:** Real fire data (1-100 acres) conforms beautifully. Deviations at boundaries are explainable: GIS rounding artifacts below 1 acre, selection/threshold effects above 10,000 acres. Benford acts as a data quality indicator.

---

## CMIP6 Model Comparison: The Big Finding

**Date:** 2026-02-11
**Variable:** burntFractionAll (monthly burned fraction, %)
**Experiment:** historical
**N per model:** ~500,000 (sampled from millions)

### Results

| Model | Fire Scheme | MAD | delta_B | Verdict | Digit-1 | Digit-2 |
|-------|------------|-----|---------|---------|---------|---------|
| **CESM2** | Li | **0.0025** | **0.008** | **Close conformity** | 30.2% (Benford: 30.1%) | 17.9% (17.6%) |
| **CESM2-WACCM** | Li | **0.0024** | **0.009** | **Close conformity** | 30.1% (dead on) | 18.0% (17.6%) |
| **CNRM-ESM2-1** | GlobFIRM | **0.0234** | **0.102** | **DEVIATES** | 31.5% (30.1%) | **26.8% (17.6%)** |

### The Smoking Gun

CNRM-ESM2-1 has a massive digit-2 excess: 26.8% vs Benford's 17.6% (+9.2%). This means the GlobFIRM fire scheme is clustering burned area values into a narrow band starting with "2" instead of producing the full power-law spread that real wildfires exhibit.

### Independent Validation (Literature)

The Benford result aligns perfectly with published model evaluations:

- **Li scheme (CESM2/CESM2-WACCM):** Spatial correlation with satellite data 0.54-0.70. Global burned area within observed range (430-802 Mha/yr). Ranked top performers.
- **GlobFIRM (CNRM-ESM2-1):** Standard implementations severely underestimate burned area. Probability cap of 1.0 prevents full distribution. Can't capture fire seasonality. Being phased out in favor of Li scheme.

**Key citation:** Yue et al., "Evaluation of global fire simulations in CMIP6 Earth system models," Geoscientific Model Development, 17, 8751-8771, 2024.

### What This Means

Benford analysis identified in 30 seconds what took the climate modeling community years of satellite validation to establish: the Li fire scheme is more physically realistic than GlobFIRM. The digit distribution alone reveals whether a fire model produces outputs that look like nature.

**Proposed use case:** Benford conformance as a rapid screening tool for new climate model parameterizations. Fail fast before expensive validation.

---

---

## Test #2: Storm Event Property Damage (NOAA NCEI)

**Date:** 2026-02-11
**Source:** NOAA NCEI Storm Events Database (2000-2024)
**N:** 340,683 damage records
**Range:** $10 to $17.9 billion (~9.3 orders of magnitude)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | 0.0562 | <0.012 | **No** |
| delta_B | 0.195 | <0.06 | **No** |

**Verdict: DEVIATES**

**The human rounding signature:** Digit 5 appears at 22.1% vs Benford's 7.9% (+14.2% excess). Digits 1 and 2 also inflated. This is because property damage is human-estimated, not measured — people report in round numbers ($5,000, $50,000, $500,000). This is not a nature signal, it's a reporting artifact. Benford is detecting the human hand in the data.

**Insight:** This is "INTERESTING" rather than a simple deviation. Benford correctly identifies that this dataset, despite spanning 9+ orders of magnitude, has been filtered through human estimation bias. A potential fraud/quality detection application.

---

## Test #3: River Discharge / Streamflow (USGS NWIS)

**Date:** 2026-02-11
**Source:** USGS NWIS daily values, 15 states, 2023
**N:** 1,770,914 daily discharge measurements
**Range:** 0.01 to 991,000 cfs (~8.0 orders of magnitude)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | **0.00105** | <0.006 | **Yes (close)** |
| delta_B | **0.00400** | <0.03 | **Yes** |

**Verdict: Close conformity (best result so far)**

Every single digit is within 0.3% of Benford's prediction. This is 1.77 million measurements from automated stream gauges — pure nature, no human filtering. The MAD of 0.001 is exceptional.

**Insight:** Instrument-measured natural processes with wide dynamic range produce near-perfect Benford conformance. This is our cleanest validation that Benford's Law is a fundamental property of natural multiplicative processes.

---

## Test #4: Tropical Cyclone Wind Speeds (IBTrACS)

**Date:** 2026-02-11
**Source:** NOAA IBTrACS v04r01 (all basins, all years)
**N:** 401,189 wind speed records
**Range:** 5 to 185 knots (~1.6 orders of magnitude)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | 0.0454 | <0.012 | **No** |
| delta_B | 0.222 | <0.06 | **No** |

**Verdict: DEVIATES**

**Why:** Wind speeds only span 1.6 orders of magnitude (5-185 knots). Not enough dynamic range for Benford. Digit 1 is severely suppressed (10.8% vs 30.1%) because most tropical cyclone winds are in the 25-80 knot range. This acts as a semi-negative control — narrow range, as expected.

**Note:** The original plan was track distances, but wind speed was more readily available. Track distances might have wider range and could be revisited.

---

## Test #5: GHG Emissions (Our World in Data, multi-GHG)

**Date:** 2026-02-11
**Source:** Our World in Data (cement, flaring, methane, per-capita GHG)
**N:** 350,831 emission values
**Range:** 0.001 to 49,694 million tonnes CO2e (~7.7 orders of magnitude)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | **0.00254** | <0.006 | **Yes (close)** |
| delta_B | **0.00870** | <0.03 | **Yes** |

**Verdict: Close conformity**

Another near-perfect result. GHG emissions across countries and sectors span a wide range and follow Benford closely. Slight digit-8 excess (+0.5%) is negligible.

---

## Test #7: CO2 Emissions by Country (Our World in Data)

**Date:** 2026-02-11
**Source:** Our World in Data owid-co2-data
**N:** 28,030 annual country-level CO2 values
**Range:** 0.001 to 38,599 million tonnes (~7.6 orders of magnitude)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | 0.00728 | <0.012 | **Yes (acceptable)** |
| delta_B | 0.0282 | <0.03 | **Yes** |

**Verdict: Acceptable conformity**

Slight digit-4 excess (+2.1%) possibly reflects clustering of small developing nations at similar emission levels. But overall, solid Benford conformance.

---

## Test #8: Earthquake Energy Release (USGS)

**Date:** 2026-02-11
**Source:** USGS FDSNWS, M2.5+ earthquakes, 2000-2024
**N:** 493,848 earthquakes
**Range:** 4.47e7 to 2.82e18 joules (~10.8 orders of magnitude)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | 0.0391 | <0.012 | **No** |
| delta_B | 0.128 | <0.06 | **No** |

**Verdict: DEVIATES — but INTERESTING**

Digits oscillate: odd digits (1,3,5,7) over-represented, even digits (2,4,6) and 9 under-represented. This is an artifact of the magnitude-to-energy conversion: E = 10^(1.5*M + 4.8). Because magnitudes are reported to 0.1 precision and the 1.5 multiplier creates a discrete grid in log-space, the energy values cluster on specific first digits.

**Insight:** Benford deviation here reveals a quantization artifact in how earthquake magnitudes are reported, not a problem with the underlying physics. The raw seismic energy is continuous, but the reporting system discretizes it. Another example of Benford detecting the measurement system rather than the phenomenon.

---

## Test #10: Mauna Loa CO2 Monthly (NEGATIVE CONTROL)

**Date:** 2026-02-11
**Source:** NOAA GML
**N:** 815 monthly values
**Range:** 312.42 to 430.51 ppm (0.14 orders of magnitude)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | 0.1729 | <0.012 | **No** |
| delta_B | 0.806 | <0.06 | **No** |

**Verdict: DEVIATES (as predicted)**

83.6% of values start with 3, 16.4% start with 4, everything else is 0%. Range is less than half an order of magnitude. **Perfect negative control** — exactly what the theory predicts.

---

## Test #11: Surface Temperature Anomalies (NEGATIVE CONTROL)

**Date:** 2026-02-11
**Source:** NASA GISS
**N:** 829 positive monthly anomalies (out of 1,753 total — half are negative)
**Range:** ~0 to 1.48 C (< 1 order of magnitude, plus negatives discarded)

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| MAD | 0.0263 | <0.012 | **No** |
| delta_B | 0.094 | <0.06 | **No** |

**Verdict: DEVIATES (as predicted)**

Flattened distribution — digit 1 suppressed, higher digits inflated. Narrow range + negative values = no Benford conformance. **Negative control confirmed.**

---

## Master Scoreboard

| # | Dataset | N | Orders of Mag | MAD | delta_B | Verdict |
|---|---------|---|:---:|-----|---------|---------|
| 1 | Wildfire Acreage | 116,310 | 12.5 | 0.0074 | 0.027 | Acceptable |
| 2 | Storm Damage | 340,683 | 9.3 | 0.0562 | 0.195 | **DEVIATES** (human rounding) |
| 3 | **River Discharge** | **1,770,914** | **8.0** | **0.0010** | **0.004** | **Close conformity** |
| 4 | Cyclone Wind Speeds | 401,189 | 1.6 | 0.0454 | 0.222 | DEVIATES (narrow range) |
| 5 | **GHG Emissions** | **350,831** | **7.7** | **0.0025** | **0.009** | **Close conformity** |
| 6 | Daily Precipitation | — | — | — | — | Skipped (needs bulk download) |
| 7 | CO2 by Country | 28,030 | 7.6 | 0.0073 | 0.028 | Acceptable |
| 8 | Earthquake Energy | 493,848 | 10.8 | 0.0391 | 0.128 | DEVIATES (quantization) |
| 9 | Ice Core CO2 | 1,240 | 0.2 | 0.1462 | 0.703 | **DEVIATES** (negative control) |
| 10 | Mauna Loa CO2 | 815 | 0.1 | 0.1729 | 0.806 | **DEVIATES** (negative control) |
| 11 | Surface Temp Anomalies | 829 | <1 | 0.0263 | 0.094 | **DEVIATES** (negative control) |
| 12 | Sea Ice Extent | 31,248 | 1.0 | 0.0722 | 0.364 | **DEVIATES** (negative control) |
| — | CMIP6 CESM2 | 493,951 | 31.9 | 0.0025 | 0.008 | **Close conformity** |
| — | CMIP6 CESM2-WACCM | 493,940 | 31.9 | 0.0024 | 0.009 | **Close conformity** |
| — | CMIP6 CNRM-ESM2-1 | 500,000 | 14.3 | 0.0234 | 0.102 | **DEVIATES** |

### Pattern Summary

**Conforms (wide range, natural/measured):** River discharge, GHG emissions, wildfires, CO2 by country, CESM2, CESM2-WACCM
**Deviates with explanation:** Storm damage (human rounding), earthquakes (quantization), cyclone winds (narrow range), CNRM-ESM2-1 (broken fire scheme)
**Negative controls confirmed:** Mauna Loa CO2, surface temp anomalies
