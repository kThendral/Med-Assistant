from flask import Flask, render_template, request, jsonify, send_from_directory
from gemini_helper import query_gemini
from retriever import index_documents, get_similar_doc
from transcriber import transcribe_audio
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize document index
try:
    index_documents()
    logger.info("Document indexing completed successfully")
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

        # Transcribe audio
        symptoms = transcribe_audio(filepath)
        logger.info(f"Transcribed symptoms: {symptoms}")
        
        if not symptoms or symptoms.strip() == "":
            return "Could not understand the audio. Please try speaking more clearly.", 400
        
        # Get relevant medical document
        doc_info = get_similar_doc(symptoms)
        logger.info("Retrieved relevant medical document")
        
        # Generate diagnosis with Gemini
        prompt = f"""You are a medical assistant. Based on the patient's symptoms and medical information provided, give a preliminary assessment.

Patient's symptoms: {symptoms}

Relevant medical information:
{doc_info}

Please provide:
1. Possible diagnosis
2. Recommended actions
3. When to seek immediate medical attention

Important: This is for informational purposes only and should not replace professional medical advice."""

        result = query_gemini(prompt)
        logger.info("Generated diagnosis with Gemini")
        
        # Clean up temporary file
        try:
            os.remove(filepath)
            if os.path.exists("temp.wav"):
                os.remove("temp.wav")
        except:
            pass
            
        return result
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        # Clean up any temporary files
        try:
            if os.path.exists("temp_audio.wav"):
                os.remove("temp_audio.wav")
            if os.path.exists("temp.wav"):
                os.remove("temp.wav")
        except:
            pass
        return f"Error processing your request: {str(e)}", 500

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
