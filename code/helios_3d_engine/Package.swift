// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "Helios3DEngine",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(
            name: "Helios3D",
            targets: ["Helios3D"]),
        .library(
            name: "HeliosCore",
            targets: ["HeliosCore"]),
    ],
    dependencies: [
    ],
    targets: [
        .executableTarget(
            name: "Helios3D",
            dependencies: ["HeliosCore"]),
        .target(
            name: "HeliosCore",
            dependencies: []),
        .testTarget(
            name: "Helios3DTests",
            dependencies: ["Helios3D", "HeliosCore"]),
    ]
)
