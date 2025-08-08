// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingStream = null;
    let recordingTimeout = null;
    let currentSessionId = null;
    
    const recordBtn = document.getElementById("recordBtn");
    const statusDiv = document.getElementById("status");
    const resultDiv = document.getElementById("result");
    const pdfSection = document.getElementById("pdf-section");
    const generatePdfBtn = document.getElementById("generatePdfBtn");
    const patientNameInput = document.getElementById("patientName");
    const doctorNameInput = document.getElementById("doctorName");
    const pdfStatusDiv = document.getElementById("pdf-status");
    
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
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        resultDiv.innerHTML = result.report.replace(/\n/g, '<br>');
                        statusDiv.textContent = "Analysis complete!";
                        
                        // Store session ID and show PDF generation section
                        currentSessionId = result.session_id;
                        pdfSection.style.display = 'block';
                        pdfStatusDiv.textContent = '';
                    } else {
                        throw new Error('Server returned error response');
                    }
                } catch (error) {
                    console.error("Upload error:", error);
                    resultDiv.textContent = `Error: ${error.message}`;
                    statusDiv.textContent = "Error occurred";
                } finally {
                    recordBtn.disabled = false;
                    recordBtn.textContent = "🎤 Record Conversation";
                    
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
                recordBtn.textContent = "🎤 Record Conversation";
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
            recordBtn.textContent = "🎤 Record Conversation";
            isRecording = false;
            
            // Clean up stream in case of error
            if (recordingStream) {
                recordingStream.getTracks().forEach(track => track.stop());
                recordingStream = null;
            }
        }
    };
    
    // PDF Generation functionality
    generatePdfBtn.onclick = async () => {
        if (!currentSessionId) {
            pdfStatusDiv.textContent = 'Error: No session data available. Please record a conversation first.';
            pdfStatusDiv.style.color = 'red';
            return;
        }
        
        const patientName = patientNameInput.value.trim();
        const doctorName = doctorNameInput.value.trim();
        
        try {
            generatePdfBtn.disabled = true;
            generatePdfBtn.textContent = '⏳ Generating PDF...';
            pdfStatusDiv.textContent = 'Generating PDF report...';
            pdfStatusDiv.style.color = 'blue';
            
            const response = await fetch('/generate_pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    patient_name: patientName,
                    doctor_name: doctorName
                }),
            });
            
            const result = await response.json();
            
            if (result.success) {
                pdfStatusDiv.innerHTML = `
                    <span style="color: green;">✅ PDF generated successfully!</span><br>
                    <a href="/download_pdf/${result.pdf_path}" download class="download-link">
                        📥 Download PDF Report
                    </a>
                `;
            } else {
                throw new Error(result.error || 'Failed to generate PDF');
            }
            
        } catch (error) {
            console.error('PDF generation error:', error);
            pdfStatusDiv.textContent = `Error: ${error.message}`;
            pdfStatusDiv.style.color = 'red';
        } finally {
            generatePdfBtn.disabled = false;
            generatePdfBtn.textContent = '📄 Create PDF Report';
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
