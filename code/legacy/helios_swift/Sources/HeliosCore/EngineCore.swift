import Foundation
import RealityKit
import Combine

public class EngineCore {
    public init() {}
    
    @MainActor
    public func processPhotogrammetry(inputFolder: URL, outputFile: URL, progressHandler: @escaping (Double) -> Void) async throws {
        let session = try PhotogrammetrySession(input: inputFolder, configuration: PhotogrammetrySession.Configuration())
        let request = PhotogrammetrySession.Request.modelFile(url: outputFile, detail: .medium)
        try session.process(requests: [request])
        
        for try await output in session.outputs {
            switch output {
            case .requestProgress(_, let fraction):
                progressHandler(fraction)
            case .processingComplete:
                print("Processing Complete")
            default:
                break
            }
        }
    }
}
