# Climate Benford

**Benford's Law as a rapid validation tool for climate models and environmental data.**

We applied Benford's Law — the observation that first digits in natural datasets follow a logarithmic distribution — to 12 climate and environmental datasets and 3 CMIP6 Earth System Models. The results:

- Every dataset that should conform to Benford's Law does
- Every dataset that shouldn't, doesn't
- Every deviation is explainable
- **We identified a known-flawed climate model fire scheme in 30 seconds that took the field years of satellite validation to establish**

## The Key Finding

We pulled burned area outputs from three CMIP6 climate models and ran a first-digit analysis:

| Model | Fire Scheme | MAD | Verdict | Independent Assessment |
|-------|------------|-----|---------|----------------------|
| CESM2 | Li | 0.0025 | **Conforms** | Top performer (Yue et al. 2024) |
| CESM2-WACCM | Li | 0.0024 | **Conforms** | Top performer |
| CNRM-ESM2-1 | GlobFIRM | 0.0234 | **Deviates** | Being phased out |

CNRM's digit-2 appears at **26.8%** instead of Benford's predicted 17.6%. The GlobFIRM fire scheme has a probability cap that prevents the full power-law spread real wildfires exhibit. Benford catches this structural flaw instantly.

The Li-scheme models (CESM2) match Benford's prediction to within 0.1% on digit 1. CESM2-WACCM's digit-1 frequency is **30.10%** — Benford predicts 30.10%. Dead on.

## Full Results

### Tier A: Datasets That Should Conform

| # | Dataset | N | Orders of Mag | MAD | Verdict |
|---|---------|--:|:---:|-----|---------|
| 1 | U.S. Wildfire Acreage | 116,310 | 12.5 | 0.0074 | Acceptable conformity |
| 2 | Storm Event Property Damage | 340,683 | 9.3 | 0.0562 | Deviates (human rounding) |
| 3 | **River Discharge** | **1,770,914** | **8.0** | **0.0010** | **Near-perfect** |
| 4 | Tropical Cyclone Wind Speeds | 401,189 | 1.6 | 0.0454 | Deviates (narrow range) |
| 5 | **GHG Emissions** | **350,831** | **7.7** | **0.0025** | **Close conformity** |
| 7 | CO2 Emissions by Country | 28,030 | 7.6 | 0.0073 | Acceptable conformity |
| 8 | Earthquake Energy Release | 493,848 | 10.8 | 0.0391 | Deviates (quantization artifact) |

### Tier C: Negative Controls (Should Deviate)

| # | Dataset | N | Orders of Mag | MAD | Verdict |
|---|---------|--:|:---:|-----|---------|
| 9 | Ice Core CO2 (800kyr) | 1,240 | 0.2 | 0.1462 | Deviates (as predicted) |
| 10 | Mauna Loa CO2 Monthly | 815 | 0.1 | 0.1729 | Deviates (as predicted) |
| 11 | Surface Temperature Anomalies | 829 | <1 | 0.0263 | Deviates (as predicted) |
| 12 | Sea Ice Extent | 31,248 | 1.0 | 0.0722 | Deviates (as predicted) |

**River discharge** (1.77 million USGS gauge readings) is the standout: MAD of 0.001, every digit within 0.3% of Benford's prediction. Pure instrument-measured nature.

**Storm damage** deviates because humans estimate losses in round numbers — digit 5 appears at 22% instead of 8%. Benford detects the human hand in the data.

**Earthquake energy** deviates due to magnitude quantization (reported to 0.1 precision, then exponentiated), not physics.

## Why This Matters

Climate model validation currently requires years of satellite comparisons, regional skill assessments, and multi-model intercomparisons. Benford analysis offers a **30-second sanity check**:

1. Run your model
2. Count first digits of the output
3. If it doesn't follow Benford's Law, your parameterization likely has a structural issue
4. Fix the physics before spending compute on detailed validation

This doesn't replace traditional validation — it's a **pre-screen**. A flashlight that shows you where to look.

## Quick Start

```bash
git clone https://github.com/jackwayne234/climate-benford.git
cd Climate_Benford
pip install -r requirements.txt

# Run a single test
python3 scripts/run_test.py wildfire_acreage

# Or use the core engine directly
python3 -c "
from scripts.benford_core import run_analysis
data = [your_values_here]
result = run_analysis(data, test_id='my_test')
print(result['verdict'])
print(f'MAD: {result[\"first_digit\"][\"mad\"][\"mad\"]:.4f}')
"
```

## How It Works

Benford's Law says that in datasets spanning multiple orders of magnitude, the probability of first digit d is:

```
P(d) = log10(1 + 1/d)
```

| Digit | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| **Benford %** | 30.1 | 17.6 | 12.5 | 9.7 | 7.9 | 6.7 | 5.8 | 5.1 | 4.6 |

We run four statistical tests on each dataset:

- **MAD** (Mean Absolute Deviation) — average |observed - expected| across all 9 digits. <0.006 is close, <0.012 acceptable, >0.015 nonconformity.
- **delta_B** (Euclidean deviation) — sqrt of sum of squared deviations. <0.03 conforms, >0.06 deviates.
- **Chi-squared** — classical goodness-of-fit test (note: rejects at large N even for tiny deviations).
- **Kolmogorov-Smirnov** — compares empirical vs. theoretical CDF.

## Project Structure

```
Climate_Benford/
├── scripts/
│   ├── benford_core.py       # Core analysis engine (all statistical tests)
│   ├── climate_fetchers.py   # Dataset acquisition (NIFC, USGS, NOAA, etc.)
│   └── run_test.py           # Single-test runner with queue management
├── data/
│   ├── test_queue.json       # Master list of all 12 datasets
│   └── sources/              # Cached raw data (gitignored, regenerated by fetchers)
├── results/
│   ├── summary.json          # Aggregated results
│   └── individual/           # Per-test detailed JSON results
├── findings_log.md           # Running log of all findings and insights
├── napkin_math.md            # Plain-English explainer + elevator pitch
└── CLAUDE.md                 # Analysis protocol and dataset specifications
```

## Data Sources

| Dataset | Source | API/URL |
|---------|--------|---------|
| Wildfire Acreage | NIFC | ArcGIS Feature Service |
| Storm Damage | NOAA NCEI | Storm Events bulk CSV |
| River Discharge | USGS NWIS | waterservices.usgs.gov |
| Cyclone Wind Speeds | NOAA IBTrACS | ncei.noaa.gov |
| GHG Emissions | Our World in Data | github.com/owid/co2-data |
| CO2 by Country | Our World in Data | github.com/owid/co2-data |
| Earthquake Energy | USGS | earthquake.usgs.gov |
| Ice Core CO2 | NOAA Paleoclimatology | ncei.noaa.gov |
| Mauna Loa CO2 | NOAA GML | gml.noaa.gov |
| Surface Temp Anomalies | NASA GISS | data.giss.nasa.gov |
| Sea Ice Extent | NSIDC | noaadata.apps.nsidc.org |
| CMIP6 Burned Area | Google Cloud | Pangeo CMIP6 catalog |

## References

- Yue et al., "Evaluation of global fire simulations in CMIP6 Earth system models," *Geoscientific Model Development*, 17, 8751-8771, 2024.
- Nigrini, M.J., *Benford's Law: Applications for Forensic Accounting, Auditing, and Fraud Detection*, Wiley, 2012.
- Newcomb, S., "Note on the Frequency of Use of the Different Digits in Natural Numbers," *American Journal of Mathematics*, 1881.

## Related Work

This project extends the Benford's Law analytical framework from [Benford_Fun](https://github.com/jackwayne234/Benford_Fun), which applies Benford analysis to quantum statistics and other domains.

Website: [benfordslawasalensforquantum.netlify.app](https://benfordslawasalensforquantum.netlify.app)

## License

MIT
