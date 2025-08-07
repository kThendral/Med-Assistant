import speech_recognition as sr
from pydub import AudioSegment
import os
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(path):
    """
    Transcribe audio file to text using Google Speech Recognition
    """
    try:
        recognizer = sr.Recognizer()
        
        # Check if input file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"Audio file not found: {path}")
        
        # Convert audio to WAV format if needed
        try:
            sound = AudioSegment.from_file(path)
            temp_wav_path = "temp.wav"
            sound.export(temp_wav_path, format="wav")
            logger.info(f"Audio converted to WAV format: {temp_wav_path}")
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            # If conversion fails, try using the original file
            temp_wav_path = path
        
        # Transcribe audio
        with sr.AudioFile(temp_wav_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)
        
        # Use Google Speech Recognition
        text = recognizer.recognize_google(audio, language='en-US')
        logger.info(f"Transcription successful: {text}")
        
        # Clean up temporary file
        if temp_wav_path != path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        
        return text
        
    except sr.UnknownValueException:
        logger.warning("Speech recognition could not understand audio")
        raise Exception("Could not understand the audio. Please try speaking more clearly.")
    except sr.RequestError as e:
        logger.error(f"Speech recognition service error: {e}")
        raise Exception("Speech recognition service is unavailable. Please try again later.")
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        # Clean up temporary file in case of error
        if 'temp_wav_path' in locals() and temp_wav_path != path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        raise Exception(f"Error processing audio: {str(e)}")
