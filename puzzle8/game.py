import pygame
import os
import random
import speech_recognition as sr
import threading
import queue
import arabic_reshaper
from bidi.algorithm import get_display

base_dir = os.path.dirname(os.path.abspath(__file__))
TILES_BASE_FOLDER = os.path.join(base_dir, "tiles")  
ICON_PATH = os.path.join(base_dir, "assets", "refresh.png")

recognizer = sr.Recognizer()
mic = sr.Microphone()
audio_queue = queue.Queue()

GRID_SIZE = 3
TILE_SIZE = 100
HEADER_HEIGHT = 75
WINDOW_WIDTH = GRID_SIZE * TILE_SIZE
WINDOW_HEIGHT = GRID_SIZE * TILE_SIZE + HEADER_HEIGHT

REFRESH_BUTTON_POS = (WINDOW_WIDTH - 50, 30)
REFRESH_BUTTON_SIZE = (32, 32)
WIN_MUSIC_PATH = os.path.join(base_dir, "assets", "win.wav")
win_image = pygame.image.load(os.path.join(base_dir, "assets", "win_image.png"))
win_image = pygame.transform.scale(win_image, (200, 200)) 

def choose_random_tile_folder():
    folders = [f for f in os.listdir(TILES_BASE_FOLDER) if os.path.isdir(os.path.join(TILES_BASE_FOLDER, f))]
    chosen = random.choice(folders)
    return os.path.join(TILES_BASE_FOLDER, chosen)

def load_tiles(tile_folder):
    tiles = []
    for i in range(GRID_SIZE * GRID_SIZE):
        tile_path = os.path.join(tile_folder, f"tile_{i}.png")
        image = pygame.image.load(tile_path)
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        tiles.append(image)
    return tiles

def draw_grid(screen, tiles, order):
    index = 0
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + HEADER_HEIGHT
            tile_index = order[index]
            screen.blit(tiles[tile_index], (x, y))
            index += 1

def is_solved(order):
    return order == list(range(GRID_SIZE * GRID_SIZE))


def generate_shuffled_order():
    order = list(range(GRID_SIZE * GRID_SIZE))
    while True:
        random.shuffle(order)
        if not is_solved(order):
            return order


def is_refresh_clicked(mouse_pos):
    x, y = mouse_pos
    rx, ry = REFRESH_BUTTON_POS
    rw, rh = REFRESH_BUTTON_SIZE
    return rx <= x <= rx + rw and ry <= y <= ry + rh

def move_empty(order, direction):
    empty_index = order.index(GRID_SIZE * GRID_SIZE - 1)
    row, col = divmod(empty_index, GRID_SIZE)

    if direction == "up" and row > 0:
        target = empty_index - GRID_SIZE
    elif direction == "down" and row < GRID_SIZE - 1:
        target = empty_index + GRID_SIZE
    elif direction == "left" and col > 0:
        target = empty_index - 1
    elif direction == "right" and col < GRID_SIZE - 1:
        target = empty_index + 1
    else:
        return order

    order[empty_index], order[target] = order[target], order[empty_index]
    return order

def audio_callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language="fa-IR")
        print("Heard:", text)
        audio_queue.put(text.lower().strip())
    except sr.UnknownValueError:
        print("Could not understand audio")
        audio_queue.put("متوجه نشدم")
    except sr.RequestError:
        print("Speech recognition service error")
        audio_queue.put("سرویس ارور")
    except Exception as e:
        print("Unknown error:", e)
        audio_queue.put("ارور ناشناخته")


def start_listening():
    global stop_listening
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
    stop_listening = recognizer.listen_in_background(mic, audio_callback)


def get_audio_input():
    try:
        return audio_queue.get_nowait()
    except queue.Empty:
        return None
    
def normalize_answer(answer):
    return answer.strip().lower()

def draw_help_screen(screen, font):
    screen.fill((255,255,255))

    help_text = [
    "__8-Puzzle Game Help__",
    "",
    "* Voice Commands (in Persian):",
    "    baalaa -> Move up",
    "    paaeen -> Move down",
    "    chap -> Move left",
    "    raast -> Move right",
    "",
    "* Keyboard Controls (when mic is OFF):",
    "    Arrow keys -> Move tiles",
    "",
    "* Press R or click the refresh icon to reshuffle tiles.",
    "* Click the mic icon to turn voice input on/off.",
    "* Press H to toggle this help screen.",
    "* Press Q to Exit.",
    "",
    "* Press H again to return to the game."
]
    y = 20
    for line in help_text:
        rendered = font.render(line, True, (255, 0 , 0))
        screen.blit(rendered, (20, y))
        y += 20

    pygame.display.flip()


def draw_win(screen, win_image):
    screen.fill((255, 255, 255))
    image_rect = win_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
    screen.blit(win_image, image_rect)

    small_font = pygame.font.Font(base_dir + "/assets/Vazirmatn-Regular.ttf", 15) 
    text = small_font.render("Press SPACE to play again.", True, (50, 0, 250))
    rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
    screen.blit(text, rect)

    pygame.display.flip()


def main():
    pygame.init()
    font = pygame.font.Font(base_dir+"/assets/Vazirmatn-Regular.ttf", 20)
    last_voice_command = ""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("8 Puzzle")

    showing_help = False
    refresh_icon = pygame.image.load(ICON_PATH)
    refresh_icon = pygame.transform.scale(refresh_icon, REFRESH_BUTTON_SIZE)
    mic_icon_size = (70, 60)
    mic_icon = pygame.image.load(os.path.join(base_dir, "assets", "mic_on.png"))
    mic_icon = pygame.transform.scale(mic_icon, mic_icon_size)
    mic_icon_x = WINDOW_WIDTH - 110
    mic_icon_rect = pygame.Rect(mic_icon_x, 10, *mic_icon_size)

    mic_active = True

    tile_folder = choose_random_tile_folder()
    tiles = load_tiles(tile_folder)
    shuffled_order = generate_shuffled_order()

    start_listening()
    game_won = False

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_won and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.music.stop()
                tile_folder = choose_random_tile_folder()
                tiles = load_tiles(tile_folder)
                shuffled_order = generate_shuffled_order()
                last_voice_command = ""
                game_won = False

            if not game_won:    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if is_refresh_clicked(event.pos):
                        tile_folder = choose_random_tile_folder()
                        tiles = load_tiles(tile_folder)
                        shuffled_order = generate_shuffled_order()
                    if mic_icon_rect.collidepoint(event.pos):
                        mic_active = not mic_active
                        if mic_active:
                            start_listening()
                        else:
                            stop_listening(wait_for_stop=False)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                            running = False
                    if event.key == pygame.K_r:
                        tile_folder = choose_random_tile_folder()
                        tiles = load_tiles(tile_folder)
                        shuffled_order = generate_shuffled_order()
                    elif event.key == pygame.K_h:
                        showing_help = not showing_help
                    elif not mic_active:
                        if event.key == pygame.K_UP:
                            shuffled_order = move_empty(shuffled_order, "up")
                            last_voice_command = "up"
                        elif event.key == pygame.K_DOWN:
                            shuffled_order = move_empty(shuffled_order, "down")
                            last_voice_command = "down"
                        elif event.key == pygame.K_LEFT:
                            shuffled_order = move_empty(shuffled_order, "left")
                            last_voice_command = "left"
                        elif event.key == pygame.K_RIGHT:
                            shuffled_order = move_empty(shuffled_order, "right")
                            last_voice_command = "right"

        try:
            if mic_active:
                inp = get_audio_input()
                if inp:
                    voice_command = normalize_answer(inp)
                    last_voice_command = voice_command
                    if "بالا" in voice_command:
                        shuffled_order = move_empty(shuffled_order, "up")
                    elif "پایین" in voice_command:
                        shuffled_order = move_empty(shuffled_order, "down")
                    elif "چپ" in voice_command:
                        shuffled_order = move_empty(shuffled_order, "left")
                    elif "راست" in voice_command:
                        shuffled_order = move_empty(shuffled_order, "right")
        except queue.Empty:
            pass
        
        if not game_won and is_solved(shuffled_order):
            game_won = True
            stop_listening(wait_for_stop=False)
            pygame.mixer.music.load(WIN_MUSIC_PATH)
            pygame.mixer.music.play() 


        if showing_help:
            hfont = pygame.font.Font(base_dir+"/assets/Vazirmatn-Regular.ttf", 10)
            draw_help_screen(screen, hfont)
            continue 
        
        screen.fill((255,255,255))
        screen.blit(refresh_icon, REFRESH_BUTTON_POS)
        if mic_active:
            screen.blit(mic_icon, mic_icon_rect.topleft)
        else:
            screen.blit(mic_icon, mic_icon_rect.topleft)
            pygame.draw.line(screen, (255, 0, 0), mic_icon_rect.topleft, mic_icon_rect.bottomright, 3)

        draw_grid(screen, tiles, shuffled_order)
        
        reshaped_text = arabic_reshaper.reshape(last_voice_command)
        bidi_text = get_display(reshaped_text)
        rendered = font.render(bidi_text, True,(0, 200, 250))
        screen.blit(rendered, (10, HEADER_HEIGHT - 50))


        if game_won:
            draw_win(screen,win_image)
            continue  

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
