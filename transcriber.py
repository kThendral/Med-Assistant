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
        
        logger.info(f"Processing audio file: {path}")
        
        # Always convert to proper WAV format for speech recognition
        temp_wav_path = "temp_converted.wav"
        try:
            # Try to load the audio file with pydub (supports many formats)
            logger.info("Loading audio file with pydub...")
            
            # Try different format assumptions since browser MediaRecorder can produce various formats
            sound = None
            formats_to_try = [None, "webm", "ogg", "mp4", "wav"]
            
            for fmt in formats_to_try:
                try:
                    if fmt is None:
                        sound = AudioSegment.from_file(path)
                        logger.info("Successfully loaded audio with auto-detection")
                    else:
                        sound = AudioSegment.from_file(path, format=fmt)
                        logger.info(f"Successfully loaded audio as {fmt} format")
                    break
                except Exception as format_error:
                    logger.warning(f"Failed to load as {fmt or 'auto'}: {format_error}")
                    continue
            
            if sound is None:
                raise Exception("Could not load audio file in any supported format")
            
            # Convert to mono, 16kHz, 16-bit WAV (optimal for speech recognition)
            logger.info("Converting audio to optimal format for speech recognition...")
            sound = sound.set_channels(1)  # Convert to mono
            sound = sound.set_frame_rate(16000)  # Set sample rate to 16kHz
            sound = sound.set_sample_width(2)  # Set to 16-bit
            
            # Export as WAV
            sound.export(temp_wav_path, format="wav")
            logger.info(f"Audio successfully converted to WAV format: {temp_wav_path}")
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise Exception(f"Could not process audio file. Error: {str(e)}")
        
        # Transcribe audio using the converted WAV file
        try:
            logger.info("Starting speech recognition...")
            with sr.AudioFile(temp_wav_path) as source:
                # Adjust for ambient noise
                logger.info("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio
                logger.info("Recording audio for transcription...")
                audio = recognizer.record(source)
            
            # Use Google Speech Recognition
            logger.info("Calling Google Speech Recognition API...")
            text = recognizer.recognize_google(audio, language='en-US')
            logger.info(f"Transcription successful: {text}")
            
            return text
            
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            raise Exception("Could not understand the audio. Please try speaking more clearly or check if audio contains speech.")
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            raise Exception("Speech recognition service is unavailable. Please check your internet connection and try again.")
        except Exception as e:
            logger.error(f"Error during speech recognition: {e}")
            raise Exception(f"Speech recognition failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise Exception(f"Audio processing failed: {str(e)}")
    
    finally:
        # Clean up temporary files
        try:
            if 'temp_wav_path' in locals() and temp_wav_path != path and os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
                logger.info("Temporary audio file cleaned up")
        except Exception as cleanup_error:
            logger.warning(f"Could not clean up temporary file: {cleanup_error}")
