# Swift Charts

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Overview

`import Charts` — available iOS 16+. Declarative chart API using marks.

## Core Pattern

```swift
import Charts

struct SalesChart: View {
    let data: [SalesData]

    var body: some View {
        Chart(data) { item in
            BarMark(
                x: .value(String(localized: "chart.month"), item.month),
                y: .value(String(localized: "chart.revenue"), item.revenue)
            )
            .foregroundStyle(by: .value(String(localized: "chart.category"), item.category))
        }
    }
}
```

## Chart Types

| Mark | Use Case |
|------|----------|
| `BarMark` | Categorical comparisons |
| `LineMark` | Trends over time |
| `AreaMark` | Volume/cumulative trends |
| `PointMark` | Scatter plots, data points |
| `RectangleMark` | Heatmaps |
| `RuleMark` | Reference lines, thresholds |
| `SectorMark` | Pie/donut charts (iOS 17+) |

## Combining Marks

```swift
Chart(data) { item in
    LineMark(
        x: .value("Date", item.date),
        y: .value("Value", item.value)
    )
    .interpolationMethod(.catmullRom)

    PointMark(
        x: .value("Date", item.date),
        y: .value("Value", item.value)
    )

    // Reference line
    RuleMark(y: .value("Average", average))
        .foregroundStyle(.secondary)
        .lineStyle(StrokeStyle(dash: [5, 5]))
}
```

## Axes

```swift
Chart { /* marks */ }
    .chartXAxis {
        AxisMarks(values: .stride(by: .month)) { value in
            AxisGridLine()
            AxisValueLabel(format: .dateTime.month(.abbreviated))
        }
    }
    .chartYAxis {
        AxisMarks(position: .leading)
    }
```

## Selection (iOS 17+)

```swift
@State private var selectedDate: Date?

Chart { /* marks */ }
    .chartXSelection(value: $selectedDate)
    .chartOverlay { proxy in
        if let date = selectedDate {
            // Show annotation at selected point
        }
    }
```

## Annotations

```swift
BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
    .annotation(position: .top) {
        Text("\(item.sales)")
            .font(.caption)
    }
```

## Donut Chart (iOS 17+)

```swift
Chart(categories) { category in
    SectorMark(
        angle: .value("Amount", category.amount),
        innerRadius: .ratio(0.6),
        angularInset: 1
    )
    .foregroundStyle(by: .value("Category", category.name))
    .cornerRadius(4)
}
```

## Chart3D (iOS 26+)

```swift
Chart3D(data) { item in
    BarMark3D(
        x: .value("X", item.x),
        y: .value("Y", item.y),
        z: .value("Z", item.z)
    )
}
```

## Best Practices

- Keep charts simple — max 5-7 categories for readability
- Use `.foregroundStyle(by:)` for automatic color coding
- Add accessibility labels (see `charts-accessibility.md`)
- Animate data changes with `.animation(_:value:)`
- Use `ChartProxy` for custom interactions in `chartOverlay`

## Checklist

- [ ] `import Charts` present in file
- [ ] Data model conforms to `Identifiable`
- [ ] Plottable values use `.value()` with localized labels
- [ ] Axes customized for readability
- [ ] Accessibility labels provided
