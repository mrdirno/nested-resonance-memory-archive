import Foundation
import RealityKit
import Combine

@main
struct HeliosCLI {
    static func main() async {
        let args = ProcessInfo.processInfo.arguments
        
        guard args.count >= 3 else {
            print("Usage: HeliosCLI <input_folder> <output_path>")
            exit(1)
        }
        
        let inputPath = args[1]
        let outputPath = args[2]
        let inputURL = URL(fileURLWithPath: inputPath)
        let outputURL = URL(fileURLWithPath: outputPath)
        
        print("HeliosCLI: Starting Photogrammetry...")
        print("Input: \(inputPath)")
        print("Output: \(outputPath)")
        
        do {
            let session = try PhotogrammetrySession(input: inputURL, configuration: PhotogrammetrySession.Configuration())
            
            // Determine format based on extension
            // RealityKit usually exports USDZ by default, but can do OBJ if path ends in .obj?
            // Actually, we need to be explicit.
            // PhotogrammetrySession.Request.modelFile(url: ..., detail: ...) auto-detects?
            // Documentation says: "The output format is determined by the filename extension."
            // Supported: .usdz, .obj (folder containing .obj and textures)
            
            let request = PhotogrammetrySession.Request.modelFile(url: outputURL, detail: .medium)
            try session.process(requests: [request])
            
            for try await output in session.outputs {
                switch output {
                case .requestProgress(_, let fraction):
                    print("PROGRESS:\(fraction)")
                    fflush(stdout)
                case .processingComplete:
                    print("COMPLETE")
                    fflush(stdout)
                    exit(0)
                case .requestError(_, let error):
                    print("ERROR:\(error)")
                    exit(1)
                case .processingCancelled:
                    print("CANCELLED")
                    exit(1)
                default:
                    break
                }
            }
        } catch {
            print("ERROR:\(error)")
            exit(1)
        }
    }
}