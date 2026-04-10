# API Client Architecture

## Protocol

```swift
protocol APIClientProtocol: Sendable {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T
    func request(_ endpoint: Endpoint) async throws -> Data
}
```

## Endpoint Definition

```swift
struct Endpoint: Sendable {
    let path: String
    let method: HTTPMethod
    let queryItems: [URLQueryItem]?
    let body: Data?
    let headers: [String: String]?

    enum HTTPMethod: String, Sendable {
        case get = "GET"
        case post = "POST"
        case put = "PUT"
        case patch = "PATCH"
        case delete = "DELETE"
    }
}

// Convenience initializers
extension Endpoint {
    static func get(_ path: String, query: [URLQueryItem]? = nil) -> Endpoint {
        Endpoint(path: path, method: .get, queryItems: query, body: nil, headers: nil)
    }

    static func post(_ path: String, body: some Encodable) throws -> Endpoint {
        let data = try JSONEncoder().encode(body)
        return Endpoint(path: path, method: .post, queryItems: nil, body: data, headers: nil)
    }
}
```

## Implementation

```swift
final class APIClient: APIClientProtocol {
    private let session: URLSession
    private let baseURL: URL
    private let decoder: JSONDecoder
    private let tokenProvider: TokenProviderProtocol

    init(
        baseURL: URL,
        tokenProvider: TokenProviderProtocol,
        session: URLSession = .shared
    ) {
        self.baseURL = baseURL
        self.tokenProvider = tokenProvider
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .iso8601
    }

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let data = try await request(endpoint)
        return try decoder.decode(T.self, from: data)
    }

    func request(_ endpoint: Endpoint) async throws -> Data {
        let urlRequest = try await buildRequest(for: endpoint)
        let (data, response) = try await performWithRetry(urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            return data
        case 401:
            throw APIError.unauthorized
        case 404:
            throw APIError.notFound
        case 400...499:
            throw APIError.clientError(httpResponse.statusCode, data)
        case 500...599:
            throw APIError.serverError(httpResponse.statusCode)
        default:
            throw APIError.unexpectedStatus(httpResponse.statusCode)
        }
    }

    private func buildRequest(for endpoint: Endpoint) async throws -> URLRequest {
        var components = URLComponents(url: baseURL.appendingPathComponent(endpoint.path), resolvingAgainstBaseURL: true)
        components?.queryItems = endpoint.queryItems

        guard let url = components?.url else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.httpBody = endpoint.body

        // Default headers
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        // Auth token
        if let token = try? await tokenProvider.accessToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        // Custom headers
        endpoint.headers?.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }

        return request
    }
}
```

## Retry with Exponential Backoff

```swift
extension APIClient {
    private func performWithRetry(
        _ request: URLRequest,
        maxRetries: Int = 3
    ) async throws -> (Data, URLResponse) {
        var lastError: Error?

        for attempt in 0..<maxRetries {
            do {
                return try await session.data(for: request)
            } catch {
                lastError = error

                // Only retry on transient errors
                guard isRetryable(error), attempt < maxRetries - 1 else {
                    throw error
                }

                // Exponential backoff: 0.5s, 1s, 2s
                let delay = pow(2.0, Double(attempt)) * 0.5
                try await Task.sleep(for: .seconds(delay))
            }
        }

        throw lastError ?? APIError.unknown
    }

    private func isRetryable(_ error: Error) -> Bool {
        if let urlError = error as? URLError {
            switch urlError.code {
            case .timedOut, .networkConnectionLost,
                 .notConnectedToInternet, .cannotConnectToHost:
                return true
            default:
                return false
            }
        }
        return false
    }
}
```

## Error Types

```swift
enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case notFound
    case clientError(Int, Data)
    case serverError(Int)
    case unexpectedStatus(Int)
    case decodingError(Error)
    case unknown

    var errorDescription: String? {
        switch self {
        case .unauthorized: String(localized: "error.unauthorized")
        case .notFound: String(localized: "error.not_found")
        case .serverError: String(localized: "error.server")
        default: String(localized: "error.unknown")
        }
    }
}
```

## Mock for Tests

```swift
final class MockAPIClient: APIClientProtocol {
    var mockData: [String: Data] = [:]
    var mockError: APIError?

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        if let error = mockError { throw error }
        guard let data = mockData[endpoint.path] else {
            throw APIError.notFound
        }
        return try JSONDecoder().decode(T.self, from: data)
    }

    func request(_ endpoint: Endpoint) async throws -> Data {
        if let error = mockError { throw error }
        guard let data = mockData[endpoint.path] else {
            throw APIError.notFound
        }
        return data
    }
}
```

## Usage in ViewModel

```swift
@MainActor @Observable
final class ItemListViewModel {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    private(set) var error: APIError?

    private let apiClient: APIClientProtocol

    init(apiClient: APIClientProtocol) {
        self.apiClient = apiClient
    }

    func loadItems() async {
        isLoading = true
        error = nil
        do {
            items = try await apiClient.request(.get("/items"))
        } catch let apiError as APIError {
            error = apiError
        } catch {
            self.error = .unknown
        }
        isLoading = false
    }
}
```

## Rules

- One `APIClient` instance shared across the app (via DI, not singleton)
- Endpoints are value types — easy to test and compose
- Retry only transient errors with backoff
- Map all HTTP errors to typed `APIError`
- Mock client for tests — never hit real API in unit tests
