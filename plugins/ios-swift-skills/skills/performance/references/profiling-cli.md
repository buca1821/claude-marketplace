# CLI-Based Performance Profiling with xctrace

Profile apps from the command line without opening Instruments.

## Record Time Profiler

### Attach to Running Process

```bash
# Get the PID
pgrep -x "SnapGPX"

# Record for 60 seconds
xcrun xctrace record \
    --template 'Time Profiler' \
    --time-limit 60s \
    --output /tmp/SnapGPX.trace \
    --attach <pid>
```

### Launch and Record

```bash
xcrun xctrace record \
    --template 'Time Profiler' \
    --time-limit 60s \
    --output /tmp/SnapGPX.trace \
    --launch -- /path/to/App.app/Contents/MacOS/App
```

### iOS Simulator Profiling

```bash
# Get simulator UDID
xcrun simctl list devices | grep Booted

# Record on simulator
xcrun xctrace record \
    --template 'Time Profiler' \
    --device <simulator-udid> \
    --time-limit 60s \
    --output /tmp/SnapGPX-iOS.trace \
    --launch -- com.snapgpx.app
```

## Export and Analyze

### List Available Schemas

```bash
xcrun xctrace export --input /tmp/SnapGPX.trace --toc
```

### Export Time Profile Data

```bash
xcrun xctrace export \
    --input /tmp/SnapGPX.trace \
    --xpath '/trace-toc/run/data/table[@schema="time-profile"]' \
    --output /tmp/time-profile.xml
```

## Symbolication

### Get Load Address

```bash
# While app is running
vmmap <pid> | grep "__TEXT"
```

### Symbolicate Addresses

```bash
atos -o /path/to/App.app/Contents/MacOS/App -l 0x100000000 <address>
```

## Available Templates

```bash
xcrun xctrace list templates
```

| Template | Use Case |
|----------|----------|
| `Time Profiler` | CPU sampling — find hot code paths |
| `Allocations` | Memory allocation tracking |
| `Leaks` | Memory leak detection |
| `Animation Hitches` | UI frame drops and stutters |
| `App Launch` | Launch time analysis |
| `System Trace` | System-level activity |
| `SwiftUI` | SwiftUI view body evaluations |

## Common Commands

| Task | Command |
|------|---------|
| List templates | `xcrun xctrace list templates` |
| List devices | `xcrun xctrace list devices` |
| Get PID | `pgrep -x "AppName"` |
| Get load address | `vmmap <pid> \| grep __TEXT` |
| Symbolicate | `atos -o <binary> -l <load-addr> <address>` |

## Quick Profiling Script

```bash
#!/bin/bash
set -e

APP_NAME="${1:?Usage: $0 <app-name> [duration] [output]}"
DURATION="${2:-60}"
OUTPUT="${3:-/tmp/$APP_NAME.trace}"

PID=$(pgrep -x "$APP_NAME" || true)

if [ -n "$PID" ]; then
    echo "Attaching to $APP_NAME (PID: $PID) for ${DURATION}s..."
    xcrun xctrace record \
        --template 'Time Profiler' \
        --time-limit "${DURATION}s" \
        --output "$OUTPUT" \
        --attach "$PID"
else
    echo "App not running. Start $APP_NAME first."
    exit 1
fi

echo "Trace saved: $OUTPUT"
echo "Analyze: xcrun xctrace export --input $OUTPUT --toc"
```

## Gotchas

- **ASLR**: Runtime load address changes each launch — get it from `vmmap` while running
- **Build mismatch**: Symbols must match the exact build that was profiled
- **Idle time**: Profiling an idle app produces empty data — trigger the slow path during capture
- **Permissions**: Some operations may need `sudo`
- **Capture duration**: If stacks are empty, capture longer
