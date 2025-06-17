import pygame
import sys

pygame.init()
pygame.mixer.init()

# ========== Settings ==========
WIDTH, HEIGHT = 900, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Main Menu")
font = pygame.font.Font(None, 24)

# ========== Assets ==========
img = pygame.image.load('assets/eye.gif')
img = pygame.transform.scale(img, (200, 200))
click_sound = pygame.mixer.Sound('assets/click.wav')


# ========== Button Class ==========
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


# ========== Create Buttons ==========
buttons = [
    Button("New Game", (WIDTH // 3, HEIGHT // 3)),
    Button("Instructions", (WIDTH // 3, HEIGHT // 2)),
    Button("Exit", (WIDTH // 3, 2 * HEIGHT // 3)),
]


# ========== Main Loop ==========
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
                            pass  # Start new game
                        elif btn.text == "Instructions":
                            pass  # Show instructions
                        elif btn.text == "Exit":
                            pygame.quit()
                            sys.exit()

        screen.fill(WHITE)
        screen.blit(img, (WIDTH // 2 + 5, HEIGHT // 2 - 100))

        for btn in buttons:
            btn.draw(screen, mouse_pos)

        pygame.display.flip()


if __name__ == "__main__":
    main()
