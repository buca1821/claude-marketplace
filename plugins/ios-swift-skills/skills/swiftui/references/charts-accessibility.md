# Charts Accessibility

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Meaningful Labels

Every chart mark should have descriptive accessibility labels:

```swift
BarMark(
    x: .value(String(localized: "chart.month"), item.month),
    y: .value(String(localized: "chart.revenue"), item.revenue)
)
.accessibilityLabel("\(item.month)")
.accessibilityValue(String(localized: "chart.revenue.value \(item.revenue.formatted(.currency(code: "USD")))"))
```

## Audio Graphs

Charts automatically support Audio Graphs for VoiceOver users. Enhance with `AXChartDescriptorRepresentable`:

```swift
struct SalesChart: View {
    let data: [SalesData]

    var body: some View {
        Chart(data) { item in
            LineMark(
                x: .value("Date", item.date),
                y: .value("Sales", item.sales)
            )
        }
        .accessibilityChartDescriptor(SalesChartDescriptor(data: data))
    }
}

struct SalesChartDescriptor: AXChartDescriptorRepresentable {
    let data: [SalesData]

    func makeChartDescriptor() -> AXChartDescriptor {
        let xAxis = AXCategoricalDataAxisDescriptor(
            title: "Month",
            categoryOrder: data.map(\.monthName)
        )
        let yAxis = AXNumericDataAxisDescriptor(
            title: "Sales",
            range: 0...Double(data.map(\.sales).max() ?? 0)
        ) { value in "\(Int(value)) units" }

        let series = AXDataSeriesDescriptor(
            name: "Monthly Sales",
            isContinuous: true,
            dataPoints: data.map { item in
                .init(x: item.monthName, y: Double(item.sales))
            }
        )

        return AXChartDescriptor(
            title: "Sales Overview",
            summary: "Monthly sales data for the current year",
            xAxis: xAxis,
            yAxis: yAxis,
            series: [series]
        )
    }
}
```

## Fallback for Older iOS

```swift
if #available(iOS 16, *) {
    Chart(data) { /* marks */ }
} else {
    // Provide a table or list as accessible fallback
    List(data) { item in
        HStack {
            Text(item.label)
            Spacer()
            Text(item.value.formatted())
        }
    }
}
```

## Checklist

- [ ] Chart marks have `.accessibilityLabel` and `.accessibilityValue`
- [ ] `AXChartDescriptorRepresentable` implemented for complex charts
- [ ] Fallback provided for pre-iOS 16 if needed
- [ ] Chart summary describes the overall trend
