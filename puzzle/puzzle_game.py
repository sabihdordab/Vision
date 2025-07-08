import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    audio = recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio, language='fa-IR')  
    print("you said:", text)
except sr.UnknownValueError:
    print("no voice detected")
except sr.RequestError as e:
    print("could not request results;", e)
