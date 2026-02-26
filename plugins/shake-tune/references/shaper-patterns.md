# Input Shaper Patterns

Visual pattern reference for interpreting input shaper calibration graphs. Covers both the upper PSD graph and lower spectrogram panel.

## Good PSD Patterns

### Single Sharp Peak
- **Visual:** One clearly defined, narrow peak rising well above the noise floor
- **Frequency:** Typically 40-80 Hz for CoreXY, 30-50 Hz for bedslingers
- **Width:** Narrow (spans <10 Hz at half-height)
- **Meaning:** Clean, well-defined resonance. The easiest case to tune.
- **Shaper:** ZV works well. MZV for extra robustness.
- **Why good:** Single mode means the shaper has one target to suppress.

### Single Wide Peak
- **Visual:** One broad peak spanning 15-25 Hz at half-height
- **Frequency:** Similar ranges but wider footprint
- **Meaning:** Higher damping in the system, or closely-spaced modes blending together
- **Shaper:** MZV or EI — ZV is too narrow to cover the full peak width
- **Note:** Wide peaks aren't bad — the system has natural damping. But the shaper needs to cover the full width.

### Two Peaks, Close Together (within 20 Hz)
- **Visual:** Two distinct peaks with some overlap between them
- **Meaning:** Two resonant modes (e.g., toolhead + gantry) at similar frequencies
- **Shaper:** MZV handles this well if the gap is <20 Hz. Otherwise 2HUMP_EI.
- **Note:** Common on printers with heavy toolheads or long belt paths

### Clean Filtered Responses
- **Visual:** The colored shaper lines (ZV, MZV, etc.) all effectively suppress the raw peak, with low residual energy
- **Meaning:** Any shaper will work. Choose based on speed preference.
- **Best indicator:** When even the most aggressive shaper line (ZV) keeps residual energy below the noise floor

## Problem PSD Patterns

### Two Peaks Far Apart (>20 Hz gap)
- **Visual:** Two clearly separated peaks with a valley between them
- **Meaning:** Two distinct resonant modes that can't be covered by a single-band shaper
- **Shaper:** 2HUMP_EI or 3HUMP_EI needed. MZV will only suppress one peak.
- **Investigation:** Identify what each mode corresponds to — one may be fixable mechanically.

### Multiple Peaks (3+)
- **Visual:** Several peaks across the frequency range, complex response
- **Meaning:** Multiple mechanical resonances. Could indicate loose hardware, worn bearings, or a fundamentally flexible structure.
- **Shaper:** 3HUMP_EI as a band-aid, but mechanical investigation recommended
- **Fix first:** Check frame bolts, gantry joints, motor mounts, idler bearings before accepting this as "normal"

### Very Low Frequency Peak (<25 Hz)
- **Visual:** Primary peak below 25 Hz
- **Meaning:** Very loose or very heavy system. On bedslingers, this may be normal for Y. On CoreXY, it suggests loose belts or frame issues.
- **Shaper:** EI with aggressive smoothing, but fix the mechanical issue first
- **Fix:** Tighten belts, check frame rigidity, verify motor mount bolts

### Flat Response (No Clear Peak)
- **Visual:** Relatively flat line with no obvious peak
- **Meaning:** Either very high damping (good) or accelerometer isn't measuring correctly (bad)
- **Diagnosis:** If prints show no ringing, the system may genuinely not need input shaper. If prints show ringing, recheck accelerometer mounting.

### Peak Above 100 Hz
- **Visual:** Primary resonance peak above 100 Hz
- **Meaning:** Very stiff, light system. Good mechanically.
- **Shaper:** ZV or MZV — peak is so high that even light shaping is effective
- **Note:** If using LIS2DW accelerometer, peaks above ~100 Hz may be aliasing artifacts. Verify with ADXL345 if uncertain.

## Spectrogram Patterns

### Clean Spectrogram
- **Visual:** Single bright horizontal band at the resonance frequency, fading smoothly above and below
- **Background:** Uniform dark (low energy) everywhere else
- **Meaning:** Clean measurement, no significant artifacts. Trust the PSD result.

### Fan Harmonics
- **Visual:** Multiple evenly-spaced horizontal bright lines throughout the spectrogram
- **Spacing:** Typically 40-60 Hz apart (depends on fan RPM)
- **Meaning:** Part cooling or hotend fan vibration bleeding into the measurement
- **Fix:** Turn off fans during testing (M106 S0) or accept as noise
- **Impact:** Can confuse PSD peak detection. If your PSD shows peaks at regular intervals matching fan speed, re-test with fans off.

### CANBUS Noise
- **Visual:** Jagged, spiky bright spots scattered irregularly, especially at higher frequencies
- **Meaning:** Electromagnetic interference from CANBUS communication corrupting accelerometer data
- **Fix:** Check CANBUS wiring, ensure proper 120-ohm termination, route CANBUS cable away from power wires
- **Impact:** Can make the PSD noisy and peak identification difficult. Consider USB-connected accelerometer for cleaner data.

### LIS2DW Aliasing ("Lightshow")
- **Visual:** Elevated bright band across all frequencies above ~100 Hz, appearing as a "wall" of energy
- **Meaning:** LIS2DW sensor's lower sample rate causes aliasing of high-frequency content
- **Fix:** Not fixable — it's a sensor limitation. Ignore data above ~100 Hz.
- **Impact:** Doesn't affect the primary resonance reading (usually below 100 Hz), but can be confusing visually.

### TAP Wobble
- **Visual:** Narrow bright line at approximately 125 Hz across the entire spectrogram
- **Meaning:** Voron TAP optical sensor's spring mechanism resonating
- **Fix:** None needed — this is cosmetic in the measurement and doesn't affect print quality
- **Impact:** Creates a small peak in the PSD at ~125 Hz. Don't mistake it for a real resonance that needs shaping.

### Motor Resonance Diagonals
- **Visual:** Bright diagonal bands that increase in frequency as sweep speed increases
- **Meaning:** Speed-dependent motor vibration (stepper motor cogging at varying speeds)
- **Impact:** Usually informational. If severe, may indicate motor driver tuning issues.

## Shaper Comparison Quick Reference

| Shaper | Vibration Reduction | Smoothing | Max Accel Impact | Best For |
|--------|-------------------|-----------|-----------------|----------|
| ZV | Moderate | Minimal | Least reduction | Single sharp peak, speed priority |
| MZV | Good | Moderate | ~10-20% reduction | Most printers, general use |
| EI | Very good | More | ~20-30% reduction | Wide or shifting peaks, reliability |
| 2HUMP_EI | Excellent | Significant | ~30-40% reduction | Two-peak resonance |
| 3HUMP_EI | Maximum | Heavy | ~40-50% reduction | Complex multi-peak, last resort |

## Before/After Comparison Guide

When comparing shaper results before and after a change:

1. **Peak position shift** — Did the resonance frequency change?
   - Up = tighter belts or lighter toolhead
   - Down = looser belts or heavier toolhead
2. **Peak width change** — Narrower is better (less damping uncertainty)
3. **Peak count change** — Fewer peaks is better (fewer modes to manage)
4. **Recommended shaper change** — If the recommendation changed from EI to MZV or ZV, the mechanical improvement was meaningful
5. **Max accel change** — Higher recommended accel = better (can print faster)

## References

- [Shake&Tune: Axes Shaper Calibration — Official Documentation](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/axes_shaper_calibrations.md) — Frix-x's canonical guide to the AXES_SHAPER_CALIBRATION macro: graph reading, shaper selection, and interpreting PSD and spectrogram panels
- [Shake&Tune: Input Shaper Tuning Generalities](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/is_tuning_generalities.md) — General principles: heat-soak conditions, MEASURE_AXES_NOISE thresholds (<100 on all axes), and why exact numbers matter less than graph shape
- [Shake&Tune: Full Documentation Index](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/README.md) — Top-level docs directory linking all Shake&Tune macro guides
- [Klipper: Resonance Compensation](https://www.klipper3d.org/Resonance_Compensation.html) — Official Klipper documentation on input shaper types (ZV, MZV, EI, 2HUMP_EI, 3HUMP_EI): trade-offs between vibration suppression, smoothing, and sensitivity to frequency measurement error
- [Klipper: Configuration Reference — [input_shaper]](https://www.klipper3d.org/Config_Reference.html) — Full config reference for the [input_shaper] section: shaper_freq_x/y, shaper_type, damping_ratio parameters
- [Klipper: Measuring Resonances](https://www.klipper3d.org/Measuring_Resonances.html) — Official docs covering ADXL345, LIS2DW, and LIS3DH accelerometer setup, wiring, mounting requirements, and the TEST_RESONANCES/SHAPER_CALIBRATE workflow
- [Klipper Input Shaper Tuning — Clever Creations](https://clevercreations.org/klipper-input-shaping-resonance-compensation/) — Community guide with practical examples of shaper type selection, graph interpretation, and before/after comparisons
- [ADXL345 Accelerometer Setup for Klipper — Clever Creations](https://clevercreations.org/adxl345-klipper-accelerometer-ender-3/) — Step-by-step ADXL345 wiring, config, and noise validation; useful background for understanding LIS2DW differences mentioned in the aliasing pattern above
