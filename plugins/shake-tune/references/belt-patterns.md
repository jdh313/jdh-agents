# Belt Comparison Patterns Reference

This guide shows visual patterns you'll see in Klippain Shake Tune belt comparison graphs and what they mean for printer health.

## Good Belt Balance

### Pattern: High Overlap (>90% similarity)

**Visual characteristics:**
- Two curves almost perfectly overlay one another
- Peaks align at the same frequency within 1-2 Hz
- Peak heights are equal (within 10% amplitude difference)
- Both curves rise and fall together across the spectrum

**What it means:**
- Belts are properly tensioned and balanced
- No adjustment needed
- Printer is ready for input shaper calibration

**Example interpretation:**
"Your belts are excellently balanced. The similarity is 94%, peaks are aligned at 52 Hz, and both curves show identical behavior. No mechanical adjustment is needed."

---

## Acceptable Balance (70-90% similarity)

### Pattern: Minor Offset

**Visual characteristics:**
- Curves are similar in shape but offset by 5-10 Hz
- Peak heights are similar but one is slightly taller
- Overall energy distribution is comparable
- Similarity percentage shows 75-88%

**What it means:**
- Slight tension difference between belts (typically 1-2% difference)
- Minor adjustment could improve balance but not critical
- Printer will print acceptably, but input shaper results may be slightly suboptimal

**Root cause:**
- Gradual loosening of one belt over time
- Tensioner spring relaxation
- Ambient temperature changes affecting polymer belt stretch

**Example interpretation:**
"Your belts are acceptable at 81% similarity, but Belt A's peak is 6 Hz higher than Belt B's. This suggests Belt A is slightly looser. Tightening it by one half-turn should bring them into excellent alignment."

---

## Needs Attention (50-70% similarity)

### Pattern: Frequency Shift

**Visual characteristics:**
- Curves have similar shape but are clearly separated
- Peak offset is 10-20+ Hz
- One peak is noticeably taller than the other
- Curve slopes may differ slightly
- Clear visual separation between the two lines

**What it means:**
- Significant tension imbalance between belts
- One belt is measurably looser (or tighter) than the other
- Input shaper calibration will be compromised
- Print quality will suffer (ringing, ghosting on different axes)

**Root cause:**
- One tensioner wasn't tightened properly during assembly
- Belt slippage or skip
- Significant tensioner drift since initial setup

**Example interpretation:**
"Belt comparison shows 63% similarity with a clear 15 Hz frequency shift — Belt A peaks at 52 Hz, Belt B at 37 Hz. This indicates Belt B is significantly looser. Tighten Belt B by 2-3 half-turns, then re-run the comparison."

---

## Problem Detected (<50% similarity)

### Pattern: Drastically Different Shapes

**Visual characteristics:**
- Curves have completely different shapes, not just shifted
- One curve has a single sharp peak, the other has multiple peaks or is very broad
- Peak heights differ dramatically (2:1 or worse)
- One curve is much noisier than the other
- Similarity percentage is below 50%, often 20-40%

**What it means:**
- Severe mechanical problem with one belt
- Belt may be damaged, slipping, or have internal issues
- Frame or gantry movement is compromised
- Printer is not suitable for motion calibration in this state

**Root causes:**
- Belt is worn, cracked, or degraded
- Belt is twisted or misaligned in the path
- Idler bearing is failing and damping one belt path
- Belt skip or slippage during the test
- One belt is not properly seated on pulleys

**Example interpretation:**
"Similarity is only 38% — this indicates a serious mechanical problem. Belt A shows a sharp, clean 52 Hz peak, but Belt B is very broad and noisy with no clear resonance. This suggests Belt B may have a worn idler bearing or the belt itself is damaged. Inspect the Belt B idler bearing for roughness, and visually inspect both belts for cracks or deformation."

---

## Specific Pattern Recognition

### Offset Peaks (Same Shape, Different Frequency)

```
Belt A: Sharp peak at 52 Hz
Belt B: Sharp peak at 45 Hz
Similarity: 72%
```

**Diagnosis:** Tension imbalance, typically 5-10% difference.

**Fix:** Tighten the belt with the lower-frequency peak (Belt B in this case). Each quarter-turn of a typical belt tensioner changes frequency by ~2-3 Hz.

**Verification:** Re-run comparison. Peak positions should move closer together.

---

### Unpaired Peaks (One Belt Has Extra Peak)

```
Belt A: Peaks at 52 Hz and 104 Hz (second harmonic)
Belt B: Peak at 52 Hz only
Similarity: 58%
```

**Diagnosis:** One belt path has an obstruction, or one idler bearing is degraded.

**Fix:** Inspect Belt B's path for:
- Foreign objects (dust, debris) stuck in belt path
- Idler bearing roughness (spin bearing by hand, listen for grinding)
- Belt twisted in the path
- Pulley misalignment (belts should enter/exit pulleys squarely)

**Verification:** Remove obstruction or replace idler, then re-run.

---

### Wide vs. Sharp Peaks

```
Belt A: Sharp peak at 52 Hz, height 1.0
Belt B: Very broad peak (35-65 Hz range), height 0.6
Similarity: 44%
```

**Diagnosis:** One belt is loose (overdamped, broad peak) while the other is tight (sharp peak).

**Fix:** Tighten the loose belt (Belt B) significantly. The broad peak indicates insufficient tension.

**Note:** Loose belts produce lower frequencies and broader resonances. Tight belts produce sharp, high peaks.

---

### High Low-Frequency Energy (Both Curves)

```
Both belts show elevated energy below 30 Hz
Peaks occur at 50+ Hz as expected
Similarity: 87%
```

**Diagnosis:** Belts are actually well-balanced, but frame rigidity issue is present.

**Fix:** This is NOT a belt problem. Check:
- Frame bolts (are all screws tight?)
- Bed mounting (does bed rock side-to-side?)
- Gantry joints (are linear rails square and tight?)
- Extrusion squareness (use a square to check 90-degree angles)

**Note:** Don't adjust belts to fix frame problems — you'll chase your tail. Fix the mechanical foundation first.

---

### Asymmetric Noise Floor

```
Belt A: Clean baseline, noise floor at 0.2 units
Belt B: High noise floor at 0.8 units
Both peaks at 52 Hz, but Belt B is noisier
```

**Diagnosis:** One accelerometer is producing more electrical noise, or one belt path is resonating against the frame.

**Fix:**
- Verify accelerometer mounting on both paths (should be identical, secure, clean contact)
- Check if one accelerometer is older/different model (can produce different noise signatures)
- Inspect belt routing — does one belt rub against a frame part?

---

## Before & After Comparison

### User adjusts belts and provides two graphs

**Before:** Similarity 62%, Belt A peak at 52 Hz, Belt B peak at 40 Hz
**After:** Similarity 89%, both peaks at 50 Hz

**Assessment:** "Excellent improvement. Your Belt B tightening was successful — the frequency gap closed from 12 Hz to 0 Hz, and similarity jumped to 89%. Your belts are now well-balanced. Run SHAPER_CALIBRATE to establish input shaper parameters with your balanced belts."

---

## Troubleshooting Guide

### "The graph looks weird compared to others I've seen"

Possible causes:
1. **Different Shake Tune version** — older versions may have different scaling or format
2. **Different accelerometer** — LIS2DW vs ADXL345 produce different noise signatures
3. **Different frequency range** — some versions zoom to 5-150 Hz, others go to 200 Hz
4. **Different printer type** — CoreXY vs H-bot vs cartesian will look different

**Action:** Ask user which accelerometer and Shake Tune version they're using. If format is truly different, it may be from a custom build.

---

### "My belt comparison is inverted/flipped compared to examples"

Possible causes:
1. **Axis labeling** — some graphs show "X" and "Y" instead of "A" and "B"
2. **Color inversion** — doesn't matter, physics is the same
3. **User rotated the image** — doesn't change the interpretation

**Action:** Look at the peak positions, similarity %, and relative curve shapes. The actual frequency and energy values are what matter.

---

### "One peak is at the belt frequency, the other at 2x"

**This is actually OK and normal.** Some belt paths will show fundamental frequency and first harmonic depending on belt routing. As long as the peaks are at the same intervals on both belts (e.g., both have fundamental + 1st harmonic), they're balanced.

---

## Key Takeaway

The belt comparison is fundamentally about assessing **whether both belt paths see the same mechanical environment**. If they do:
- Curves overlay (high similarity)
- Peaks align at the same frequency
- Peak shapes and heights are similar

If they don't, something in the mechanical system differs between paths — find and fix it.

## References

- [Shake&Tune: Compare Belt Responses — Official Documentation](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/compare_belts_responses.md) — Frix-x's canonical guide to interpreting the COMPARE_BELTS_RESPONSES macro output, including graph zones and common failure modes
- [Shake&Tune: Input Shaper Tuning Generalities](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/is_tuning_generalities.md) — General principles for using Shake&Tune: heat-soak conditions, accelerometer noise thresholds, and graph interpretation philosophy
- [Shake&Tune: Full Documentation Index](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/README.md) — Top-level docs directory for all Shake&Tune macros and guides
- [Klipper: Measuring Resonances](https://www.klipper3d.org/Measuring_Resonances.html) — Official Klipper documentation covering accelerometer setup (ADXL345, LIS2DW), TEST_RESONANCES command, and belt frequency measurement workflow
- [Klipper: Resonance Compensation](https://www.klipper3d.org/Resonance_Compensation.html) — Official Klipper docs on input shaper configuration and resonance compensation concepts relevant to belt tuning
- [CoreXY Belt Routing — 3D Distributed](https://3ddistributed.com/corexy-3d-printer/corexy-belt-routing/) — Explanation of CoreXY belt paths (stacked vs. crossed), alignment requirements, and how belt routing affects resonance measurements
- [Belt Frequency and Tensioning — 3D Distributed](https://3ddistributed.com/belt-frequency-and-tensioning/) — Practical guide to belt tension targets, frequency-based tensioning (Hz over a fixed span), and the relationship between tension and peak frequency in resonance graphs
- [CoreXY Mechanism Layout and Belt Tensioning — Mark Rehorst](https://drmrehorst.blogspot.com/2018/08/corexy-mechanism-layout-and-belt.html) — Engineering-focused analysis of CoreXY belt tension coupling and how asymmetric tension causes gantry rack
