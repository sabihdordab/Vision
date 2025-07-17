import pygame
import os
import random

base_dir = os.path.dirname(os.path.abspath(__file__))
TILES_BASE_FOLDER = os.path.join(base_dir, "tiles")  
ICON_PATH = os.path.join(base_dir, "assets", "refresh.png")

GRID_SIZE = 3
TILE_SIZE = 100
HEADER_HEIGHT = 50
WINDOW_WIDTH = GRID_SIZE * TILE_SIZE
WINDOW_HEIGHT = GRID_SIZE * TILE_SIZE + HEADER_HEIGHT

REFRESH_BUTTON_POS = (WINDOW_WIDTH - 50, 10)
REFRESH_BUTTON_SIZE = (32, 32)

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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("8 Puzzle")

    refresh_icon = pygame.image.load(ICON_PATH)
    refresh_icon = pygame.transform.scale(refresh_icon, REFRESH_BUTTON_SIZE)

    tile_folder = choose_random_tile_folder()
    tiles = load_tiles(tile_folder)
    shuffled_order = generate_shuffled_order()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if is_refresh_clicked(event.pos):
                    tile_folder = choose_random_tile_folder()
                    tiles = load_tiles(tile_folder)
                    shuffled_order = generate_shuffled_order()

        screen.fill((30, 30, 30))
        screen.blit(refresh_icon, REFRESH_BUTTON_POS)
        draw_grid(screen, tiles, shuffled_order)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
