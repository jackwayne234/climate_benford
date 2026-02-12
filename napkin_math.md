# Benford's Law — The Napkin Math

Everything you need to explain this in an elevator, at a whiteboard, or on the back of a napkin.

---

## The One-Liner

"In any natural dataset that spans multiple orders of magnitude, about 30% of numbers start with 1, 18% start with 2, 12% start with 3... and only 4.6% start with 9. If a dataset doesn't follow this pattern, something's off."

---

## The Law (memorize these)

```
Digit    Benford %     Easy memory
  1       30.1%        "About a third"
  2       17.6%        "About a sixth"
  3       12.5%        "About an eighth"
  4        9.7%        "About a tenth"
  5        7.9%           |
  6        6.7%           | These five
  7        5.8%           | are all
  8        5.1%           | 5-10%
  9        4.6%           |
```

The formula (for a napkin):

```
P(d) = log10(1 + 1/d)
```

That's it. One formula. P(1) = log10(2) = 0.301. P(9) = log10(10/9) = 0.046.

---

## Why It Works (the intuition)

Think about a stock price going from $100 to $200. It has to pass through $100-$199 — all starting with "1." But going from $200 to $300 means passing through $200-$299 — same count of numbers, but you got there faster (percentage-wise). Going from $100 to $200 is a 100% gain. Going from $900 to $1000 is only an 11% gain, then you're back to digit 1 again.

**Anything that grows or shrinks multiplicatively (percentages, not fixed amounts) will follow Benford's Law.** Fire sizes, river flows, earthquake energies, emissions — all multiplicative processes.

Narrow-range data (temperature anomalies between -2 and +2) won't follow it. No room for the logarithmic spread.

---

## The Three Numbers You Need

When someone asks "does this dataset follow Benford's Law?", you run three tests:

### 1. MAD (Mean Absolute Deviation)

```
MAD = average of |observed% - benford%| for each digit
```

On a napkin: take each digit's percentage, subtract what Benford predicts, take the absolute value, average all 9.

| MAD | Meaning |
|-----|---------|
| < 0.006 | Close conformity |
| < 0.012 | Acceptable conformity |
| < 0.015 | Marginal |
| > 0.015 | Nonconformity |

**Our wildfire data: MAD = 0.006. Close conformity.**
**CESM2 fire model: MAD = 0.0025. Extremely close.**
**CNRM fire model: MAD = 0.023. Nonconformity.**

### 2. delta_B (Euclidean Deviation)

```
delta_B = sqrt( sum of (observed% - benford%)^2 )
```

Same idea as MAD but uses squares so big deviations get amplified. Like the Pythagorean theorem applied to deviation.

| delta_B | Meaning |
|---------|---------|
| < 0.03 | Conforms |
| 0.03-0.06 | Marginal |
| > 0.06 | Deviates |

**CESM2: delta_B = 0.008. Tight.**
**CNRM: delta_B = 0.102. Way off.**

### 3. Chi-Squared p-value

The classic statistical test. "What's the probability we'd see these digit counts if the data truly followed Benford?"

- p > 0.05: Can't reject Benford (good)
- p < 0.05: Statistically significant deviation

**Caveat you need to know:** With huge datasets (100K+ points), chi-squared will almost always reject because even tiny deviations become "statistically significant." That's why MAD and delta_B matter more in practice. Statistical significance ≠ practical significance.

---

## The Elevator Pitch (2 minutes)

"I test whether datasets follow a mathematical law called Benford's Law. It says that in nature, 30% of numbers start with 1, 18% start with 2, and so on down to 4.6% starting with 9. It's not intuitive but it's ironclad — it shows up in river flows, earthquake energies, wildfire sizes, everything.

Here's why it matters: I pulled burned area outputs from three climate models. Two of them — CESM2 and CESM2-WACCM — followed Benford's Law almost perfectly. The third one, CNRM, didn't. Its digit-2 was 27% instead of 18% — way off.

Turns out, the two that follow Benford are the ones the climate community already considers the best. The one that deviates uses an older fire scheme called GlobFIRM that's being phased out because it doesn't match satellite observations.

It took the modeling community years of satellite comparisons to figure out which models were better. The Benford test took 30 seconds.

The idea isn't to replace climate models. It's to give modelers a fast sanity check: run your model, count first digits, and if it doesn't follow Benford, don't bother with the expensive validation — go fix your physics first."

---

## The Napkin Demo

If someone hands you a napkin and a pen:

1. Write the Benford distribution:
   ```
   1: 30%  2: 18%  3: 12%  4: 10%  5-9: ~5-8% each
   ```

2. Write the CESM2 result next to it:
   ```
   1: 30%  2: 18%  3: 13%  4: 10%  ... nearly identical
   MAD = 0.0025
   ```

3. Write the CNRM result:
   ```
   1: 31%  2: 27%  3: 10%  4: 8%  ... digit 2 is WAY off
   MAD = 0.023
   ```

4. Draw a circle around the 27% and write: "GlobFIRM — probability cap clusters values"

5. Say: "The good models look like nature. The broken one doesn't. Thirty seconds of arithmetic."

---

## Common Objections and Responses

**"Isn't this just a coincidence with three models?"**
Fair point — we need more models. But the mechanism is clear: GlobFIRM has a hard probability ceiling of 1.0 that prevents the full power-law distribution. That's a structural constraint that Benford directly detects. It's not coincidence, it's math.

**"Chi-squared rejects the good models too."**
That's a large-sample effect, not a real deviation. At N=500,000, a 0.3% difference is "statistically significant." MAD and delta_B measure practical deviation, which is what matters. CESM2's MAD of 0.0025 is exceptional by any standard.

**"Why would fire sizes follow Benford's Law?"**
Because fire growth is multiplicative — a fire doubles, triples, gets suppressed by a fraction. Any process driven by multiplication across a wide range produces Benford-distributed first digits. It's a mathematical consequence of spanning many orders of magnitude.

**"What about data that doesn't follow Benford?"**
That's equally important. Temperature anomalies (-2 to +2 degrees) shouldn't follow it — too narrow a range. Ice core CO2 (170-420 ppm) shouldn't either. If those DID follow Benford, something would be wrong with our test. The negative controls validate the method.

**"Can you use this for fraud detection?"**
That's actually where Benford analysis started — detecting accounting fraud. Same principle. If someone fabricates emissions data, the digit distribution usually looks wrong because humans are bad at generating natural-looking numbers. But our focus is model validation, not fraud.

---

## The Math You Should Know Cold

**Benford probability for digit d:**
```
P(d) = log10(1 + 1/d)
```

**Quick derivation:** If data is uniformly distributed on a log scale (which multiplicative processes produce), then the probability of landing between log10(d) and log10(d+1) is log10(d+1) - log10(d) = log10((d+1)/d) = log10(1 + 1/d).

**MAD calculation (9 digits):**
```
MAD = (1/9) * sum(|obs_i - benford_i|) for i = 1..9
```

**delta_B calculation:**
```
delta_B = sqrt(sum((obs_i - benford_i)^2)) for i = 1..9
```

**Chi-squared:**
```
chi2 = sum((count_i - N*benford_i)^2 / (N*benford_i)) for i = 1..9
df = 8, look up p-value
```

That's the complete toolkit. Three formulas, one log function, and a table of thresholds.
