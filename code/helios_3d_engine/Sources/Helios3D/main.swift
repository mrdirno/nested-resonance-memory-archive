import SwiftUI
import HeliosCore

@main
struct Helios3DApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.hiddenTitleBar)
    }
}

struct ContentView: View {
    @State private var engineStatus: String = "Ready"
    @State private var isProcessing: Bool = false
    @State private var selectedFolder: URL?
    @State private var generatedModelURL: URL?
    @State private var meshStats: String = "No Model Loaded"
    @State private var voxelResolution: Double = 64.0
    
    var body: some View {
        HSplitView {
            // Sidebar
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    Image(systemName: "cube.transparent.fill")
                        .foregroundStyle(.indigo)
                    Text("Helios 3D")
                        .font(.headline)
                }
                .padding(.top)
                
                Divider()
                
                // Input
                Group {
                    Text("Input")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    Button("Select Image Folder") { selectFolder() }
                        .controlSize(.large)
                        .buttonStyle(.bordered)
                    if let folder = selectedFolder {
                        Text(folder.lastPathComponent)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .truncationMode(.middle)
                    }
                }
                
                Divider()
                
                // Photogrammetry
                Group {
                    Text("Generation")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    Button(action: startPhotogrammetry) {
                        HStack {
                            if isProcessing { ProgressView().controlSize(.small) }
                            Text(isProcessing ? "Processing..." : "Generate Model")
                        }
                    }
                    .disabled(selectedFolder == nil || isProcessing)
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                }
                
                Divider()
                
                // Optimization
                Group {
                    Text("Optimization")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    
                    VStack(alignment: .leading) {
                        Text("Voxel Resolution: \(Int(voxelResolution))")
                            .font(.caption)
                        Slider(value: $voxelResolution, in: 32...256, step: 32)
                    }
                    
                    Button("Remesh (Voxelize)") {
                        remeshModel()
                    }
                    .disabled(generatedModelURL == nil || isProcessing)
                }
                
                Divider()
                
                // Stats
                Group {
                    Text("Analysis")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    Text(meshStats)
                        .font(.caption)
                        .foregroundStyle(.primary)
                        .textSelection(.enabled)
                }
                
                Spacer()
                Text(engineStatus)
                    .font(.caption2)
                    .foregroundStyle(.gray)
                    .padding(.bottom)
            }
            .padding()
            .frame(minWidth: 220, maxWidth: 300, maxHeight: .infinity)
            .background(Color(nsColor: .controlBackgroundColor))
            
            // Viewport
            ZStack {
                Color(nsColor: .windowBackgroundColor)
                if let modelURL = generatedModelURL {
                    ModelViewer(modelURL: modelURL)
                        .edgesIgnoringSafeArea(.all)
                        .id(modelURL) // Force refresh on URL change
                } else {
                    ContentUnavailableView("No Model Loaded", systemImage: "view.3d", description: Text("Generate or Load a model."))
                }
            }
            .frame(minWidth: 500, maxWidth: .infinity, maxHeight: .infinity)
        }
        .frame(minWidth: 900, minHeight: 600)
    }
    
    func selectFolder() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        if panel.runModal() == .OK {
            selectedFolder = panel.url
            generatedModelURL = nil
            meshStats = "No Model Loaded"
            engineStatus = "Ready"
        }
    }
    
    func startPhotogrammetry() {
        guard let folder = selectedFolder else { return }
        isProcessing = true
        engineStatus = "Scanning..."
        Task {
            do {
                let outputURL = folder.appendingPathComponent("model.usdz")
                let engine = EngineCore()
                try await engine.processPhotogrammetry(inputFolder: folder, outputFile: outputURL) { p in
                    engineStatus = "Processing: \(Int(p * 100))%"
                }
                engineStatus = "Generation Complete."
                updateModel(url: outputURL)
            } catch {
                engineStatus = "Error: \(error.localizedDescription)"
            }
            isProcessing = false
        }
    }
    
    func remeshModel() {
        guard let url = generatedModelURL else { return }
        isProcessing = true
        engineStatus = "Remeshing..."
        let res = Int(voxelResolution)
        
        Task {
            do {
                let outputURL = url.deletingPathExtension().appendingPathExtension("remesh_\(res).usdz")
                let analyzer = try MeshAnalyzer()
                try analyzer.simplify(url: url, outputUrl: outputURL, resolution: res)
                
                engineStatus = "Remeshing Complete."
                updateModel(url: outputURL)
            } catch {
                engineStatus = "Remesh Failed: \(error.localizedDescription)"
            }
            isProcessing = false
        }
    }
    
    func updateModel(url: URL) {
        generatedModelURL = url
        do {
            let analyzer = try MeshAnalyzer()
            let stats = try analyzer.analyze(url: url)
            meshStats = stats.description
        } catch {
            meshStats = "Analysis Failed"
        }
    }
}
