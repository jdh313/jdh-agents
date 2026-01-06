# Time Patterns Reference

Natural language date and time patterns accepted by `doing`.

## Duration Formats (`--took`)

| Format | Example | Meaning |
|--------|---------|---------|
| Minutes | `30m`, `45m` | 30/45 minutes |
| Hours | `1h`, `2h` | 1/2 hours |
| Combined | `1h30m`, `2h15m` | Hours and minutes |
| Decimal | `1.5h` | 1.5 hours |

## Time of Day (`--back`, `--at`)

| Format | Example | Meaning |
|--------|---------|---------|
| 12-hour | `9am`, `2pm`, `11:30am` | Clock time |
| 24-hour | `14:00`, `09:30`, `17:45` | Military time |
| Named | `noon`, `midnight` | Common times |

## Relative Times (`--back`)

| Format | Example | Meaning |
|--------|---------|---------|
| Minutes ago | `30m`, `45 minutes ago` | Relative to now |
| Hours ago | `2h`, `3 hours ago` | Relative to now |
| Days | `yesterday`, `yesterday 3pm` | Previous day |
| Day names | `monday`, `friday 2pm` | Recent weekday |
| Last X | `last monday`, `last week` | Previous occurrence |

## Date Ranges (`--from`)

| Format | Example | Meaning |
|--------|---------|---------|
| Single day | `monday`, `yesterday` | All entries that day |
| Range | `"monday to friday"` | Multi-day range |
| Time range | `"9am to 5pm"` | Time window (any date) |
| Full range | `"monday 9am to friday 5pm"` | Specific window |
| Relative | `"last week"`, `"this month"` | Named periods |

## Common Backdating Scenarios

### Meeting that just ended
```bash
doing done --took 1h team standup @meetings
```

### Morning meeting logged in afternoon
```bash
doing done --back 9am --took 30m standup @meetings
```

### Work block with known times
```bash
doing done --back 2pm --at 4:30pm feature development
```

### Yesterday's forgotten entry
```bash
doing done --back "yesterday 10am" --took 2h client call @client
```

### Last week's entry
```bash
doing done --back "last tuesday 2pm" --took 3h workshop @training
```

## Tips

- **Quotes required** for multi-word times: `--back "yesterday 3pm"`
- **Single words** don't need quotes: `--back 2pm`, `--back yesterday`
- **Relative times** (30m, 2h) backdate from now
- **Clock times** (2pm) assume today unless specified
- **Day names** refer to the most recent occurrence
