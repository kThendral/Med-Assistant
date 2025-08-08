from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from gemini_helper import query_gemini
from retriever import index_documents, get_similar_doc
from transcriber import transcribe_audio
from pdf_generator import generate_medical_report_pdf, cleanup_old_reports
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize document index
try:
    index_documents()
    logger.info("Document indexing completed successfully")
    # Clean up old reports on startup
    cleanup_old_reports()
except Exception as e:
    logger.error(f"Error indexing documents: {e}")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    # Return a simple favicon response to prevent 404 errors
    return send_from_directory(os.path.join(app.root_path, 'static'), 
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/upload", methods=["POST"])
def upload_audio():
    try:
        if "audio" not in request.files:
            logger.warning("No audio file in request")
            return "No audio file uploaded", 400
        
        audio = request.files["audio"]
        if audio.filename == '':
            logger.warning("Empty filename in request")
            return "No file selected", 400
            
        filepath = "temp_audio.wav"
        audio.save(filepath)
        logger.info(f"Audio file saved: {filepath}")

        # Transcribe audio (doctor-patient conversation)
        conversation = transcribe_audio(filepath)
        logger.info(f"Transcribed conversation: {conversation}")
        
        if not conversation or conversation.strip() == "":
            return "Could not understand the audio. Please try speaking more clearly.", 400
        
        # Get relevant medical document for context
        doc_info = get_similar_doc(conversation)
        logger.info("Retrieved relevant medical document")
        
        # Generate prescription and report with Gemini
        prompt = f"""You are an AI medical assistant analyzing a doctor-patient conversation. Based on the conversation transcript, generate a comprehensive medical prescription and report.

Doctor-Patient Conversation Transcript:
{conversation}

Relevant Medical Knowledge Base:
{doc_info}

Please provide a structured response with the following sections:

## MEDICAL REPORT

**Patient Summary:**
[Brief summary of patient's condition based on the conversation]

**Chief Complaint:**
[Main symptoms/concerns discussed]

**Assessment:**
[Medical assessment and diagnosis]

**Clinical Notes:**
[Additional observations and recommendations]

## PRESCRIPTION

**Medications Prescribed:**
1. [Medicine name] - [Dosage] - [Frequency] - [Duration]
2. [Continue for each medication]

**Dietary Recommendations:**
[Specific dietary advice]

**Lifestyle Modifications:**
[Exercise, habits, precautions]

**Follow-up Instructions:**
[When to return, monitoring requirements]

**Important Notes:**
[Warnings, side effects, emergency contacts]

---
*This is a computer-generated report based on conversation analysis. Please verify all prescriptions with a licensed healthcare provider.*"""

        result = query_gemini(prompt)
        logger.info("Generated prescription and report with Gemini")
        
        # Store conversation and result for PDF generation
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_data = {
            'conversation': conversation,
            'medical_report': result,
            'timestamp': timestamp
        }
        
        # Store session data temporarily (in production, use proper session management)
        session_file = f"temp_session_{timestamp}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Clean up temporary files
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists("temp_converted.wav"):
                os.remove("temp_converted.wav")
            logger.info("Temporary files cleaned up successfully")
        except Exception as cleanup_error:
            logger.warning(f"Could not clean up temporary files: {cleanup_error}")
        
        # Return result with session data for PDF generation
        return jsonify({
            'success': True,
            'report': result,
            'session_id': timestamp
        })
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        # Clean up any temporary files in error case
        try:
            if os.path.exists("temp_audio.wav"):
                os.remove("temp_audio.wav")
            if os.path.exists("temp_converted.wav"):
                os.remove("temp_converted.wav")
            logger.info("Temporary files cleaned up after error")
        except Exception as cleanup_error:
            logger.warning(f"Could not clean up temporary files after error: {cleanup_error}")
        return f"Error processing your request: {str(e)}", 500

@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        patient_name = data.get('patient_name', 'Not Specified')
        doctor_name = data.get('doctor_name', 'Not Specified')
        
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
        
        # Load session data
        session_file = f"temp_session_{session_id}.json"
        if not os.path.exists(session_file):
            return jsonify({'error': 'Session data not found'}), 404
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Generate PDF
        pdf_path = generate_medical_report_pdf(
            session_data['conversation'],
            session_data['medical_report'],
            patient_name,
            doctor_name
        )
        
        # Clean up session file
        try:
            os.remove(session_file)
        except:
            pass
        
        return jsonify({
            'success': True,
            'pdf_path': os.path.basename(pdf_path),
            'message': 'PDF report generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500

@app.route("/download_pdf/<filename>")
def download_pdf(filename):
    try:
        reports_dir = "reports"
        filepath = os.path.join(reports_dir, filename)
        
        if not os.path.exists(filepath):
            return "File not found", 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        return f"Error downloading file: {str(e)}", 500

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
