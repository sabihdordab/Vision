import pygame
import random
import speech_recognition as sr
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Puzzle
import os
import threading
import queue
import arabic_reshaper
from bidi.algorithm import get_display
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "puzzles.db")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()

recognizer = sr.Recognizer()
mic = sr.Microphone()
audio_queue = queue.Queue()

voice_lang = "en-US"  

def callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language=voice_lang)
        audio_queue.put(text.lower().strip())
    except:
        audio_queue.put("")

def normalize_answer(ans):
    return ans.strip().lower()

pygame.init()
WIDTH, HEIGHT = 1300, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice-based puzzle game")
font = pygame.font.Font("./assets/Vazirmatn-Regular.ttf", 28)

def draw_text(text, y, color=(0,0,0)):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any('\u0600' <= c <= '\u06FF' for c in line): 
            reshaped_text = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped_text)
            rendered = font.render(bidi_text, True, color)
        else:
            rendered = font.render(line, True, color)
        screen.blit(rendered, (40, y + i*40))

def main():
    global voice_lang
    running = True
    state = "choose_lang"
    lang = None
    puzzle = None
    message = ""
    stop_listening = None
    sleep_time = 0

    while running:
        screen.fill((220, 220, 250))
        if message:
                    draw_text(message, 350, (0,100,0))
        time.sleep(sleep_time)
        sleep_time = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                if stop_listening: stop_listening()
            elif event.type == pygame.KEYDOWN:
                if state == "choose_lang":
                    if event.key == pygame.K_f:
                        lang = "fa"
                        voice_lang = "fa-IR"
                        state = "game"
                    elif event.key == pygame.K_e:
                        lang = "en"
                        voice_lang = "en-US"
                        state = "game"
                    if state == "game":
                        with mic as source:
                            recognizer.adjust_for_ambient_noise(source)
                        stop_listening = recognizer.listen_in_background(mic, callback)
        
        if state == "choose_lang":
            draw_text("Press F for فارسی or E for English", 120)
        elif state == "game":
            if not puzzle:
                puzzles = session.query(Puzzle).filter_by(language=lang).all()
                if not puzzles:
                    draw_text("No puzzles found.", 120)
                    state = "end"
                else:
                    puzzle = random.choice(puzzles)
                    message = ""
            else:
                draw_text("Puzzle:", 60)
                draw_text(puzzle.prompt, 100)
                draw_text("Speak your answer...", 200)
                
                try:
                    user_input = audio_queue.get_nowait()
                    if user_input:
                        if user_input in ["exit", "خروج"]:
                            message = "👋 Goodbye! خداافز"
                            state = "end"
                        elif user_input in ["i don't know", "نمی‌دونم", "نمیدونم"]:
                            message = f"❓ The correct answer was: {puzzle.answer}"
                            puzzle = None
                        elif normalize_answer(user_input) == normalize_answer(puzzle.answer):
                            message = "✅ Correct! the answer was: {}".format(puzzle.answer)
                            puzzle = None
                            sleep_time = 5
                        else:
                            message = f"❌ Incorrect ,you said: {user_input} .Try again..."
                except queue.Empty:
                    pass
                
        elif state == "end":
            draw_text("Game Over or No puzzles found. Close window to exit.", 150)
        
        pygame.display.flip()
        pygame.time.wait(100)

if __name__ == "__main__":
    main()
