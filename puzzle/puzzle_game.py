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
import sys

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
    except sr.UnknownValueError:
        audio_queue.put("__speech_not_understood__")
    except sr.RequestError:
        audio_queue.put("__speech_service_error__")
    except Exception as e:
        audio_queue.put("__unknown_error__")

def normalize_answer(ans):
    return ans.strip().lower()

pygame.mixer.init()
correct_sound = pygame.mixer.Sound("./assets/correct.mp3")
wrong_sound = pygame.mixer.Sound("./assets/error.mp3")
game_over_sound = pygame.mixer.Sound("./assets/gameover.mp3")
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
    score = 0

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
                draw_text(f"Score: {score}", 20, (50, 50, 200))
                draw_text("Puzzle:", 60)
                draw_text(puzzle.prompt, 100)
                draw_text("Speak your answer...", 200)
                
                try:
                    user_input = audio_queue.get_nowait()
                    if user_input:
                        if user_input == "__speech_not_understood__":
                            message = "Didn't catch that. Please try again."
                        elif user_input == "__speech_service_error__":
                            message = "Connection problem. Please check your internet."
                        elif user_input == "__unknown_error__":
                            message = "An unknown error occurred."
                        elif user_input in ["exit", "خروج"]:
                            message = "Goodbye! خداافز"
                            state = "end"
                        elif user_input in ["i don't know", "نمی‌دونم", "نمیدونم"]:
                            message = f"The correct answer was: {puzzle.answer}"
                            puzzle = None
                            wrong_sound.play()
                            score -= 1
                        elif normalize_answer(user_input) == normalize_answer(puzzle.answer):
                            message = "Correct! the answer was: {}".format(puzzle.answer)
                            puzzle = None
                            correct_sound.play()
                            sleep_time = 3
                            score += 2
                        else:
                            message = f"X Incorrect ,you said: {user_input} .Try again..."
                            wrong_sound.play()
                except queue.Empty:
                    pass
                
        elif state == "end":
            game_over_sound.play()
            draw_text(f"Game Over!", 120)
            draw_text(f"Your final score: {score}", 170, (50, 50, 200))
            draw_text("Press any key to exit...", 250)
            pygame.display.flip()
    
            waiting_for_exit = True
            while waiting_for_exit:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                        waiting_for_exit = False
                        pygame.quit()
                        sys.exit()
        
        pygame.display.flip()
        pygame.time.wait(100)

if __name__ == "__main__":
    main()
