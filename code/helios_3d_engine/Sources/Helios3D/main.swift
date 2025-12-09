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
    var body: some View {
        VStack {
            Image(systemName: "cube.transparent")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("Helios 3D Engine")
                .font(.largeTitle)
            Text("Native macOS 3D Generation Tool")
                .font(.subheadline)
            
            Divider()
            
            Button("Initialize Engine") {
                let engine = EngineCore()
                print(engine.status())
            }
        }
        .padding()
        .frame(minWidth: 800, minHeight: 600)
    }
}
