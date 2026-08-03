# Printer Profiles

Printer profiles provide context for more targeted analysis and recommendations. A profile is optional — analysis works without one, but recommendations are more specific with it.

## Profile Location

- **Primary:** `.shake-tune-profile.json` in the parent directory of the results folder
- **Fallback:** `.shake-tune-profile.json` in the results directory itself
- **Example:** If results are in `~/printer_data/config/ShakeTune_results/`, check `~/printer_data/config/.shake-tune-profile.json`

## Profile Schema

```json
{
  "printer_name": "string (required) — friendly name for the printer",
  "kinematics": "string (required) — corexy | cartesian | delta | hybrid_corexy",
  "frame": {
    "type": "string — aluminum_extrusion | steel | printed",
    "size": "string — 250 | 300 | 350 (build volume in mm)",
    "notes": "string — any frame-specific notes (e.g., 'Voron 2.4r2', 'Ender 3 S1 Pro')"
  },
  "belts": {
    "type": "string — gates_2gt | gates_6mm | generic_gt2",
    "path": "string — a_b (CoreXY) | single_per_axis (cartesian)",
    "notes": "string — e.g., 'replaced 2025-01-15'"
  },
  "toolhead": {
    "type": "string — e.g., 'Stealthburner + CW2', 'Dragon HF', 'Rapido 2'",
    "mass": "string — light | medium | heavy",
    "notes": "string — e.g., 'with CPAP fan mod'"
  },
  "accelerometer": {
    "type": "string — ADXL345 | LIS2DW | MPU6050",
    "placement": "string — toolhead | bed | nozzle_tip",
    "connection": "string — SPI | USB | CANBUS"
  },
  "drivers": {
    "type": "string — TMC2209 | TMC2240 | TMC5160",
    "notes": "string — e.g., 'UART mode', '48V'"
  },
  "probe": {
    "type": "string — TAP | Klicky | BLTouch | Beacon | Cartographer | none"
  },
  "notes": "string — any additional context (mods, known issues, etc.)"
}
```

All fields except `printer_name` and `kinematics` are optional. Include what you know — skip what you don't.

## Example Profiles

### CoreXY (Voron 2.4)

```json
{
  "printer_name": "V2.4 350",
  "kinematics": "corexy",
  "frame": {
    "type": "aluminum_extrusion",
    "size": "350",
    "notes": "Voron 2.4r2"
  },
  "belts": {
    "type": "gates_2gt",
    "path": "a_b"
  },
  "toolhead": {
    "type": "Stealthburner + CW2 + Rapido 2",
    "mass": "medium"
  },
  "accelerometer": {
    "type": "ADXL345",
    "placement": "toolhead",
    "connection": "SPI"
  },
  "drivers": {
    "type": "TMC2209"
  },
  "probe": {
    "type": "TAP"
  },
  "notes": "Titanium backers on X gantry, nevermore filter installed"
}
```

### Bedslinger (Ender 3)

```json
{
  "printer_name": "Ender 3 S1 Pro",
  "kinematics": "cartesian",
  "frame": {
    "type": "aluminum_extrusion",
    "size": "235",
    "notes": "Stock frame with CR Touch"
  },
  "belts": {
    "type": "generic_gt2",
    "path": "single_per_axis"
  },
  "toolhead": {
    "type": "Stock direct drive",
    "mass": "medium"
  },
  "accelerometer": {
    "type": "ADXL345",
    "placement": "toolhead",
    "connection": "SPI"
  },
  "drivers": {
    "type": "TMC2209"
  },
  "probe": {
    "type": "BLTouch"
  }
}
```

### CoreXY (Voron Trident)

```json
{
  "printer_name": "Trident 300",
  "kinematics": "corexy",
  "frame": {
    "type": "aluminum_extrusion",
    "size": "300",
    "notes": "Voron Trident, Z with 3x leadscrew"
  },
  "belts": {
    "type": "gates_2gt",
    "path": "a_b"
  },
  "toolhead": {
    "type": "Mini Stealthburner + Orbiter 2 + Dragon",
    "mass": "light"
  },
  "accelerometer": {
    "type": "LIS2DW",
    "placement": "nozzle_tip",
    "connection": "CANBUS"
  },
  "drivers": {
    "type": "TMC2240"
  },
  "probe": {
    "type": "Beacon"
  },
  "notes": "CANBUS toolhead via EBB36"
}
```

## How Profiles Influence Analysis

| Profile Field | Influence on Analysis |
|---------------|----------------------|
| `kinematics: corexy` | Enables belt comparison analysis, CoreXY-specific advice |
| `kinematics: cartesian` | Skips belt comparison, adjusts Y-axis expectations for bed mass |
| `accelerometer.type: LIS2DW` | Warns about aliasing above ~100 Hz, explains "lightshow" artifacts |
| `accelerometer.connection: CANBUS` | Notes potential CANBUS noise in spectrograms |
| `probe.type: TAP` | Explains ~125 Hz resonance spike as known TAP artifact |
| `toolhead.mass: heavy` | Expects lower resonance frequencies, may need more aggressive shaping |
| `belts.type` | Context for belt tension recommendations |
| `frame.size: 350` | Larger frames have lower resonance — adjusts expectations |
| `drivers.type: TMC5160` | Higher current capability — can handle more aggressive acceleration |

## Creating a Profile Interactively

When no profile exists and the user wants one, ask these questions in order:

1. "What printer is this?" (name + kinematics type)
2. "What's the frame size?" (build volume)
3. "What accelerometer are you using, and how is it connected?" (type + connection)
4. "Do you have a probe like TAP, Beacon, or BLTouch?"
5. "Anything else notable?" (mods, special toolhead, belt type)

Write the profile to the detected location and confirm.

## References

### Klipper Configuration

- [Klipper Configuration Reference](https://www.klipper3d.org/Config_Reference.html) — Full config reference covering `[printer]`, `[input_shaper]`, `[adxl345]`, `[lis2dw]`, kinematics, and all other sections
- [Klipper Kinematics](https://www.klipper3d.org/Kinematics.html) — Internals and math behind cartesian, CoreXY, delta, and other kinematic systems
- [Klipper Resonance Compensation](https://www.klipper3d.org/Resonance_Compensation.html) — How input shaper filters work, shaper types (ZV, MZV, EI, etc.), and configuration
- [Klipper Measuring Resonances](https://www.klipper3d.org/Measuring_Resonances.html) — ADXL345, LIS2DW, and MPU-9250 accelerometer setup, wiring, and `TEST_RESONANCES` / `SHAPER_CALIBRATE` usage
- [Klipper TMC Drivers](https://www.klipper3d.org/TMC_Drivers.html) — Configuration and tuning for TMC2209, TMC2240, TMC5160, and other Trinamic stepper drivers

### Shake&Tune

- [Klippain Shake&Tune GitHub](https://github.com/Frix-x/klippain-shaketune) — Main repository: installation, macros (`AXES_SHAPER_CALIBRATION`, `CREATE_VIBRATIONS_PROFILE`, `AXES_MAP_CALIBRATION`), and changelog
- [Shake&Tune Documentation Index](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/README.md) — Documentation root covering all calibration workflows
- [Axes Shaper Calibration Docs](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/axes_shaper_calibrations.md) — Graph interpretation guide for input shaper results
- [Vibrations Profile Docs](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/create_vibrations_profile.md) — Toolhead vibration measurement and profile creation
- [Input Shaper Tuning Generalities](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/is_tuning_generalities.md) — General theory and best practices for IS tuning

### Voron Hardware

- [Voron Documentation — Hardware](https://docs.vorondesign.com/hardware.html) — Printer and extruder selection guide covering Voron models
- [Voron-Tap GitHub](https://github.com/VoronDesign/Voron-Tap) — TAP nozzle-based Z-probe: design files, BOM, and installation notes (explains ~125 Hz resonance artifact)
- [Voron-Stealthburner GitHub](https://github.com/VoronDesign/Voron-Stealthburner) — Stealthburner toolhead: design files, CW2 extruder, and hotend compatibility
