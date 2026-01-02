import SwiftUI
import RealityKit

struct ModelViewer: View {
    let modelURL: URL
    @State private var rootEntity: Entity?
    @State private var rotation: Double = 0.0
    
    var body: some View {
        RealityView { content in
            let anchor = AnchorEntity()
            content.add(anchor)
            Task {
                if let model = try? await ModelEntity(contentsOf: modelURL) {
                    let bounds = model.visualBounds(relativeTo: nil)
                    let maxDim = max(bounds.extents.x, max(bounds.extents.y, bounds.extents.z))
                    let scale = Float(0.2) / maxDim 
                    model.scale = SIMD3<Float>(repeating: scale)
                    model.position = -bounds.center * scale
                    anchor.addChild(model)
                    
                    let light = DirectionalLight()
                    light.light.intensity = 1000
                    light.look(at: .zero, from: [1, 1, 1], relativeTo: nil)
                    anchor.addChild(light)
                    
                    DispatchQueue.main.async { self.rootEntity = anchor }
                }
            }
        } update: { content in
            if let root = rootEntity {
                root.orientation = simd_quatf(angle: Float(rotation), axis: [0, 1, 0])
            }
        }
        .gesture(DragGesture().onChanged { value in rotation += Double(value.translation.width) * 0.01 })
        .frame(minWidth: 400, minHeight: 400)
        .background(Color.black.opacity(0.1))
    }
}
