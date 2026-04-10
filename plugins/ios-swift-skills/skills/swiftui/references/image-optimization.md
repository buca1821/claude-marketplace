# Image Optimization

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## AsyncImage

```swift
AsyncImage(url: imageURL) { phase in
    switch phase {
    case .empty:
        ProgressView()
    case .success(let image):
        image
            .resizable()
            .aspectRatio(contentMode: .fill)
    case .failure:
        Image(systemName: "photo")
            .foregroundStyle(.secondary)
    @unknown default:
        EmptyView()
    }
}
.frame(width: 200, height: 200)
.clipShape(.rect(cornerRadius: 12))
```

## Image Downsampling (Optional Optimization)

For large images, decode at display size to reduce memory:

```swift
actor ImageDownsampler {
    func downsample(data: Data, to pointSize: CGSize, scale: CGFloat = 1) -> UIImage? {
        let maxDimensionInPixels = max(pointSize.width, pointSize.height) * scale
        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceShouldCacheImmediately: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceThumbnailMaxPixelSize: maxDimensionInPixels
        ]
        guard let source = CGImageSourceCreateWithData(data as CFData, nil),
              let cgImage = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary)
        else { return nil }
        return UIImage(cgImage: cgImage)
    }
}
```

## Caching

Use `NSCache` for in-memory image caching:

```swift
actor ImageCache {
    static let shared = ImageCache()
    private let cache = NSCache<NSString, UIImage>()

    func image(for key: String) -> UIImage? {
        cache.object(forKey: key as NSString)
    }

    func store(_ image: UIImage, for key: String) {
        cache.setObject(image, forKey: key as NSString)
    }
}
```

## SF Symbols

```swift
// Preferred — scales with text
Image(systemName: "heart.fill")
    .font(.title)

// With rendering mode
Image(systemName: "heart.fill")
    .symbolRenderingMode(.multicolor)

// Variable value (iOS 16+)
Image(systemName: "wifi", variableValue: signalStrength)

// Symbol effects (iOS 17+)
Image(systemName: "arrow.down.circle")
    .symbolEffect(.bounce, value: downloadCount)
```

## UIImage Memory

- `UIImage(named:)` — caches in system cache (good for reused assets)
- `UIImage(contentsOfFile:)` — no caching (good for one-time large images)
- `UIImage(data:)` — decodes full image into memory; downsample for large images

## Checklist

- [ ] `AsyncImage` handles all phases (empty, success, failure)
- [ ] Large images downsampled to display size
- [ ] SF Symbols used with `.font()` for automatic scaling
- [ ] `UIImage(data:)` avoided for large images without downsampling
