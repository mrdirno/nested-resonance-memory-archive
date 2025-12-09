import SwiftUI
import HeliosCore

@main
struct Helios3DApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var engineStatus: String = "Ready"
    @State private var isProcessing: Bool = false
    @State private var selectedFolder: URL?
    @State private var generatedModelURL: URL?
    
    var body: some View {
        HSplitView {
            // Sidebar / Controls
            VStack(alignment: .leading, spacing: 20) {
                Label("Helios 3D", systemImage: "cube.transparent.fill")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding(.top)
                
                Divider()
                
                Group {
                    Text("Input Source")
                        .font(.headline)
                    
                    Button("Select Image Folder") {
                        selectFolder()
                    }
                    .controlSize(.large)
                    
                    if let folder = selectedFolder {
                        Text(folder.path(percentEncoded: false))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
                    }
                }
                
                Divider()
                
                Group {
                    Text("Processing")
                        .font(.headline)
                    
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
                }
                
                Spacer()
                
                Text(engineStatus)
                    .font(.caption)
                    .foregroundStyle(.gray)
                    .padding(.bottom)
            }
            .padding()
            .frame(minWidth: 250, maxWidth: 350, maxHeight: .infinity)
            .background(Color(nsColor: .controlBackgroundColor))
            
            // Main Content / 3D Viewer
            ZStack {
                Color(nsColor: .windowBackgroundColor)
                
                if let modelURL = generatedModelURL {
                    ModelViewer(modelURL: modelURL)
                } else {
                    VStack {
                        Image(systemName: "view.3d")
                            .font(.system(size: 50))
                            .foregroundStyle(.tertiary)
                        Text("No Model Loaded")
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .frame(minWidth: 500, maxWidth: .infinity, maxHeight: .infinity)
        }
        .frame(minWidth: 800, minHeight: 600)
    }
    
    func selectFolder() {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        if panel.runModal() == .OK {
            selectedFolder = panel.url
            generatedModelURL = nil // Reset previous model
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
                try await engine.processPhotogrammetry(inputFolder: folder, outputFile: outputURL) { progress in
                   engineStatus = "Processing: \(Int(progress * 100))%"
                }
                engineStatus = "Success! Loaded model."
                generatedModelURL = outputURL
            } catch {
                engineStatus = "Error: \(error.localizedDescription)"
            }
            isProcessing = false
        }
    }
}