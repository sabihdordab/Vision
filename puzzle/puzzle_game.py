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
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple


class GameState(Enum):
    CHOOSE_LANG = "choose_lang"
    GAME = "game"
    END = "end"


class CharacterState(Enum):
    THINKING = "thinking"
    WIN = "win"
    LOSE = "lose"



GAME_CONFIG = {
    'WIDTH': 1300,
    'HEIGHT': 500,
    'COLORS': {
        'BLACK': (0, 0, 0),
        'WHITE': (255, 255, 255),
        'DARK_BLUE': (0, 0, 200),
        'RED': (255, 0, 0),
        'YELLOW': (247, 173, 25),
        'LIGHT_BLUE': (159, 231, 245),
    },
    'SCORING': {
        'CORRECT': 2,
        'WRONG': -1,
    },
    'TIMING': {
        'CHARACTER_CHANGE_INTERVAL': 3.0,
        'GAME_OVER_SOUND_INTERVAL': 8,
    }
}


game_state = {
    'current_state': GameState.CHOOSE_LANG,
    'language': None,
    'show_help': False,
    'running': True,
    'score': 0,
    'correct_count': 0,
    'wrong_count': 0,
    'used_puzzles': set(),
    'current_puzzle': None,
    'message': "",
    'character_state': CharacterState.THINKING,
    'last_character_change': time.time(),
    'background': None,
    'current_character_image': None,
}


db_session = None
audio_queue = queue.Queue()
recognizer = sr.Recognizer()
mic = sr.Microphone()
stop_listening = None
voice_lang = "en-US"

# Assets
sounds = {}
images = {}
character_sets = {}
bg_images = []


def initialize_database():
    global db_session
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "puzzles.db")
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    db_session = Session()


def load_sounds():
    global sounds
    pygame.mixer.init()
    
    sound_files = {
        'correct': './assets/correct.mp3',
        'wrong': './assets/error.mp3',
        'game_over': './assets/gameover.mp3'
    }
    
    for name, path in sound_files.items():
        try:
            sounds[name] = pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Warning: Could not load {name} sound: {e}")
            sounds[name] = None


def load_images():
    global images
    
    try:
        images['mic_icon'] = pygame.image.load("./assets/mic.png")
        images['mic_icon'] = pygame.transform.scale(images['mic_icon'], (40, 40))
    except pygame.error as e:
        print(f"Warning: Could not load mic icon: {e}")
        images['mic_icon'] = None
    
    try:
        first_bg = pygame.image.load("./assets/puzzle/first.jpg")
        images['first_bg'] = pygame.transform.scale(first_bg, (GAME_CONFIG['WIDTH'], GAME_CONFIG['HEIGHT']))
    except pygame.error as e:
        print(f"Warning: Could not load first background: {e}")
        images['first_bg'] = None


def load_backgrounds():
    global bg_images
    bg_images = glob.glob(os.path.join("./assets/puzzle/backgrounds/", "*.jpg"))


def load_character_images():
    global character_sets
    
    for state in CharacterState:
        folder_path = os.path.join("./assets/character", state.value)
        image_files = glob.glob(os.path.join(folder_path, "*.png"))
        
        if image_files:
            character_sets[state] = []
            for img_path in image_files:
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    character_sets[state].append(img)
                except pygame.error as e:
                    print(f"Warning: Could not load character image {img_path}: {e}")
        else:
            character_sets[state] = []


def initialize_assets():
    load_sounds()
    load_images()
    load_backgrounds()
    load_character_images()


def audio_callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language=voice_lang)
        audio_queue.put(text.lower().strip())
    except sr.UnknownValueError:
        audio_queue.put("__speech_not_understood__")
    except sr.RequestError:
        audio_queue.put("__speech_service_error__")
    except Exception:
        audio_queue.put("__unknown_error__")


def set_language(lang: str):
    global voice_lang
    voice_lang = "fa-IR" if lang == "fa" else "en-US"


def start_listening():
    global stop_listening
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
    stop_listening = recognizer.listen_in_background(mic, audio_callback)


def stop_listening_process():
    global stop_listening
    if stop_listening:
        stop_listening()


def get_audio_input():
    try:
        return audio_queue.get_nowait()
    except queue.Empty:
        return None


def play_sound(sound_name):
    if sound_name in sounds and sounds[sound_name]:
        sounds[sound_name].play()


def get_random_background():
    if not bg_images:
        return None
    
    path = random.choice(bg_images)
    try:
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (GAME_CONFIG['WIDTH'], GAME_CONFIG['HEIGHT']))
    except pygame.error:
        return None


def get_character_image(state):
    if state in character_sets and character_sets[state]:
        return random.choice(character_sets[state])
    return None


def get_puzzles_by_language(language):
    return db_session.query(Puzzle).filter_by(language=language).all()


def normalize_answer(answer):
    return answer.strip().lower()


def check_answer(user_input, correct_answer):
    return normalize_answer(user_input) == normalize_answer(correct_answer)


def reset_game():
    global game_state
    game_state.update({
        'score': 0,
        'correct_count': 0,
        'wrong_count': 0,
        'used_puzzles': set(),
        'current_puzzle': None,
        'message': "",
        'character_state': CharacterState.THINKING,
        'last_character_change': time.time(),
        'background': None,
        'current_character_image': None,
    })


def get_next_puzzle(available_puzzles):
    available = [p for p in available_puzzles if p.id not in game_state['used_puzzles']]
    if not available:
        return None
    
    puzzle = random.choice(available)
    game_state['used_puzzles'].add(puzzle.id)
    game_state['current_puzzle'] = puzzle
    return puzzle


def should_change_character():
    return time.time() - game_state['last_character_change'] > GAME_CONFIG['TIMING']['CHARACTER_CHANGE_INTERVAL']


def update_character_change_time():
    game_state['last_character_change'] = time.time()


def get_final_character_state():
    return CharacterState.LOSE if game_state['correct_count'] <= game_state['wrong_count'] else CharacterState.WIN


def process_user_input(user_input):
    result = {
        "new_puzzle": False,
        "game_end": False,
        "message": "",
        "score_change": 0,
        "sound": None
    }
    
    if user_input == "__speech_not_understood__":
        result["message"] = "Didn't catch that. Please try again."
    elif user_input == "__speech_service_error__":
        result["message"] = "Connection problem. Please check your internet."
    elif user_input == "__unknown_error__":
        result["message"] = "An unknown error occurred."
    elif user_input in ["exit", "خروج"]:
        result["message"] = "Goodbye! خداحافظ"
        result["game_end"] = True
    elif user_input in ["i don't know", "نمی‌دونم", "نمیدونم"]:
        result["new_puzzle"] = True
        result["score_change"] = GAME_CONFIG['SCORING']['WRONG']
        result["sound"] = "wrong"
        game_state['wrong_count'] += 1
    elif game_state['current_puzzle'] and check_answer(user_input, game_state['current_puzzle'].answer):
        result["message"] = "Correct!"
        result["new_puzzle"] = True
        result["score_change"] = GAME_CONFIG['SCORING']['CORRECT']
        result["sound"] = "correct"
        game_state['correct_count'] += 1
    else:
        result["message"] = f"X Incorrect, you said: {user_input}. Try again..."
        result["sound"] = "wrong"
    
    game_state['score'] += result["score_change"]
    game_state['message'] = result["message"]
    
    return result


def draw_text(screen, text, y, color= None, x = 40, font = None):
    if color is None:
        color = GAME_CONFIG['COLORS']['WHITE']
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any('\u0600' <= c <= '\u06FF' for c in line):
            # Arabic text processing
            reshaped_text = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped_text)
            rendered = font.render(bidi_text, True, color)
        else:
            rendered = font.render(line, True, color)
        
        screen.blit(rendered, (x, y + i * 40))


def draw_key_button(screen, text, x, y, key_font):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, 50, 40)
    
    color = GAME_CONFIG['COLORS']['DARK_BLUE'] if rect.collidepoint(mouse_pos) else GAME_CONFIG['COLORS']['BLACK']
    pygame.draw.rect(screen, color, rect, border_radius=8)
    
    txt = key_font.render(text, True, GAME_CONFIG['COLORS']['YELLOW'])
    screen.blit(txt, (x + 15, y + 8))


def draw_help(screen, font, key_font):
    box_width, box_height = 900, 330
    box_x = (GAME_CONFIG['WIDTH'] - box_width) // 2
    box_y = (GAME_CONFIG['HEIGHT'] - box_height) // 2
    
    pygame.draw.rect(screen, GAME_CONFIG['COLORS']['YELLOW'], (box_x, box_y, box_width, box_height), border_radius=12)
    
    start_x = box_x + 20
    start_y = box_y + 20
    

    draw_text(screen, "Help:", start_y - 5, GAME_CONFIG['COLORS']['DARK_BLUE'], start_x, font)
    draw_key_button(screen, "H", start_x, start_y + 35, key_font)
    draw_text(screen, "Show/Hide Help", start_y + 40, GAME_CONFIG['COLORS']['RED'], start_x + 70, font)
    draw_key_button(screen, "F", start_x, start_y + 85, key_font)
    draw_text(screen, "Select Persian Language", start_y + 90, GAME_CONFIG['COLORS']['RED'], start_x + 70, font)
    draw_key_button(screen, "E", start_x, start_y + 135, key_font)
    draw_text(screen, "Select English Language", start_y + 140, GAME_CONFIG['COLORS']['RED'], start_x + 70, font)
    draw_text(screen, "This is a voice-controlled puzzle game. Speak your answers!", start_y + 180, GAME_CONFIG['COLORS']['BLACK'], start_x, font)
    draw_text(screen, "Say 'exit'|'خروج' or press Q to quit the game", start_y + 220, GAME_CONFIG['COLORS']['BLACK'], start_x, font)
    draw_text(screen, "Say 'I don't know'|'نمی دونم' to skip a puzzle", start_y + 260, GAME_CONFIG['COLORS']['BLACK'], start_x, font)


def draw_mic_icon(screen, x, y):
    pygame.draw.circle(screen, GAME_CONFIG['COLORS']['DARK_BLUE'], (x + 20, y + 20), 25, 3)
    if images['mic_icon']:
        screen.blit(images['mic_icon'], (x, y))


def draw_character(screen, character_image):
    if character_image:
        img = pygame.transform.scale(character_image, (200, 200))
        screen.blit(img, (GAME_CONFIG['WIDTH'] - img.get_width() - 30, GAME_CONFIG['HEIGHT'] - img.get_height() - 30))


def handle_keydown(event):
    if event.key == pygame.K_q:
        pygame.quit()
        sys.exit()
    
    if game_state['current_state'] == GameState.CHOOSE_LANG:
        if event.key == pygame.K_f:
            game_state['language'] = "fa"
            set_language("fa")
            start_game()
        elif event.key == pygame.K_e:
            game_state['language'] = "en"
            set_language("en")
            start_game()
        elif event.key == pygame.K_h:
            game_state['show_help'] = not game_state['show_help']


def start_game():
    game_state['current_state'] = GameState.GAME
    start_listening()


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state['running'] = False
            stop_listening_process()
        elif event.type == pygame.KEYDOWN:
            handle_keydown(event)


def update_game_logic():
    if not game_state['current_puzzle']:
        puzzles = get_puzzles_by_language(game_state['language'])
        puzzle = get_next_puzzle(puzzles)
        
        if not puzzle:
            game_state['message'] = "All puzzles completed!"
            game_state['current_state'] = GameState.END
            return
        
        game_state['background'] = get_random_background()
        game_state['message'] = ""
    
    # Update character animation
    if game_state['character_state'] == CharacterState.THINKING and should_change_character():
        game_state['current_character_image'] = get_character_image(CharacterState.THINKING)
        update_character_change_time()
    
    # Process audio input
    user_input = get_audio_input()
    if user_input:
        result = process_user_input(user_input)
        
        if result["sound"]:
            play_sound(result["sound"])
        
        if result["new_puzzle"]:
            game_state['current_puzzle'] = None
        
        if result["game_end"]:
            game_state['current_state'] = GameState.END


def update_end_state():
    
    if should_change_character():
        update_character_change_time()
        final_state = get_final_character_state()  # CharacterState.WIN or CharacterState.LOSE
        game_state['character_state'] = final_state
        game_state['current_character_image'] = get_character_image(final_state)
        
    
    if int(time.time()) % GAME_CONFIG['TIMING']['GAME_OVER_SOUND_INTERVAL'] == 0:
        play_sound("game_over")


def update_game_state():
    if game_state['current_state'] == GameState.GAME:
        update_game_logic()
    elif game_state['current_state'] == GameState.END:
        update_end_state()


def render_language_selection(screen , font, key_font):
    if game_state['show_help']:
        draw_help(screen, font, key_font)
    else:
        draw_key_button(screen, "H", 200, 340, key_font)
        draw_text(screen, "Show/Hide Help", 340, GAME_CONFIG['COLORS']['BLACK'], 260, font)
        draw_key_button(screen, "F", 500, 340, key_font)
        draw_text(screen, "Persian Language", 340, GAME_CONFIG['COLORS']['DARK_BLUE'], 560, font)
        draw_key_button(screen, "E", 820, 340, key_font)
        draw_text(screen, "English Language", 340, GAME_CONFIG['COLORS']['DARK_BLUE'], 880, font)


def render_game(screen, font):
    if game_state['current_puzzle']:
        if game_state['character_state'] == CharacterState.THINKING:
            if game_state['current_character_image']:
                draw_character(screen, game_state['current_character_image'])
        
        
        draw_text(screen, f"Score: {game_state['score']}", 20, GAME_CONFIG['COLORS']['RED'], 40, font)
        draw_text(screen, "Puzzle:", 60, GAME_CONFIG['COLORS']['DARK_BLUE'], 40, font)
        draw_text(screen, game_state['current_puzzle'].prompt, 100, GAME_CONFIG['COLORS']['YELLOW'], 40, font)
        draw_text(screen, "Speak your answer...", 200, GAME_CONFIG['COLORS']['WHITE'], 40, font)
        
        
        if int(time.time() * 2) % 2 == 0:
            draw_mic_icon(screen, 400, 200)


def render_end_screen(screen, font):
    
    total_puzzles = game_state['correct_count'] + game_state['wrong_count']
    
    draw_text(screen, "Game Over!", 30, GAME_CONFIG['COLORS']['WHITE'], 40, font)
    draw_text(screen, f"Your final score: {game_state['score']}", 90, GAME_CONFIG['COLORS']['YELLOW'], 40, font)
    draw_text(screen, f"Total puzzles: {total_puzzles}", 140, GAME_CONFIG['COLORS']['YELLOW'], 40, font)
    draw_text(screen, f"Correct answers: {game_state['correct_count']}", 190, GAME_CONFIG['COLORS']['YELLOW'], 40, font)
    draw_text(screen, f"Wrong answers: {game_state['wrong_count']}", 240, GAME_CONFIG['COLORS']['RED'], 40, font)
    draw_text(screen, "Press Q to exit...", 295, GAME_CONFIG['COLORS']['WHITE'], 40, font)
    
    if game_state['current_character_image']:
        draw_character(screen, game_state['current_character_image'])


def render(screen, font, key_font):
    # Set background
    if game_state['current_state'] == GameState.GAME and game_state['background']:
        screen.blit(game_state['background'], (0, 0))
    elif game_state['current_state'] == GameState.CHOOSE_LANG and not game_state['show_help']:
        if images['first_bg']:
            screen.blit(images['first_bg'], (0, 0))
    else:
        screen.fill(GAME_CONFIG['COLORS']['BLACK'])
    
 
    if game_state['message']:
        draw_text(screen, game_state['message'], 350, GAME_CONFIG['COLORS']['WHITE'], 40, font)
    
    if game_state['current_state'] == GameState.CHOOSE_LANG:
        render_language_selection(screen, font, key_font)
    elif game_state['current_state'] == GameState.GAME:
        render_game(screen, font)
    elif game_state['current_state'] == GameState.END:
        render_end_screen(screen, font)
    
    pygame.display.flip()


def cleanup():
    stop_listening_process()
    if db_session:
        db_session.close()
    pygame.quit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((GAME_CONFIG['WIDTH'], GAME_CONFIG['HEIGHT']))
    pygame.display.set_caption("Voice-based puzzle game")
    

    try:
        font = pygame.font.Font("./assets/Vazirmatn-Regular.ttf", 28)
        key_font = pygame.font.Font("./assets/Vazirmatn-Regular.ttf", 24)
    except pygame.error:
        print("Warning: Could not load custom font, using default")
        font = pygame.font.Font(None, 28)
        key_font = pygame.font.Font(None, 24)
    

    initialize_database()
    initialize_assets()
    

    clock = pygame.time.Clock()
    
    while game_state['running']:
        handle_events()
        update_game_state()
        render(screen, font, key_font)
        clock.tick(60)
    
    cleanup()


if __name__ == "__main__":
    main()