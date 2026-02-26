# File Detection Patterns

Shake Tune outputs PNGs and raw data files with predictable naming conventions. Use these patterns to detect which tests are available in a results directory.

## PNG Filename Patterns

| Test Type | Glob Pattern | Example Filename |
|-----------|-------------|-----------------|
| Belt Comparison | `**/beltscomparison_*.png` | `beltscomparison_20250215_143022.png` |
| Input Shaper (X) | `**/inputshaper_*_x.png` | `inputshaper_20250215_150033_x.png` |
| Input Shaper (Y) | `**/inputshaper_*_y.png` | `inputshaper_20250215_150033_y.png` |
| Vibration Profile | `**/vibrations_profile_*.png` | `vibrations_profile_20250215_160044.png` |
| Axes Map | `**/axesmap_*.png` | `axesmap_20250215_170055.png` |
| Excitation | `**/staticfreq_*.png` | `staticfreq_20250215_180066.png` |

## Timestamp Format

- Format: `YYYYMMDD_HHMMSS`
- Tests run in the same session share the same timestamp (or timestamps within a few minutes)
- Use timestamps to group results into sessions for comparison

## Raw Data Files

Shake Tune also produces `.stdata` and `.csv` files alongside PNGs. These contain the raw accelerometer data but require Python decompression to read. **Focus on PNGs** — Claude can read these natively via multimodal vision.

| Data Pattern | Associated Test |
|-------------|----------------|
| `**/beltscomparison_*.stdata` | Belt comparison raw data |
| `**/inputshaper_*.stdata` | Input shaper raw data |
| `**/vibrations_*.stdata` | Vibration profile raw data |
| `**/axesmap_*.stdata` | Axes map raw data |

## Common Directory Structures

### Default Shake Tune Output

```
~/printer_data/config/ShakeTune_results/
├── beltscomparison_20250215_143022.png
├── inputshaper_20250215_150033_x.png
├── inputshaper_20250215_150033_y.png
├── vibrations_profile_20250215_160044.png
└── axesmap_20250215_170055.png
```

### Organized by Date

Some users organize results into date subdirectories:

```
~/printer_data/config/ShakeTune_results/
├── 2025-02-15/
│   ├── beltscomparison_20250215_143022.png
│   └── inputshaper_20250215_150033_x.png
└── 2025-02-20/
    ├── beltscomparison_20250220_091122.png
    └── inputshaper_20250220_093344_x.png
```

### Archived Results

Users may keep historical results in subdirectories:

```
~/printer_data/config/ShakeTune_results/
├── archive/
│   └── before-belt-change/
│       └── beltscomparison_20250101_120000.png
├── beltscomparison_20250215_143022.png
└── ...
```

## Detection Strategy

1. **Start with the user-provided directory** (or ask for it)
2. **Glob recursively** for each PNG pattern to find all available tests
3. **Group by timestamp** to identify sessions (timestamps within 5 minutes = same session)
4. **Sort by date** descending — most recent session first
5. **Report** what was found before proceeding to analysis

## Session Grouping Logic

```
For each PNG found:
  1. Extract timestamp from filename (YYYYMMDD_HHMMSS)
  2. Convert to datetime
  3. Group files where timestamps differ by < 5 minutes
  4. Label each group as a session: "Session YYYY-MM-DD HH:MM"
```

## References

- [Frix-x/klippain-shaketune — GitHub Repository](https://github.com/Frix-x/klippain-shaketune) — Source of file naming conventions and output patterns; the plugin generates all PNG and `.stdata` filenames documented above
- [Shake&Tune Docs Directory](https://github.com/Frix-x/klippain-shaketune/tree/main/docs) — Full documentation index covering each macro, CLI usage, and general IS tuning concepts
- [Shake&Tune: Axes Shaper Calibration Docs](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/axes_shaper_calibrations.md) — Documents the `AXES_SHAPER_CALIBRATION` macro that produces `inputshaper_*_x.png` and `inputshaper_*_y.png` output files
- [Shake&Tune: Belt Comparison Docs](https://github.com/Frix-x/klippain-shaketune/blob/main/docs/macros/compare_belts_responses.md) — Documents the `COMPARE_BELTS_RESPONSES` macro that produces `beltscomparison_*.png` output files
- [Measuring Resonances — Klipper Documentation](https://www.klipper3d.org/Measuring_Resonances.html) — Official Klipper docs on accelerometer setup and resonance data collection; context for the raw `.csv` data that Shake&Tune builds upon
