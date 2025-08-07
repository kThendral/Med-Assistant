// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    const recordBtn = document.getElementById("recordBtn");
    const statusDiv = document.getElementById("status");
    const resultDiv = document.getElementById("result");
    
    if (!recordBtn) {
        console.error("Record button not found!");
        return;
    }
    
    recordBtn.onclick = async () => {
        if (isRecording) {
            return; // Prevent multiple recordings
        }
        
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error("Audio recording not supported in this browser");
            }
            
            statusDiv.textContent = "Starting recording...";
            recordBtn.disabled = true;
            audioChunks = []; // Reset chunks
            
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };
            
            mediaRecorder.onstop = async () => {
                isRecording = false;
                statusDiv.textContent = "Processing audio...";
                
                try {
                    const blob = new Blob(audioChunks, { type: "audio/wav" });
                    const formData = new FormData();
                    formData.append("audio", blob, "recording.wav");
                    
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
                    recordBtn.textContent = "🎤 Record Audio (5 sec)";
                    
                    // Stop all tracks to release microphone
                    stream.getTracks().forEach(track => track.stop());
                }
            };
            
            mediaRecorder.onerror = (e) => {
                console.error("MediaRecorder error:", e);
                statusDiv.textContent = "Recording error occurred";
                recordBtn.disabled = false;
                isRecording = false;
            };
            
            mediaRecorder.start();
            isRecording = true;
            recordBtn.textContent = "🔴 Recording...";
            statusDiv.textContent = "Recording in progress...";
            
            // Auto stop after 5 seconds
            setTimeout(() => {
                if (mediaRecorder && mediaRecorder.state === "recording") {
                    mediaRecorder.stop();
                }
            }, 5000);
            
        } catch (error) {
            console.error("Error starting recording:", error);
            statusDiv.textContent = `Error: ${error.message}`;
            recordBtn.disabled = false;
            isRecording = false;
        }
    };
});
