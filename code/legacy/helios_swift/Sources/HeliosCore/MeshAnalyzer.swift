import Foundation
import Metal
import ModelIO
import MetalKit

public class MeshAnalyzer {
    let device: MTLDevice
    
    public struct MeshStats {
        public var vertexCount: Int
        public var triangleCount: Int
        public var boundingBox: (min: SIMD3<Float>, max: SIMD3<Float>)
        public var description: String {
            let width = boundingBox.max.x - boundingBox.min.x
            let height = boundingBox.max.y - boundingBox.min.y
            let depth = boundingBox.max.z - boundingBox.min.z
            return """
            Vertices: \(vertexCount)
            Triangles: \(triangleCount)
            Dimensions: \(String(format: "%.2f", width))m x \(String(format: "%.2f", height))m x \(String(format: "%.2f", depth))m
            """
        }
    }
    
    public init() throws {
        guard let device = MTLCreateSystemDefaultDevice() else {
            throw NSError(domain: "Helios3D", code: 1, userInfo: [NSLocalizedDescriptionKey: "Metal Device Init Failed"])
        }
        self.device = device
    }
    
    public func analyze(url: URL) throws -> MeshStats {
        let allocator = MTKMeshBufferAllocator(device: device)
        let asset = MDLAsset(url: url, vertexDescriptor: nil, bufferAllocator: allocator)
        
        var vertexCount = 0
        var triangleCount = 0
        var minBounds = SIMD3<Float>(Float.greatestFiniteMagnitude, Float.greatestFiniteMagnitude, Float.greatestFiniteMagnitude)
        var maxBounds = SIMD3<Float>(-Float.greatestFiniteMagnitude, -Float.greatestFiniteMagnitude, -Float.greatestFiniteMagnitude)
        
        for object in asset.childObjects(of: MDLMesh.self) {
            guard let mesh = object as? MDLMesh else { continue }
            vertexCount += mesh.vertexCount
            for submesh in mesh.submeshes as? [MDLSubmesh] ?? [] {
                if submesh.geometryType == .triangles {
                    triangleCount += submesh.indexCount / 3
                }
            }
            let bounds = mesh.boundingBox
            minBounds = simd_min(minBounds, SIMD3<Float>(bounds.minBounds))
            maxBounds = simd_max(maxBounds, SIMD3<Float>(bounds.maxBounds))
        }
        
        return MeshStats(vertexCount: vertexCount, triangleCount: triangleCount, boundingBox: (minBounds, maxBounds))
    }
    
    public func simplify(url: URL, outputUrl: URL, resolution: Int) throws {
        let allocator = MTKMeshBufferAllocator(device: device)
        let asset = MDLAsset(url: url, vertexDescriptor: nil, bufferAllocator: allocator)
        let voxelArray = MDLVoxelArray(asset: asset, divisions: Int32(resolution), patchRadius: 0.0)
        
        if let newMesh = voxelArray.mesh(using: allocator) {
            let newAsset = MDLAsset(bufferAllocator: allocator)
            newAsset.add(newMesh)
            try newAsset.export(to: outputUrl)
        } else {
            try asset.export(to: outputUrl)
        }
    }
}
