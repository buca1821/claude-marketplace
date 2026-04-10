# MetricKit — Production Diagnostics

## Overview

MetricKit provides performance metrics and diagnostic reports from real users in production — no third-party SDKs needed.

- **iOS 13+**: Daily metric payloads (aggregated)
- **iOS 14+**: Diagnostic payloads (crash, hang, disk write reports)
- **iOS 15+**: Immediate crash/hang delivery on next launch

## Setup

```swift
import MetricKit

@MainActor @Observable
final class DiagnosticsManager: NSObject, MXMetricManagerSubscriber {
    static let shared = DiagnosticsManager()

    func start() {
        MXMetricManager.shared.add(self)
    }

    // MARK: - MXMetricManagerSubscriber

    nonisolated func didReceive(_ payloads: [MXMetricPayload]) {
        // Daily aggregated performance metrics
        Task { @MainActor in
            for payload in payloads {
                processMetrics(payload)
            }
        }
    }

    nonisolated func didReceive(_ payloads: [MXDiagnosticPayload]) {
        // Crash, hang, and disk write reports
        Task { @MainActor in
            for payload in payloads {
                processDiagnostics(payload)
            }
        }
    }
}
```

## Metrics Available

### Launch Time
```swift
private func processMetrics(_ payload: MXMetricPayload) {
    // App launch
    if let launch = payload.applicationLaunchMetrics {
        let coldLaunch = launch.histogrammedTimeToFirstDraw
        let resumeTime = launch.histogrammedApplicationResumeTime
        Logger.diagnostics.notice("Cold launch p50: \(coldLaunch.bucketEnumerator)")
    }

    // Responsiveness (hangs)
    if let responsiveness = payload.applicationResponsivenessMetrics {
        let hangTime = responsiveness.histogrammedApplicationHangTime
        Logger.diagnostics.notice("Hang time distribution: \(hangTime.bucketEnumerator)")
    }

    // Memory
    if let memory = payload.memoryMetrics {
        let peak = memory.peakMemoryUsage
        Logger.diagnostics.notice("Peak memory: \(peak)")
    }

    // Battery
    if let cpu = payload.cpuMetrics {
        Logger.diagnostics.notice("CPU time: \(cpu.cumulativeCPUTime)")
    }

    // Disk I/O
    if let disk = payload.diskIOMetrics {
        Logger.diagnostics.notice("Disk writes: \(disk.cumulativeLogicalWrites)")
    }

    // Animation hitches
    if let animation = payload.animationMetrics {
        let hitchRate = animation.scrollHitchTimeRatio
        Logger.diagnostics.notice("Scroll hitch ratio: \(hitchRate)")
    }
}
```

### Diagnostics (Crashes, Hangs)
```swift
private func processDiagnostics(_ payload: MXDiagnosticPayload) {
    // Crashes
    if let crashes = payload.crashDiagnostics {
        for crash in crashes {
            Logger.diagnostics.fault("Crash: \(crash.applicationVersion)")
            let report = crash.jsonRepresentation()
            storeDiagnostic(report, type: "crash")
        }
    }

    // Hangs (> 250ms on main thread)
    if let hangs = payload.hangDiagnostics {
        for hang in hangs {
            Logger.diagnostics.error("Hang detected: \(hang.hangDuration)")
            let report = hang.jsonRepresentation()
            storeDiagnostic(report, type: "hang")
        }
    }

    // Disk write exceptions
    if let diskWrites = payload.diskWriteExceptionDiagnostics {
        for write in diskWrites {
            Logger.diagnostics.error("Excessive disk write: \(write.totalWritesCaused)")
        }
    }

    // CPU exceptions
    if let cpuExceptions = payload.cpuExceptionDiagnostics {
        for exception in cpuExceptions {
            Logger.diagnostics.error("CPU exception: \(exception.totalCPUTime)")
        }
    }
}
```

## Storing and Forwarding

```swift
private func storeDiagnostic(_ json: Data, type: String) {
    // Option 1: Save to local file for debugging
    let filename = "\(type)-\(Date.now.ISO8601Format()).json"
    let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        .appendingPathComponent("diagnostics/\(filename)")
    try? json.write(to: url)

    // Option 2: Forward to your backend
    // Task { try await apiClient.request(.post("/diagnostics", body: json)) }

    // Option 3: Use Xcode Organizer (automatic — no code needed)
    // Users who opt into sharing diagnostics with developers
    // appear in Xcode → Window → Organizer → Crashes/Metrics
}
```

## Xcode Organizer (Free, No Code)

Without any MetricKit code, Apple automatically collects:
- **Crashes** — symbolicated crash reports from users who opted in
- **Energy** — battery impact reports
- **Disk** — disk write reports
- **Metrics** — launch time, hang rate, memory, scrolling

Access via: Xcode → Window → Organizer → select your app

## What MetricKit Replaces

| Third-Party | MetricKit Equivalent |
|-------------|---------------------|
| Firebase Crashlytics | `MXCrashDiagnostic` + Xcode Organizer |
| Sentry crash reporting | `MXCrashDiagnostic` |
| New Relic performance | `MXMetricPayload` metrics |
| Custom launch tracking | `applicationLaunchMetrics` |
| Custom hang tracking | `applicationResponsivenessMetrics` |

## Limitations

- Metrics are aggregated daily (not real-time)
- Crash diagnostics arrive on next launch (iOS 15+) or next day (iOS 14)
- No user-level attribution (privacy-preserving)
- Call stacks may need symbolication
- Not useful during development — use Instruments instead

## Integration in App

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .task {
                    DiagnosticsManager.shared.start()
                }
        }
    }
}
```

## Rules

- MetricKit is for production — use Instruments/OSLog for development
- Process payloads on background queue, store or forward
- Never block app launch waiting for diagnostic processing
- Xcode Organizer is free and automatic — MetricKit adds custom handling
- Combine with OSLog for complete observability (OSLog for events, MetricKit for trends)
