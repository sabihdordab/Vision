import pygame
import os
import cv2
import mediapipe as mp
import threading


pygame.init()
TILE_SIZE = 80
GRID_WIDTH = 6
GRID_HEIGHT = 7
WIDTH = GRID_WIDTH * TILE_SIZE
HEIGHT = GRID_HEIGHT * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

COLORS = {
    "wall": BLACK,
    "path": WHITE,
    "start": BLUE,
    "goal": GREEN,
    "player": RED,
    "bg": (0, 0, 0),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = BASE_DIR + "/assets/"
MAZE_FILE = os.path.join(BASE_DIR, "mazes.txt")

done_sound = pygame.mixer.Sound( ASSETS_DIR + "done.wav")
error_sound = pygame.mixer.Sound( ASSETS_DIR + "error.wav")
camera_img = pygame.image.load(ASSETS_DIR + "camera.png")
exit_img = pygame.image.load(ASSETS_DIR + "exit.png")
help_img = pygame.image.load(ASSETS_DIR + "help.png")

camera_img = pygame.transform.scale(camera_img, (50, 50))
exit_img = pygame.transform.scale(exit_img, (50, 50))
help_img = pygame.transform.scale(help_img, (70, 60))

hand_x, hand_y = 0, 0
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,       
    max_num_hands=1,                
    min_detection_confidence=0.5,   
    min_tracking_confidence=0.5     
)

def load_mazes_from_file(filename):
    mazes = []
    current_maze = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            if line.startswith("#"):
                if current_maze:
                    mazes.append(current_maze)
                    current_maze = []
                continue
            row = list(map(int, line.split()))
            current_maze.append(row)
        if current_maze:
            mazes.append(current_maze)
    return mazes


def draw_maze(maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == 0:
                pygame.draw.rect(screen, BLACK, rect)
            elif tile == 1:
                pygame.draw.rect(screen, WHITE, rect)
            elif tile == 2:
                pygame.draw.rect(screen, BLUE, rect)
            elif tile == 3:
                pygame.draw.rect(screen, GREEN, rect)

def find_start(maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            if tile == 2:
                return x, y

def draw_player(x, y):
    center = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
    pygame.draw.circle(screen, COLORS["player"], center, TILE_SIZE // 3)

def handle_input(keys):
    dx = dy = 0
    if keys[pygame.K_LEFT]:  dx = -1
    if keys[pygame.K_RIGHT]: dx = 1
    if keys[pygame.K_UP]:    dy = -1
    if keys[pygame.K_DOWN]:  dy = 1
    return dx, dy

def can_move(maze, x, y):
    return 0 <= x < len(maze[0]) and 0 <= y < len(maze) and maze[y][x] in [1, 3]


def next_maze(mazes, index):
    index += 1
    if index < len(mazes):
        return index, mazes[index], find_start(mazes[index])
    return None, None, (0, 0)

def show_game_over():
    font = pygame.font.SysFont(None, 72)
    text = font.render("You Won!", True, COLORS["goal"])
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, rect)
    pygame.display.update()
    pygame.time.wait(3000)

def get_hand_frame(cap, hands):
    ret, frame = cap.read()
    if not ret:
        return None
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    return frame

def cvframe_to_pygame(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
    frame = cv2.resize(frame, (160, 120))  
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return frame

def draw_icons(img,pos):

    screen.blit(img,pos)

    img_rect = pygame.Rect(pos[0],pos[1], 50, 50)

    return img_rect

def draw_help():
    screen.fill((240, 240, 240))

    font_title = pygame.font.SysFont("arial", 40, bold=True)
    font_text = pygame.font.SysFont("arial", 15)

    title_surf = font_title.render("Game Instructions", True, (0, 0, 0))
    screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 40))


    instructions = [
        "Game Instructions:",
        "",
        "When the camera is ON:",
        "Solve the maze using your index finger in front of the webcam.",
        "Your finger acts as a virtual joystick to move the player.",
        "",
        "When the camera is OFF:",
        "Use the keyboard arrow keys to move the player manually.",
    ]

    y = 120
    for line in instructions:
        text_surf = font_text.render(line, True, (30, 30, 30))
        screen.blit(text_surf, (50, y))
        y += 35

    return_font = pygame.font.SysFont("arial", 20, bold=True)
    return_text = return_font.render("Press Space to return", True, (0, 0, 255))
    screen.blit(return_text, (75, HEIGHT - 70))




def main():
    mazes = load_mazes_from_file(MAZE_FILE)
    maze_index = 0
    maze = mazes[maze_index]
    start_x, start_y = find_start(maze)
    player_x, player_y = start_x, start_y

    clock = pygame.time.Clock()

    cap = None

    camera_on = False
    camera_pos = (10, HEIGHT - 130)
    exit_pos = (70, HEIGHT - 130)
    help_pos = (120,HEIGHT - 130)

    help_on = False

    running = True

    while running:
        screen.fill(COLORS["bg"])
        draw_maze(maze)
        draw_player(player_x, player_y)

        cam_rect = draw_icons(camera_img,camera_pos)
        exit_rect = draw_icons(exit_img,exit_pos)
        help_rect = draw_icons(help_img,help_pos)

        if not camera_on:
            start_pos1 = camera_pos
            end_pos1 = (camera_pos[0] + 50, camera_pos[1] + 50)
            start_pos2 = (camera_pos[0], camera_pos[1] + 50)
            end_pos2 = (camera_pos[0] + 50, camera_pos[1])

            pygame.draw.line(screen, (255, 0, 0), start_pos1, end_pos1, 4)
            pygame.draw.line(screen, (255, 0, 0), start_pos2, end_pos2, 4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    help_on = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if cam_rect.collidepoint(mx, my):
                    if cap is not None:
                        cap.release()
                        cap = None
                        camera_on = False
                    else:
                        cap = cv2.VideoCapture(0)
                        camera_on = True
                elif exit_rect.collidepoint(mx, my):
                    running = False
                elif help_rect.collidepoint(mx, my):
                    help_on = True
        if help_on:
            draw_help()

        if not camera_on:
            keys = pygame.key.get_pressed()
            dx, dy = handle_input(keys)

        new_x = player_x + dx
        new_y = player_y + dy

        if can_move(maze, new_x, new_y):
            player_x, player_y = new_x, new_y
        else:
            if player_x != start_x and player_y != start_y:
                error_sound.play()

        if maze[player_y][player_x] == 3:
            print(f"{maze_index + 1} Done")
            result = next_maze(mazes, maze_index)
            if result[0] is not None:
                done_sound.play()
                maze_index, maze, (player_x, player_y) = result
                start_x, start_y = player_x, player_y
                pygame.time.delay(500)
            else:
                show_game_over()
                print("Bye")
                running = False
        if camera_on:        
            frame = get_hand_frame(cap, hands)
            if frame is not None:
                hand_surface = cvframe_to_pygame(frame)
                screen.blit(hand_surface, (WIDTH - 160, HEIGHT - 120))

        pygame.display.update()
        clock.tick(10)

    if cap : cap.release()
    hands.close()
    pygame.quit()


if __name__ == "__main__":
    main()