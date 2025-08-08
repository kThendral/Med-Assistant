import google.generativeai as genai
from config import GOOGLE_API_KEY
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=GOOGLE_API_KEY)

# Use the updated model name for Gemini 1.5
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    logger.info("Using gemini-1.5-flash model")
except Exception as e:
    logger.warning(f"Failed to load gemini-1.5-flash, trying gemini-1.5-pro: {e}")
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        logger.info("Using gemini-1.5-pro model")
    except Exception as e2:
        logger.error(f"Failed to load any Gemini model: {e2}")
        raise

def query_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error querying Gemini: {e}")
        raise Exception(f"Failed to generate response from Gemini AI: {str(e)}")
