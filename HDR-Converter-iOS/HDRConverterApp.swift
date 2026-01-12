// HDR Converter iOS App
// A native iOS app that converts SDR videos to HDR/HLG format

// MARK: - Project Structure
// Create a new Xcode project with these settings:
// - Product Name: HDR Converter
// - Interface: SwiftUI
// - Language: Swift
// - Minimum Deployment: iOS 15.0

// Then replace/add the following files:

// ================================
// FILE: HDRConverterApp.swift
// ================================

import SwiftUI

@main
struct HDRConverterApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

// ================================
// FILE: ContentView.swift
// ================================

import SwiftUI
import PhotosUI
import AVFoundation

struct ContentView: View {
    @StateObject private var viewModel = HDRConverterViewModel()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Image(systemName: "film.stack")
                        .font(.system(size: 60))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.purple, .blue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    Text("HDR Converter")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    Text("Convert videos to HDR/HLG")
                        .foregroundColor(.secondary)
                }
                .padding(.top, 40)
                
                Spacer()
                
                // Status Area
                if viewModel.isProcessing {
                    VStack(spacing: 16) {
                        ProgressView(value: viewModel.progress)
                            .progressViewStyle(.linear)
                            .frame(width: 250)
                        
                        Text(viewModel.statusMessage)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                } else if viewModel.isComplete {
                    VStack(spacing: 16) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.green)
                        
                        Text("Conversion Complete!")
                            .font(.headline)
                        
                        Text("Saved to Photos with HDR")
                            .foregroundColor(.secondary)
                        
                        Button("Convert Another") {
                            viewModel.reset()
                        }
                        .buttonStyle(.bordered)
                    }
                } else if let error = viewModel.errorMessage {
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.red)
                        
                        Text("Error")
                            .font(.headline)
                        
                        Text(error)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        
                        Button("Try Again") {
                            viewModel.reset()
                        }
                        .buttonStyle(.bordered)
                    }
                    .padding()
                } else {
                    // Video Picker
                    PhotosPicker(
                        selection: $viewModel.selectedItem,
                        matching: .videos
                    ) {
                        VStack(spacing: 12) {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 50))
                            Text("Select Video")
                                .font(.headline)
                        }
                        .frame(width: 200, height: 150)
                        .background(Color.secondary.opacity(0.1))
                        .cornerRadius(16)
                    }
                    
                    if viewModel.selectedVideoURL != nil {
                        VStack(spacing: 16) {
                            HStack {
                                Image(systemName: "video.fill")
                                Text("Video selected")
                            }
                            .foregroundColor(.green)
                            
                            Button(action: {
                                viewModel.convertToHDR()
                            }) {
                                HStack {
                                    Image(systemName: "wand.and.stars")
                                    Text("Convert to HDR")
                                }
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(width: 220, height: 50)
                                .background(
                                    LinearGradient(
                                        colors: [.purple, .blue],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .cornerRadius(12)
                            }
                        }
                    }
                }
                
                Spacer()
                
                // Footer
                Text("Output saves to Photos with HDR badge")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding(.bottom)
            }
            .padding()
            .navigationBarHidden(true)
        }
    }
}

// ================================
// FILE: HDRConverterViewModel.swift
// ================================

import SwiftUI
import PhotosUI
import AVFoundation
import VideoToolbox

@MainActor
class HDRConverterViewModel: ObservableObject {
    @Published var selectedItem: PhotosPickerItem? {
        didSet {
            loadVideo()
        }
    }
    @Published var selectedVideoURL: URL?
    @Published var isProcessing = false
    @Published var progress: Double = 0
    @Published var statusMessage = ""
    @Published var isComplete = false
    @Published var errorMessage: String?
    
    private var tempInputURL: URL?
    
    func reset() {
        selectedItem = nil
        selectedVideoURL = nil
        isProcessing = false
        progress = 0
        statusMessage = ""
        isComplete = false
        errorMessage = nil
        
        // Clean up temp file
        if let url = tempInputURL {
            try? FileManager.default.removeItem(at: url)
        }
        tempInputURL = nil
    }
    
    private func loadVideo() {
        guard let item = selectedItem else { return }
        
        Task {
            do {
                // Load video data
                guard let data = try await item.loadTransferable(type: Data.self) else {
                    errorMessage = "Could not load video"
                    return
                }
                
                // Save to temp file
                let tempURL = FileManager.default.temporaryDirectory
                    .appendingPathComponent(UUID().uuidString)
                    .appendingPathExtension("mov")
                
                try data.write(to: tempURL)
                tempInputURL = tempURL
                selectedVideoURL = tempURL
                
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
    
    func convertToHDR() {
        guard let inputURL = selectedVideoURL else { return }
        
        isProcessing = true
        statusMessage = "Preparing..."
        progress = 0
        
        Task {
            do {
                let outputURL = try await HDRConverter.convert(
                    inputURL: inputURL,
                    progressHandler: { [weak self] prog, message in
                        Task { @MainActor in
                            self?.progress = prog
                            self?.statusMessage = message
                        }
                    }
                )
                
                // Save to Photos
                statusMessage = "Saving to Photos..."
                try await saveToPhotos(url: outputURL)
                
                // Clean up
                try? FileManager.default.removeItem(at: outputURL)
                
                isComplete = true
                isProcessing = false
                
            } catch {
                errorMessage = error.localizedDescription
                isProcessing = false
            }
        }
    }
    
    private func saveToPhotos(url: URL) async throws {
        try await PHPhotoLibrary.shared().performChanges {
            PHAssetChangeRequest.creationRequestForAssetFromVideo(atFileURL: url)
        }
    }
}

// ================================
// FILE: HDRConverter.swift
// ================================

import AVFoundation
import VideoToolbox
import CoreImage

enum HDRConverterError: Error, LocalizedError {
    case noVideoTrack
    case exportFailed(String)
    case encodingFailed
    
    var errorDescription: String? {
        switch self {
        case .noVideoTrack:
            return "No video track found"
        case .exportFailed(let reason):
            return "Export failed: \(reason)"
        case .encodingFailed:
            return "HDR encoding failed"
        }
    }
}

class HDRConverter {
    
    static func convert(
        inputURL: URL,
        progressHandler: @escaping (Double, String) -> Void
    ) async throws -> URL {
        
        progressHandler(0.1, "Loading video...")
        
        let asset = AVURLAsset(url: inputURL)
        
        guard let videoTrack = try await asset.loadTracks(withMediaType: .video).first else {
            throw HDRConverterError.noVideoTrack
        }
        
        let duration = try await asset.load(.duration)
        let naturalSize = try await videoTrack.load(.naturalSize)
        let preferredTransform = try await videoTrack.load(.preferredTransform)
        
        progressHandler(0.2, "Configuring HDR output...")
        
        // Output URL
        let outputURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("HDR_\(UUID().uuidString).mov")
        
        // Create composition
        let composition = AVMutableComposition()
        
        guard let compositionVideoTrack = composition.addMutableTrack(
            withMediaType: .video,
            preferredTrackID: kCMPersistentTrackID_Invalid
        ) else {
            throw HDRConverterError.encodingFailed
        }
        
        try compositionVideoTrack.insertTimeRange(
            CMTimeRange(start: .zero, duration: duration),
            of: videoTrack,
            at: .zero
        )
        compositionVideoTrack.preferredTransform = preferredTransform
        
        // Add audio if present
        if let audioTrack = try? await asset.loadTracks(withMediaType: .audio).first,
           let compositionAudioTrack = composition.addMutableTrack(
            withMediaType: .audio,
            preferredTrackID: kCMPersistentTrackID_Invalid
           ) {
            try compositionAudioTrack.insertTimeRange(
                CMTimeRange(start: .zero, duration: duration),
                of: audioTrack,
                at: .zero
            )
        }
        
        progressHandler(0.3, "Setting up HDR encoding...")
        
        // Video composition for color processing
        let videoComposition = AVMutableVideoComposition(propertiesOf: composition)
        
        // Apply HDR color space
        // BT.2020 with HLG transfer function
        if #available(iOS 15.0, *) {
            videoComposition.colorPrimaries = AVVideoColorPrimaries_ITU_R_2020
            videoComposition.colorTransferFunction = AVVideoTransferFunction_ITU_R_2100_HLG
            videoComposition.colorYCbCrMatrix = AVVideoYCbCrMatrix_ITU_R_2020
        }
        
        // Export with HEVC and HLG
        guard let exportSession = AVAssetExportSession(
            asset: composition,
            presetName: AVAssetExportPresetHEVCHighestQualityWithAlpha
        ) else {
            // Fallback to standard HEVC
            guard let fallbackSession = AVAssetExportSession(
                asset: composition,
                presetName: AVAssetExportPresetHEVCHighestQuality
            ) else {
                throw HDRConverterError.encodingFailed
            }
            return try await performExport(
                session: fallbackSession,
                outputURL: outputURL,
                videoComposition: videoComposition,
                progressHandler: progressHandler
            )
        }
        
        return try await performExport(
            session: exportSession,
            outputURL: outputURL,
            videoComposition: videoComposition,
            progressHandler: progressHandler
        )
    }
    
    private static func performExport(
        session: AVAssetExportSession,
        outputURL: URL,
        videoComposition: AVMutableVideoComposition,
        progressHandler: @escaping (Double, String) -> Void
    ) async throws -> URL {
        
        session.outputURL = outputURL
        session.outputFileType = .mov
        session.videoComposition = videoComposition
        session.shouldOptimizeForNetworkUse = true
        
        // Monitor progress
        let progressTask = Task {
            while !Task.isCancelled {
                let prog = Double(session.progress)
                progressHandler(0.3 + prog * 0.6, "Converting: \(Int(prog * 100))%")
                try await Task.sleep(nanoseconds: 100_000_000) // 0.1s
            }
        }
        
        await session.export()
        progressTask.cancel()
        
        progressHandler(0.95, "Finalizing...")
        
        if let error = session.error {
            throw HDRConverterError.exportFailed(error.localizedDescription)
        }
        
        guard session.status == .completed else {
            throw HDRConverterError.exportFailed("Unknown error")
        }
        
        return outputURL
    }
}

// ================================
// FILE: Info.plist (add these keys)
// ================================
/*
Add to Info.plist:

<key>NSPhotoLibraryUsageDescription</key>
<string>HDR Converter needs access to your photos to select and save videos.</string>

<key>NSPhotoLibraryAddUsageDescription</key>  
<string>HDR Converter needs permission to save converted HDR videos to your Photos.</string>
*/
