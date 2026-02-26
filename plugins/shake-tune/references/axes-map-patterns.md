# Axes Map Patterns

Visual pattern reference for axes map calibration results.

## Good Patterns

### Clean Axis Mapping
- **Visual:** Three distinct, well-separated axes with clear primary directions
- **Gravity:** 9.7-10.0 m/s² pointing in the expected Z direction
- **Tilt:** <5°
- **Noise:** Low, clean signals
- **Meaning:** Accelerometer is correctly mounted and oriented. Ready for testing.

### Slightly Tilted but Correct
- **Visual:** Axes are correctly mapped but the gravity vector is slightly off-vertical
- **Gravity:** 9.7-10.0 m/s²
- **Tilt:** 5-15°
- **Noise:** Low
- **Meaning:** Sensor is a bit tilted. Results are still usable with minor accuracy loss.
- **Action:** Acceptable for most users. Perfectionists can remount more level.

## Problem Patterns

### Duplicate Axis Mapping
- **Visual:** Two printer axes produce response on the same accelerometer axis
- **Gravity:** May be normal
- **Meaning:** Sensor is oriented incorrectly — typically rotated 90° around one axis
- **Fix:** Physically remount the sensor with correct orientation, or adjust axes_map in printer.cfg

### Swapped Axes
- **Visual:** X movement produces Y-axis response and vice versa
- **Gravity:** Normal
- **Meaning:** Sensor is rotated around the Z axis relative to expected orientation
- **Fix:** Rotate sensor physically, or swap axis mapping in Klipper config:
  ```ini
  [adxl345]  # or [lis2dw]
  axes_map: y,x,z  # Example — adjust to match your rotation
  ```

### Low/Zero Gravity
- **Visual:** Gravity magnitude significantly below 9.5 m/s² or near zero
- **Meaning:** Sensor not measuring correctly — power issue, bad connection, or hardware failure
- **Fix:** Check wiring, verify SPI/I2C connection, try different cable/port, replace sensor if needed

### High Noise Floor
- **Visual:** Signals are noisy with high baseline energy even at rest
- **Gravity:** May be normal
- **Meaning:** Electromagnetic interference (common with CANBUS), loose mounting, or damaged sensor
- **Fix:** Tighten sensor mount, check for loose screws, route accelerometer cable away from motor/heater wires

### Very High Tilt (>15°)
- **Visual:** Gravity vector significantly off-vertical
- **Gravity:** Normal magnitude but wrong direction
- **Meaning:** Sensor physically tilted on the mounting surface
- **Fix:** Remount more level. If on a toolhead with an angled surface, use a shim or different mounting position.

## Pre-Flight Checklist

Before trusting axes map results:
1. Printer should be at print temperature (thermal expansion affects mounting)
2. No fans running (vibration affects readings)
3. Toolhead should be roughly centered on the bed
4. No filament drag or umbilical tension on the toolhead
5. Printer on a stable surface (not wobbly table)

## References

- [Shake&Tune: AXES_MAP_CALIBRATION documentation](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/axes_map_calibration.md) — Official macro docs covering axes map detection algorithm, virtual axis extrapolation, and interpreting calibration output
- [Shake&Tune GitHub repository (Frix-x)](https://github.com/Frix-x/klippain-shaketune) — Main project repo with full documentation index
- [Klipper: Measuring Resonances](https://www.klipper3d.org/Measuring_Resonances.html) — Official Klipper guide on accelerometer setup including ADXL345 and LIS2DW wiring, mounting, and axes_map configuration
- [Klipper: Configuration Reference](https://www.klipper3d.org/Config_Reference.html) — Full reference for accelerometer chip config sections ([adxl345], [lis2dw], etc.) including the axes_map parameter and supported negation syntax
- [Klipper: Resonance Compensation](https://www.klipper3d.org/Resonance_Compensation.html) — Klipper docs on applying resonance measurements to input shaper configuration after axes map is confirmed correct
