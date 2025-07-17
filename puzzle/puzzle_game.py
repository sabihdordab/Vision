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
import difflib
import glob

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

pygame.init()
pygame.mixer.init()

BLACK = (0,0,0) 
BG_COLOR = BLACK            
WHITE = (255, 255, 255)              
DARK_BLUE = (0, 0, 200)
RED = (255, 0, 0)
MIC_ICON_COLOR = DARK_BLUE
YELLOW = (247, 173, 25)
LIGHT_BLUE = (159, 231, 245)

ASSETS_DIR = BASE_DIR + "/assets/"
correct_sound = pygame.mixer.Sound( ASSETS_DIR + "correct.mp3")
wrong_sound = pygame.mixer.Sound(ASSETS_DIR + "error.mp3")
game_over_sound = pygame.mixer.Sound(ASSETS_DIR + "gameover.mp3")
mic_icon = pygame.image.load(ASSETS_DIR + "mic.png")
mic_icon = pygame.transform.scale(mic_icon, (40, 40))

WIDTH, HEIGHT = 1300, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice-based puzzle game")
font = pygame.font.Font(ASSETS_DIR + "Vazirmatn-Regular.ttf", 28)
bg_images = glob.glob(os.path.join(ASSETS_DIR + "bg/backgrounds/", "*.jpg"))

def load_random_background():
    if not bg_images:
        return None
    path = random.choice(bg_images)
    img = pygame.image.load(path)
    return pygame.transform.scale(img, (WIDTH, HEIGHT))

def draw_text(text, y, color=WHITE, x=40):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any('\u0600' <= c <= '\u06FF' for c in line):

            reshaped_text = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped_text)
            rendered = font.render(bidi_text, True, color)
        else:
            rendered = font.render(line, True, color)
        screen.blit(rendered, (x, y + i*40))


def draw_key_button(text, x, y):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, 50, 40)
    if rect.collidepoint(mouse_pos):
        color = DARK_BLUE
    else:
        color = BLACK

    pygame.draw.rect(screen, color, rect, border_radius=8)
    key_font = pygame.font.Font(ASSETS_DIR +"Vazirmatn-Regular.ttf", 24)
    txt = key_font.render(text, True, WHITE)
    screen.blit(txt, (x + 15, y + 8))

def draw_help():
    box_width, box_height = 900, 330
    box_x = (WIDTH - box_width) // 2
    box_y = (HEIGHT - box_height) // 2
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=12)


    start_x = box_x + 20
    start_y = box_y + 20

    draw_text("Help:", start_y-5, DARK_BLUE, x=start_x)
    draw_key_button("H", start_x, start_y + 35)
    draw_text("Show/Hide Help", start_y + 40, x=start_x + 70 , color=RED)
    draw_key_button("F", start_x, start_y + 85)
    draw_text("Select Persian Language", start_y + 90, x=start_x + 70,color=RED)
    draw_key_button("E", start_x, start_y + 135)
    draw_text("Select English Language", start_y + 140, x=start_x + 70,color=RED)
    draw_text("This is a voice-controlled puzzle game. Speak your answers!", start_y + 180, x=start_x , color=BLACK)
    draw_text("Say 'exit'|'خروج' or press Q to quit the game", start_y + 220, x=start_x,color=BLACK)
    draw_text("Say 'I don't know'|'نمی دونم' to skip a puzzle", start_y + 260, x=start_x,color=BLACK)

def draw_mic_icon(x, y):
    pygame.draw.circle(screen, MIC_ICON_COLOR, (x+20, y+20), 25, 3) 
    screen.blit(mic_icon, (x, y))

def load_character_images(folder_name):
    folder_path = os.path.join(ASSETS_DIR + "character", folder_name)
    images = glob.glob(os.path.join(folder_path, "*.png"))
    return [pygame.image.load(img).convert_alpha() for img in images]

character_sets = {
    "thinking": load_character_images("thinking"),
    "win": load_character_images("win"),
    "lose": load_character_images("lose")
}


def draw_character(state_name):
    if character_sets.get(state_name):
        img = random.choice(character_sets[state_name])
        img = pygame.transform.scale(img, (200, 200))
        screen.blit(img, (WIDTH - img.get_width() - 30, HEIGHT - img.get_height() - 30))


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
    show_help = False
    used_puzzles = set()
    correct_count = 0
    wrong_count = 0
    background = None
    message = ""
    character_state = "thinking"
    last_character_change = time.time()
    current_character_image = random.choice(character_sets[character_state])

    while running:
        if state == "game" and background:
            screen.blit(background, (0, 0))
        elif state == "choose_lang":
            img = pygame.image.load(ASSETS_DIR + "bg/first.jpg")
            bg= pygame.transform.scale(img, (WIDTH, HEIGHT))
            screen.blit(bg, (0, 0))
        else:
            screen.fill(BG_COLOR)

        if message:
                draw_text(message, 350)
        time.sleep(sleep_time)
        sleep_time = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                if stop_listening: stop_listening()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if state == "choose_lang":
                    if event.key == pygame.K_f:
                        lang = "fa"
                        voice_lang = "fa-IR"
                        state = "game"
                    elif event.key == pygame.K_e:
                        lang = "en"
                        voice_lang = "en-US"
                        state = "game"
                    elif event.key == pygame.K_h:
                        show_help = not show_help
                    if state == "game":
                        with mic as source:
                            recognizer.adjust_for_ambient_noise(source)
                        stop_listening = recognizer.listen_in_background(mic, callback)
        
        if state == "choose_lang":
            if show_help:
                draw_help()
            else:
                draw_key_button("H", 200, 340)
                draw_text("Show/Hide Help", 340, x=260,color=BLACK)
                draw_key_button("F", 500, 340)
                draw_text("Persian Language", 340, x=560,color=WHITE)
                draw_key_button("E", 820, 340)
                draw_text("English Language", 340, x=880,color=WHITE)

        elif state == "game":
            if not puzzle:
                available = [p for p in session.query(Puzzle).filter_by(language=lang).all() if p.id not in used_puzzles]
                if not available:
                    message = "All puzzles completed!"
                    state = "end"
                else:
                    puzzle = random.choice(available)
                    used_puzzles.add(puzzle.id)
                    background = load_random_background()
                    message = ""
            else:
                if character_state == "thinking":
                    now = time.time()
                    if now - last_character_change > 3: 
                        current_character_image = random.choice(character_sets[character_state])
                        last_character_change = now

                    img = pygame.transform.scale(current_character_image, (200, 200))
                    screen.blit(img, (WIDTH - img.get_width() - 30, HEIGHT - img.get_height() - 30))

                draw_text(f"Score: {score}", 20, RED)
                draw_text("Puzzle:", 60 , color=DARK_BLUE)
                draw_text(puzzle.prompt, 100 , color=YELLOW)
                draw_text("Speak your answer...", 200)
                
                if int(time.time() * 2) % 2 == 0:
                    draw_mic_icon(400, 200)

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
                            # message = f"The correct answer was: {puzzle.answer}"
                            puzzle = None
                            wrong_sound.play()
                            # sleep_time = 3
                            score -= 1
                            wrong_count += 1
                        elif normalize_answer(user_input) == normalize_answer(puzzle.answer):
                            message = "Correct!"
                            puzzle = None
                            correct_sound.play()
                            score += 2
                            correct_count += 1
                        else:
                            message = f"X Incorrect ,you said: {user_input}.Try again..."
                            wrong_sound.play()
                except queue.Empty:
                    pass
                
        elif state == "end":
            character_state  = "win"
            if correct_count <= wrong_count:
                character_state = "lose"

            if int(time.time()) % 8 == 0:
                game_over_sound.play()

            draw_text("Game Over!", 30)
            draw_text(f"Your final score: {score}", 90,color=YELLOW)
            draw_text(f"Total puzzles: {correct_count + wrong_count}", 140,color=YELLOW)
            draw_text(f"Correct answers: {correct_count}", 190,color=YELLOW)
            draw_text(f"Wrong answers: {wrong_count}", 240,color=RED)
            draw_text("Press Q to exit...", 295)
            draw_character(character_state)
            pygame.display.flip()
            pygame.time.wait(900)
            
        
        pygame.display.flip()
        pygame.time.wait(100)

if __name__ == "__main__":
    main()