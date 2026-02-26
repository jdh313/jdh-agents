# Vibration Profile Patterns

Visual pattern reference for interpreting vibration profile graphs. The vibration profile is a 6-panel figure; patterns here focus primarily on the global energy profile (Panel 1) and supporting panels.

## Good Global Energy Patterns

### Clean Valley Profile
- **Visual:** Low, flat energy baseline with gentle rises at specific speeds
- **Hot spots:** Few or none — energy stays close to baseline throughout
- **Meaning:** Printer handles a wide range of speeds cleanly
- **Speed guidance:** Can print at almost any speed. Pick based on quality/speed trade-off preference.
- **Common on:** Well-tuned CoreXY printers with good input shaper config

### Valley-with-Notch Profile
- **Visual:** Generally low energy with 1-2 narrow peaks (notches) at specific speeds
- **Hot spots:** Narrow, well-defined peaks that can be avoided precisely
- **Meaning:** Motor resonance at specific speeds, but overall system is well-tuned
- **Speed guidance:** Avoid the specific hot spot speeds, everything else is fair game
- **Common on:** Most printers after input shaper tuning

### Gradual Rise Profile
- **Visual:** Energy slowly increases with speed but stays moderate until high speeds
- **Hot spots:** No specific peaks, just a general upward trend
- **Meaning:** System is clean but vibration naturally increases with speed
- **Speed guidance:** Set speed ceiling where energy becomes unacceptable (usually where curve inflects upward sharply)

## Problem Global Energy Patterns

### Multi-Peak Profile
- **Visual:** Multiple pronounced peaks across the speed range
- **Hot spots:** Several elevated regions making it hard to find clean zones
- **Meaning:** Multiple resonances excited at different speeds. Input shaper may not be well-tuned.
- **Fix:** Re-run input shaper calibration. If already done, check mechanical issues.

### Elevated Baseline
- **Visual:** High energy across all speeds, even at the lowest tested speeds
- **Hot spots:** Hard to identify — everything is elevated
- **Meaning:** Systemic vibration issue. Frame flex, loose hardware, or poor accelerometer mounting.
- **Fix:** Address mechanical basics before speed optimization: frame bolts, gantry, motor mounts.

### Cliff Profile
- **Visual:** Clean at low speeds, then a sharp, steep rise at a specific speed with no recovery
- **Hot spots:** Everything above the cliff speed
- **Meaning:** The printer's mechanical limit for clean motion. Printing above this speed will always have issues.
- **Speed guidance:** Set max speed just below the cliff. Accept this as the printer's limit.

### Sawtooth Profile
- **Visual:** Regular repeating peaks at evenly-spaced speed intervals
- **Hot spots:** Periodic, predictable peaks
- **Meaning:** Motor harmonic resonance — the stepper motor's natural vibration frequencies align with these speeds
- **Speed guidance:** Print in the valleys between peaks

## Polar Plot Patterns

### Symmetric Circle (Good — CoreXY)
- **Visual:** Roughly circular shape centered on origin
- **Meaning:** Equal vibration in all directions. Balanced system.
- **Note:** Perfect circle is ideal but rare. Slight elongation is normal.

### Symmetric at 45/135 (Expected — CoreXY)
- **Visual:** Slightly elongated along the 45° and 135° axes
- **Meaning:** Normal CoreXY behavior — belt paths at 45° and 135° carry more energy
- **Note:** As long as both lobes are similar, this is fine

### Asymmetric Lobes
- **Visual:** One lobe significantly larger than the other
- **Meaning:** One axis or belt path has more vibration than the other
- **Diagnosis:** Compare with per-axis panel to identify which axis is worse
- **Fix:** If CoreXY, check belt balance (run belt comparison). If cartesian, address the problematic axis.

### Elongated in X or Y
- **Visual:** Stretched along 0° (X) or 90° (Y) axis
- **Meaning:** That axis dominates vibration. Could be belt tension, mass imbalance, or driver issue.
- **Fix:** Focus mechanical improvements on the elongated axis

## Spectrogram Patterns

### Clean Diagonal Lines
- **Visual:** Straight diagonal lines from lower-left to upper-right
- **Meaning:** Speed-dependent motor harmonics. Normal and expected.
- **Impact:** Creates the hot spots in the global energy profile at specific speeds.

### Horizontal Bright Lines
- **Visual:** Horizontal lines at fixed frequencies
- **Meaning:** Structural resonance independent of speed. Input shaper targets these.
- **Impact:** If input shaper is configured, these should be suppressed. If still bright, input shaper may need retuning.

### Bright Cloud at High Speed
- **Visual:** Diffuse bright region at high speeds across many frequencies
- **Meaning:** System becoming chaotic at high speeds. This is the speed limit.
- **Impact:** Set max speed below where the cloud starts.

### Dark/Clean Regions
- **Visual:** Dark regions with minimal energy
- **Meaning:** These speed-frequency combinations are clean. Good.
- **Impact:** Corresponds to the valleys in the global energy profile.

## Speed Zone Classification

Use these labels when presenting speed recommendations:

| Zone | Energy Level | Print Use |
|------|-------------|-----------|
| **Clean** | At or near baseline | External perimeters, top surfaces, detail work |
| **Moderate** | 1.5-2x baseline | Internal perimeters, solid infill |
| **Hot** | >2x baseline | Avoid for quality, acceptable for travel moves only |
| **Critical** | >3x baseline | Avoid entirely — ringing, artifacts, potential skipping |

## Before/After Comparison Guide

When comparing vibration profiles:

1. **Hot spots moved or disappeared** — Mechanical change affected resonance frequencies
2. **Baseline energy decreased** — System-wide improvement (better tuning, tighter hardware)
3. **New hot spots appeared** — Something loosened or changed, investigate
4. **Same hot spots, lower peaks** — Input shaper improvement helping, but mechanical source remains
5. **Polar plot more symmetric** — Belt balance improved
6. **Clean zone expanded** — Wider range of usable speeds. This is the win.

## References

- [Shake&Tune: CREATE_VIBRATIONS_PROFILE documentation](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/create_vibrations_profile.md) — Official macro docs covering vibration profile graph interpretation, hot spots, and speed optimization
- [Shake&Tune: Input shaper tuning generalities](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/is_tuning_generalities.md) — Background on input shaper concepts, graph reading, and mechanical diagnosis
- [Shake&Tune: Axes shaper calibration](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/axes_shaper_calibrations.md) — AXES_SHAPER_CALIBRATION macro docs used alongside vibration profiling
- [Shake&Tune GitHub repository (Frix-x)](https://github.com/Frix-x/klippain-shaketune) — Main project repo with full documentation index
- [Klipper: Measuring Resonances](https://www.klipper3d.org/Measuring_Resonances.html) — Official Klipper guide on accelerometer setup, resonance testing, and input shaper workflow
- [Klipper: Resonance Compensation](https://www.klipper3d.org/Resonance_Compensation.html) — Klipper docs on input shaper configuration and applying resonance compensation
- [OrcaSlicer: VFA Calibration guide](https://www.orcaslicer.com/wiki/calibration/vfa-calib) — Speed tower test for identifying VFA (Vertical Fine Artifacts) hot spots in your slicer speed settings
- [Obico: Speed Test in OrcaSlicer (VFA)](https://www.obico.io/blog/speed-test-in-orcaslicer-vfa-a-comprehensive-guide/) — Practical walkthrough of using OrcaSlicer's VFA speed test to correlate vibration profile data with print quality results
