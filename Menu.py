import pygame
import sys
import subprocess

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 200)
RED = (255, 0, 0)

spacing = 50
start_y = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echo Menu")
font = pygame.font.Font("assets/TTOctosquaresItalic.ttf", 15)
title_font = pygame.font.Font("assets/TTOctosquaresExpXBoldIt.ttf", 48)


img = pygame.image.load('assets/girl.png')
img = pygame.transform.scale(img, (200, 200))
click_sound = pygame.mixer.Sound('assets/click.wav')
pygame.mixer.music.load('assets/30 Singularity.mp3') 
pygame.mixer.music.play(-1)


class Button:
    def __init__(self, text, center_pos):
        self.text = text
        self.center = center_pos
        self.size = (150, 40)
        self.rect = pygame.Rect(0, 0, *self.size)
        self.rect.center = self.center

    def draw(self, surface, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = BLUE if is_hovered else BLACK
        pygame.draw.rect(surface, color, self.rect, border_radius=5)

        label = font.render(self.text, True, WHITE)
        label_pos = (
            self.center[0] - label.get_width() // 2,
            self.center[1] - label.get_height() // 2
        )
        surface.blit(label, label_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


buttons = [
    Button("New Game", (WIDTH // 3, HEIGHT // 3)),
    Button("Instructions", (WIDTH // 3, HEIGHT // 2)),
    Button("Exit", (WIDTH // 3, 2 * HEIGHT // 3)),
]

game_imgs = [
    pygame.transform.scale(pygame.image.load("assets/game1.png"), (50, 50)),
    pygame.transform.scale(pygame.image.load("assets/game2.png"), (50, 50)),
]

game_buttons = [
    Button("Text Puzzle", (WIDTH // 2, 150 + 100 + 20)),  
    Button("8 Puzzle", (WIDTH // 2, 300 + 100 + 20)), 
]


def start_game():
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((20, 20, 20))

        title = title_font.render("Select Game", True, RED)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        for i, img in enumerate(game_imgs):
            y_offset = start_y + i * (img.get_height() + 40 + spacing)
            screen.blit(img, (WIDTH // 2 - img.get_width() // 2, y_offset))
            game_buttons[i].center = (WIDTH // 2, y_offset + img.get_height() + 20)
            game_buttons[i].rect.center = game_buttons[i].center
            game_buttons[i].draw(screen, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_buttons[0].is_clicked(mouse_pos):
                    click_sound.play()
                    pygame.time.delay(200)
                    subprocess.run(["python", "puzzle/puzzle_game.py"])
                elif game_buttons[1].is_clicked(mouse_pos):
                    click_sound.play()
                    pygame.time.delay(200)
                    subprocess.run(["python", "puzzle8/game.py"])

        hint_text = font.render("Press Esc to return", True, WHITE)
        hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        screen.blit(hint_text, hint_rect)

        pygame.display.flip()

def main():
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        click_sound.play()
                        pygame.time.delay(300)

                        if btn.text == "New Game":
                            start_game()
                        elif btn.text == "Instructions":
                            pass  
                        elif btn.text == "Exit":
                            pygame.quit()
                            sys.exit()

        screen.fill(WHITE)

        title_label = title_font.render("ECHO", True, RED)
        title_rect = title_label.get_rect(center=(WIDTH // 2, 40))
        screen.blit(title_label, title_rect)

        screen.blit(img, (WIDTH // 2 + 5, HEIGHT // 2 ))

        for btn in buttons:
            btn.draw(screen, mouse_pos)

        pygame.display.flip()


if __name__ == "__main__":
    main()
