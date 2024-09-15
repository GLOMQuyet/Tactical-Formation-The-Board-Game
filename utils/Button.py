import pygame

pygame.init()
WHITE = (255, 255, 255)
FONT = pygame.font.Font('./assets/fonts/Roboto-Bold.ttf', 36)
class Button:
    def __init__(self, text, pos, size, callback):
        self.text = text
        self.pos = pos
        self.size = size
        self.callback = callback
        self.rect = pygame.Rect(pos, size)
        self.hovered = False

    def draw(self, win):
        color = (70, 130, 180) if self.hovered else (65, 105, 225)  # Steel Blue or Royal Blue
        pygame.draw.rect(win, color, self.rect)
        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        win.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.callback()