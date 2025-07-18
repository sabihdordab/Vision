import pygame
import os


pygame.init()
TILE_SIZE = 80
GRID_WIDTH = 6
GRID_HEIGHT = 6
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
    "bg": (200, 200, 200),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = BASE_DIR + "/assets/"
MAZE_FILE = os.path.join(BASE_DIR, "mazes.txt")

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

def main():
    mazes = load_mazes_from_file(MAZE_FILE)
    maze_index = 0
    maze = mazes[maze_index]
    player_x, player_y = find_start(maze)

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(COLORS["bg"])
        draw_maze(maze)
        draw_player(player_x, player_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx, dy = handle_input(keys)

        new_x = player_x + dx
        new_y = player_y + dy

        if can_move(maze, new_x, new_y):
            player_x, player_y = new_x, new_y

        if maze[player_y][player_x] == 3:
            print(f"{maze_index + 1} Done")
            result = next_maze(mazes, maze_index)
            if result[0] is not None:
                maze_index, maze, (player_x, player_y) = result
                pygame.time.delay(500)
            else:
                print("Bye")
                running = False

        pygame.display.update()
        clock.tick(10)

    pygame.quit()


if __name__ == "__main__":
    main()