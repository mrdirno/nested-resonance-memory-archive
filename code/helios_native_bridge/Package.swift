// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "HeliosNativeBridge",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "HeliosCLI", targets: ["HeliosCLI"])
    ],
    targets: [
        .executableTarget(name: "HeliosCLI", dependencies: [])
    ]
)
