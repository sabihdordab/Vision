import pygame
import os


pygame.init()
TILE_SIZE = 80
WIDTH = 6 * TILE_SIZE
HEIGHT = 5 * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = BASE_DIR + "/assets/"
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

mazes = load_mazes_from_file(BASE_DIR+"/mazes.txt")
maze_index = 0
maze = mazes[maze_index]


def draw_maze():
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

def main():
    running = True
    while running:
        screen.fill((200, 200, 200))
        draw_maze()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()