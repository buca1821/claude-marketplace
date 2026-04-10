# Connectivity & Offline Handling

## NWPathMonitor (Preferred)

Use `Network` framework — not the old `SCNetworkReachability` or third-party Reachability.

```swift
import Network

@MainActor @Observable
final class ConnectivityMonitor {
    private(set) var isConnected = true
    private(set) var isExpensive = false // Cellular
    private(set) var isConstrained = false // Low Data Mode

    private let monitor = NWPathMonitor()

    func start() {
        monitor.pathUpdateHandler = { [weak self] path in
            Task { @MainActor in
                self?.isConnected = path.status == .satisfied
                self?.isExpensive = path.isExpensive
                self?.isConstrained = path.isConstrained
            }
        }
        monitor.start(queue: .global(qos: .utility))
    }

    func stop() {
        monitor.cancel()
    }

    deinit {
        monitor.cancel()
    }
}
```

## Injecting via Environment

```swift
// Environment key
struct ConnectivityMonitorKey: EnvironmentKey {
    static let defaultValue = ConnectivityMonitor()
}

extension EnvironmentValues {
    var connectivity: ConnectivityMonitor {
        get { self[ConnectivityMonitorKey.self] }
        set { self[ConnectivityMonitorKey.self] = newValue }
    }
}

// In app root
@main
struct MyApp: App {
    @State private var connectivity = ConnectivityMonitor()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.connectivity, connectivity)
                .task { connectivity.start() }
        }
    }
}

// In views
struct MyView: View {
    @Environment(\.connectivity) private var connectivity

    var body: some View {
        if !connectivity.isConnected {
            OfflineBanner()
        }
    }
}
```

## Offline-First Pattern

```swift
@MainActor @Observable
final class ItemListViewModel {
    private(set) var items: [Item] = []
    private(set) var source: DataSource = .cache

    enum DataSource { case cache, network }

    private let apiClient: APIClientProtocol
    private let localStore: LocalStoreProtocol

    func loadItems() async {
        // 1. Show cached data immediately
        items = await localStore.fetchItems()
        source = .cache

        // 2. Try to refresh from network
        do {
            let fresh: [Item] = try await apiClient.request(.get("/items"))
            items = fresh
            source = .network
            await localStore.saveItems(fresh) // Update cache
        } catch {
            // Network failed — cached data is still showing
            // Only show error if cache was empty
            if items.isEmpty {
                // Show error state
            }
        }
    }
}
```

## Queuing Mutations for Sync

```swift
actor PendingMutationQueue {
    private var queue: [PendingMutation] = []

    struct PendingMutation: Codable {
        let endpoint: String
        let method: String
        let body: Data?
        let createdAt: Date
    }

    func enqueue(_ mutation: PendingMutation) {
        queue.append(mutation)
        persist()
    }

    func processAll(using client: APIClientProtocol) async {
        var failed: [PendingMutation] = []
        for mutation in queue {
            do {
                let endpoint = Endpoint(
                    path: mutation.endpoint,
                    method: .init(rawValue: mutation.method) ?? .post,
                    queryItems: nil,
                    body: mutation.body,
                    headers: nil
                )
                _ = try await client.request(endpoint)
            } catch {
                failed.append(mutation) // Retry later
            }
        }
        queue = failed
        persist()
    }

    private func persist() {
        // Save queue to disk for crash recovery
    }
}
```

## Low Data Mode

Respect user's Low Data Mode setting:

```swift
let configuration = URLSessionConfiguration.default
configuration.allowsConstrainedNetworkAccess = false // Respects Low Data Mode

// Or check and adapt:
if connectivity.isConstrained {
    // Load low-res images, skip prefetching
}
```

## Rules

- Use `NWPathMonitor`, not Reachability or `SCNetworkReachability`
- Offline-first: show cached data immediately, refresh in background
- Queue failed mutations for retry when connectivity returns
- Respect `isExpensive` (cellular) and `isConstrained` (Low Data Mode)
- Never block the UI waiting for network — show cached or empty state
