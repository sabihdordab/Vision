import random
import speech_recognition as sr
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Puzzle
import os
import threading
import queue

# Database connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "puzzles.db")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()

recognizer = sr.Recognizer()
mic = sr.Microphone()

audio_queue = queue.Queue() #background queue

def callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language=voice_lang)
        print(f"🗣 You said: {text}")
        audio_queue.put(text.lower().strip())
    except sr.UnknownValueError:
        print("❌ Couldn't understand.")
    except sr.RequestError as e:
        print("⚠️ Speech service error:", e)

def normalize_answer(ans):
    return ans.strip().lower()

def main():
    global voice_lang 
    lang = input("Choose language (fa/en): ").strip().lower()
    if lang not in ("fa", "en"):
        print("Invalid language selected.")
        return

    voice_lang = "fa-IR" if lang == "fa" else "en-US"

    print("\n🎮 Voice-based puzzle game started. Say 'exit' to quit.\n")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    stop_listening = recognizer.listen_in_background(mic, callback)

    try:
        while True:
            puzzles = session.query(Puzzle).filter_by(language=lang).all()
            if not puzzles:
                print("No puzzles found.")
                break

            puzzle = random.choice(puzzles)
            print("\n🧩 Puzzle:")
            print(puzzle.prompt)

            print("🎤 Please answer:")

            try:
                user_input = audio_queue.get(timeout=30)
            except queue.Empty:
                print("⏰ No response detected. Moving to next puzzle.")
                continue

            if user_input in ["exit", "خروج"]:
                print("👋 Goodbye!")
                break
            elif user_input in ["i don't know", "idk", "نمی‌دونم", "نمیدونم"]:
                print(f"❓ The correct answer was: {puzzle.answer}")
            elif normalize_answer(user_input) == normalize_answer(puzzle.answer):
                print("✅ Correct!")
            else:
                print(f"❌ Incorrect. The correct answer was: {puzzle.answer}")

            print("\nContinue? Say 'yes' or 'exit'")

            try:
                again = audio_queue.get(timeout=30)
            except queue.Empty:
                print("⏰ No response detected. Exiting.")
                break

            if again not in ["yes", "بله", "آره"]:
                print("👋 Game over.")
                break

    finally:
        stop_listening()

if __name__ == "__main__":
    main()
