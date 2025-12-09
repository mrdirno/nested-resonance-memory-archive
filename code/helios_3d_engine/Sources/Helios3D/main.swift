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
                
                // Input Section
                Group {
                    Text("Input")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    
                    Button("Select Image Folder") {
                        selectFolder()
                    }
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
                
                // Process Section
                Group {
                    Text("Generation")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    
                    Button(action: startPhotogrammetry) {
                        HStack {
                            if isProcessing {
                                ProgressView().controlSize(.small)
                            }
                            Text(isProcessing ? "Processing..." : "Generate Model")
                        }
                    }
                    .disabled(selectedFolder == nil || isProcessing)
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                }
                
                Divider()
                
                // Stats Section
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
                
                // Footer
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
                } else {
                    ContentUnavailableView("No Model Loaded", systemImage: "view.3d", description: Text("Generate a model to view it here."))
                }
            }
            .frame(minWidth: 500, maxWidth: .infinity, maxHeight: .infinity)
        }
        .frame(minWidth: 800, minHeight: 600)
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
        engineStatus = "Initializing Session..."
        
        Task {
            do {
                let outputURL = folder.appendingPathComponent("model.usdz")
                let engine = EngineCore()
                try await engine.processPhotogrammetry(inputFolder: folder, outputFile: outputURL) { p in
                    engineStatus = "Processing: \(Int(p * 100))%"
                }
                engineStatus = "Generation Complete."
                generatedModelURL = outputURL
                
                // Run Analysis
                do {
                    let analyzer = try MeshAnalyzer()
                    let stats = try analyzer.analyze(url: outputURL)
                    meshStats = stats.description
                } catch {
                    meshStats = "Analysis Failed: \(error.localizedDescription)"
                }
                
            } catch {
                engineStatus = "Error: \(error.localizedDescription)"
            }
            isProcessing = false
        }
    }
}
