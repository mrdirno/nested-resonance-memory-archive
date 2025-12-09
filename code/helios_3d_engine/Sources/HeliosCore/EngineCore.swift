import Foundation
import RealityKit
import Combine

public class EngineCore {
    public init() {}
    
    /// Processes a folder of images into a USDZ model using RealityKit's PhotogrammetrySession.
    /// - Parameters:
    ///   - inputFolder: URL to the folder containing input images.
    ///   - outputFile: URL where the resulting USDZ file should be saved.
    ///   - progressHandler: Closure to report progress (0.0 to 1.0).
    @MainActor
    public func processPhotogrammetry(inputFolder: URL, outputFile: URL, progressHandler: @escaping (Double) -> Void) async throws {
        
        // 1. Initialize Session
        let session = try PhotogrammetrySession(input: inputFolder, configuration: PhotogrammetrySession.Configuration())
        
        // 2. Define Request (Model File)
        let request = PhotogrammetrySession.Request.modelFile(url: outputFile, detail: .medium)
        
        // 3. Process Stream
        try session.process(requests: [request])
        
        // 4. Observe Outputs
        for try await output in session.outputs {
            switch output {
            case .processingComplete:
                print("Processing Complete")
            case .requestError(let request, let error):
                print("Request Error: \(request) - \(error)")
                throw error
            case .requestComplete(let request, let result):
                print("Request Complete: \(request)")
                // Result handle?
            case .requestProgress(_, let fraction):
                progressHandler(fraction)
            case .inputComplete:
                print("Input Complete")
            case .invalidSample(let id, let reason):
                print("Invalid Sample \(id): \(reason)")
            case .skippedSample(let id):
                print("Skipped Sample \(id)")
            case .automaticDownsampling:
                print("Automatic Downsampling applied")
            case .processingCancelled:
                print("Processing Cancelled")
            @unknown default:
                break
            }
        }
    }
}
