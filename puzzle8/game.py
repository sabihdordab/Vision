import pygame
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
TILE_FOLDER = base_dir + "/tiles/i1"  
GRID_SIZE = 3
TILE_SIZE = 100 
WINDOW_SIZE = GRID_SIZE * TILE_SIZE

def load_tiles(tile_folder):
    tiles = []
    for i in range(GRID_SIZE * GRID_SIZE):
        tile_path = os.path.join(tile_folder, f"tile_{i}.png")
        image = pygame.image.load(tile_path)
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        tiles.append(image)
    return tiles

def draw_grid(screen, tiles):
    index = 0
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            screen.blit(tiles[index], (x, y))
            index += 1

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Voice Puzzle - Viewer")

    tiles = load_tiles(TILE_FOLDER)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30)) 
        draw_grid(screen, tiles)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
