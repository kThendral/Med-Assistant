// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingStream = null;
    let recordingTimeout = null;
    
    const recordBtn = document.getElementById("recordBtn");
    const statusDiv = document.getElementById("status");
    const resultDiv = document.getElementById("result");
    
    if (!recordBtn) {
        console.error("Record button not found!");
        return;
    }
    
    // Function to stop recording
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
        if (recordingTimeout) {
            clearTimeout(recordingTimeout);
            recordingTimeout = null;
        }
    }
    
    recordBtn.onclick = async () => {
        // If currently recording, stop the recording
        if (isRecording) {
            stopRecording();
            return;
        }
        
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error("Audio recording not supported in this browser");
            }
            
            statusDiv.textContent = "Starting recording...";
            recordBtn.disabled = true;
            audioChunks = []; // Reset chunks
            
            recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Try to use a more compatible audio format
            let mimeType = 'audio/webm';
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                mimeType = 'audio/webm;codecs=opus';
            } else if (MediaRecorder.isTypeSupported('audio/wav')) {
                mimeType = 'audio/wav';
            } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
                mimeType = 'audio/ogg';
            }
            
            console.log(`Using MIME type: ${mimeType}`);
            mediaRecorder = new MediaRecorder(recordingStream, { mimeType: mimeType });
            
            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };
            
            mediaRecorder.onstop = async () => {
                isRecording = false;
                statusDiv.textContent = "Processing audio...";
                
                try {
                    const blob = new Blob(audioChunks, { type: mimeType });
                    const formData = new FormData();
                    
                    // Use appropriate file extension based on MIME type
                    let fileName = "recording.webm";
                    if (mimeType.includes('wav')) {
                        fileName = "recording.wav";
                    } else if (mimeType.includes('ogg')) {
                        fileName = "recording.ogg";
                    }
                    
                    formData.append("audio", blob, fileName);
                    console.log(`Sending audio file: ${fileName} with type: ${mimeType}`);
                    
                    const response = await fetch("/upload", {
                        method: "POST",
                        body: formData,
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    
                    const result = await response.text();
                    resultDiv.innerHTML = result.replace(/\n/g, '<br>');
                    statusDiv.textContent = "Analysis complete!";
                } catch (error) {
                    console.error("Upload error:", error);
                    resultDiv.textContent = `Error: ${error.message}`;
                    statusDiv.textContent = "Error occurred";
                } finally {
                    recordBtn.disabled = false;
                    recordBtn.textContent = "🎤 Record Audio";
                    
                    // Stop all tracks to release microphone
                    if (recordingStream) {
                        recordingStream.getTracks().forEach(track => track.stop());
                        recordingStream = null;
                    }
                }
            };
            
            mediaRecorder.onerror = (e) => {
                console.error("MediaRecorder error:", e);
                statusDiv.textContent = "Recording error occurred";
                recordBtn.disabled = false;
                recordBtn.textContent = "🎤 Record Audio";
                isRecording = false;
                
                // Clean up stream
                if (recordingStream) {
                    recordingStream.getTracks().forEach(track => track.stop());
                    recordingStream = null;
                }
            };
            
            mediaRecorder.start();
            isRecording = true;
            recordBtn.disabled = false; // Enable button so it can be used to stop
            recordBtn.textContent = "⏹️ Stop Recording";
            statusDiv.textContent = "Recording... Click stop to finish";
            
        } catch (error) {
            console.error("Error starting recording:", error);
            statusDiv.textContent = `Error: ${error.message}`;
            recordBtn.disabled = false;
            recordBtn.textContent = "🎤 Record Audio";
            isRecording = false;
            
            // Clean up stream in case of error
            if (recordingStream) {
                recordingStream.getTracks().forEach(track => track.stop());
                recordingStream = null;
            }
        }
    };
    
    // Optional: Add keyboard shortcut to stop recording (Escape key)
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && isRecording) {
            console.log("Recording stopped by Escape key");
            stopRecording();
        }
    });
});
