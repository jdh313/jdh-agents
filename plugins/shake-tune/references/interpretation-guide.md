# Shake Tune Interpretation Guide

Cross-cutting principles that apply to all Shake Tune test types. Read this before interpreting any specific test.

## Core Principles

### 1. Focus on Graph Shapes, Not Absolute Numbers

- Resonance frequencies vary by printer, toolhead mass, and belt tension
- What matters is the **shape** of curves: sharp vs. wide peaks, symmetry, noise floor
- Compare shapes between runs, not specific Hz or dB values
- Exception: gravity reading in axes map should be ~9.81 m/s²

### 2. Test at Thermal Equilibrium

- Results change significantly when the printer is cold vs. heated
- Always test at print temperature (bed + hotend at typical temps)
- Wait 10-15 minutes after reaching temp for frame expansion to stabilize
- Belt tension changes with temperature — cold tests are misleading

### 3. Different X/Y Results Are Normal

- Most printers have asymmetric mass distribution
- CoreXY: X axis moves the full gantry, Y moves the toolhead — different masses
- Bedslinger: X is the toolhead, Y is the entire bed — very different responses
- Don't try to make X and Y match — optimize each independently

### 4. Recommended Test Workflow Order

Run tests in this order for systematic tuning:

1. **Axes Map** — Verify accelerometer placement and axis mapping are correct
2. **Belt Comparison** (CoreXY only) — Ensure belts are balanced before shaper calibration
3. **Input Shaper** — Calibrate input shaper parameters for X and Y
4. **Vibration Profile** — Find optimal speed ranges and validate improvements

Excitation tests are used for targeted investigation, not routine tuning.

### 5. Don't Over-Optimize

- Diminishing returns set in quickly after the first round of tuning
- A "good enough" input shaper config is better than chasing perfection
- If prints look good, stop tuning — the graphs don't need to be perfect
- Re-test only after mechanical changes (belt swap, toolhead change, crash)

## Reading Shake Tune Graphs

### Common Graph Elements

- **X-axis (frequency):** Usually 0-200 Hz. Most relevant action is in 20-100 Hz range.
- **Y-axis (amplitude/energy):** Relative power spectral density. Higher = more vibration energy.
- **Shaded regions:** Often show recommended operating ranges or shaper effect zones.
- **Vertical dashed lines:** Mark specific frequencies (resonance peaks, shaper frequencies).
- **Spectrograms:** Color heatmaps showing frequency content over time. Bright spots = high energy.

### Color Conventions in Shake Tune Graphs

- **Red/warm colors:** Higher energy, potential problems
- **Blue/cool colors:** Lower energy, quieter operation
- **Green zones:** Recommended ranges (in vibration profiles)
- **Gray/light regions:** Background noise floor

## Printer-Specific Considerations

### CoreXY

- Belt comparison is essential — A and B belts must be balanced
- Gantry flex at high speeds shows as broad low-frequency energy
- Cross-coupling between X and Y is common — fix belts before shaper tuning
- Motor mount rigidity affects high-frequency behavior

### Bedslinger (i3-style)

- No belt comparison test (single belt per axis)
- Y-axis response dominated by bed mass — expect lower resonance frequency
- Bed slingers often need lower max acceleration on Y
- Glass beds vs. spring steel change the Y response significantly

### Delta

- All three axes contribute to each movement
- Input shaper tuning is less straightforward
- Focus on vibration profiles for speed optimization

## Common Artifacts and Noise Sources

| Artifact | Appearance | Source | Action |
|----------|-----------|--------|--------|
| ~125 Hz spike | Sharp peak at ~125 Hz on both axes | Voron TAP optical sensor | Informational — doesn't affect print quality |
| Jagged/spiky spectrogram | Irregular bright spots across frequencies | CANBUS communication noise | Check CANBUS wiring, ensure proper termination |
| Flat energy above 100 Hz | Elevated noise floor in high frequencies | LIS2DW accelerometer aliasing | Sensor limitation — ignore data above ~100 Hz |
| Periodic vertical lines in spectrogram | Evenly spaced bright columns | Fan vibration harmonics | Turn off fans during testing, or note as unavoidable |
| Broadband low-frequency hump | Wide energy spread below 30 Hz | Frame/gantry flex | Improve frame rigidity, check joints |

## When to Re-Test

- After any mechanical change (belt swap, toolhead change, nozzle change)
- After a crash or collision
- If print quality suddenly changes
- Seasonally (temperature-sensitive setups like garages)
- After significant firmware updates that affect motion

## Historical Comparison Tips

- Compare same test type across sessions — don't cross-compare belt vs. shaper
- Focus on whether peaks shifted, widened, or new peaks appeared
- Belt comparison: look for similarity % changes
- Input shaper: look for resonance frequency shifts (belt tension change) or new peaks (loosening)
- Vibration profile: look for new hot spots at speeds that were previously clean

## References

- [Frix-x/klippain-shaketune — GitHub Repository](https://github.com/Frix-x/klippain-shaketune) — Primary source for Shake&Tune; includes overview of all macros, graph types, and how to interpret each
- [Shake&Tune: IS Tuning Generalities](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/is_tuning_generalities.md) — Frix-x's own interpretation guide covering what to look for in resonance graphs, peak shapes, noise floors, and shaper selection
- [Shake&Tune: Axes Shaper Calibration Interpretation](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/axes_shaper_calibrations.md) — Detailed breakdown of input shaper graph elements and how to read the recommended shaper parameters
- [Shake&Tune: Belt Comparison Interpretation](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/compare_belts_responses.md) — How to read the differential belt resonance graph; explains the diagonal center-line symmetry target and what imbalance looks like
- [Resonance Compensation — Klipper Documentation](https://www.klipper3d.org/Resonance_Compensation.html) — Official Klipper docs on input shaper types (MZV, EI, 2HEI, etc.), tradeoffs, and how the `[input_shaper]` config section works
- [Measuring Resonances — Klipper Documentation](https://www.klipper3d.org/Measuring_Resonances.html) — Official Klipper docs on accelerometer setup, running resonance tests, and interpreting raw CSV output that underlies Shake&Tune graphs
- [Ellis' Print Tuning Guide — Tuning Index](https://ellis3dp.com/Print-Tuning-Guide/articles/index_tuning.html) — Community reference covering input shaper in context of broader print quality tuning; useful for understanding how IS results translate to slicer acceleration settings
