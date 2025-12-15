# tooltip.py

import pygame
from settings import TEXT_COLOR, BACKGROUND_COLOR, FONT_NAME, FONT_SIZE

class Tooltip:
    """
    Displays tooltips for UI elements.
    """
    def __init__(self):
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.text = ''
        self.rect = None

    def draw(self, surface, pos):
        if self.text:
            text_surf = self.font.render(self.text, True, TEXT_COLOR)
            self.rect = text_surf.get_rect()
            self.rect.topleft = (pos[0] + 10, pos[1] + 10)
            pygame.draw.rect(surface, BACKGROUND_COLOR, self.rect.inflate(10, 10))
            surface.blit(text_surf, self.rect)

    def update(self, text):
        self.text = text
