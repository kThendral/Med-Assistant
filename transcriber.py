import speech_recognition as sr
from pydub import AudioSegment

def transcribe_audio(path):
    recognizer = sr.Recognizer()
    sound = AudioSegment.from_file(path)
    sound.export("temp.wav", format="wav")
    with sr.AudioFile("temp.wav") as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)
