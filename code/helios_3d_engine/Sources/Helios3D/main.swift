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
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "cube.transparent.fill")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 100, height: 100)
                .foregroundStyle(.indigo)
            
            Text("Helios 3D Engine")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Divider()
            
            HStack {
                Button("Select Image Folder") {
                    let panel = NSOpenPanel()
                    panel.allowsMultipleSelection = false
                    panel.canChooseDirectories = true
                    panel.canChooseFiles = false
                    if panel.runModal() == .OK {
                        selectedFolder = panel.url
                    }
                }
                
                if let folder = selectedFolder {
                    Text(folder.lastPathComponent)
                        .foregroundStyle(.secondary)
                } else {
                    Text("No folder selected")
                        .foregroundStyle(.secondary)
                }
            }
            
            Button(action: startPhotogrammetry) {
                HStack {
                    if isProcessing {
                        ProgressView().controlSize(.small)
                    }
                    Text(isProcessing ? "Processing..." : "Generate 3D Model")
                }
            }
            .disabled(selectedFolder == nil || isProcessing)
            .buttonStyle(.borderedProminent)
            
            Text(engineStatus)
                .font(.caption)
                .foregroundStyle(.gray)
        }
        .padding()
        .frame(minWidth: 600, minHeight: 400)
    }
    
    func startPhotogrammetry() {
        guard let folder = selectedFolder else { return }
        isProcessing = true
        engineStatus = "Initializing Photogrammetry Session..."
        
        // Async call to Core
        Task {
            do {
                let outputURL = folder.appendingPathComponent("model.usdz")
                let engine = EngineCore()
                try await engine.processPhotogrammetry(inputFolder: folder, outputFile: outputURL) { progress in
                   engineStatus = "Processing: \(Int(progress * 100))%"
                }
                engineStatus = "Success! Saved to \(outputURL.lastPathComponent)"
            } catch {
                engineStatus = "Error: \(error.localizedDescription)"
            }
            isProcessing = false
        }
    }
}
