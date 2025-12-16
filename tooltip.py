import pygame
from settings import TEXT_COLOR, PANEL_BACKGROUND_COLOR

class TooltipManager:
    """Manages contextual tooltips throughout the UI."""
    
    DELAY_MS = 500  # Show tooltip after 500ms hover
    
    def __init__(self, font):
        self.font = font
        self.current_tooltip = None
        self.hover_start = 0
        self.position = (0, 0)
        
    def set(self, text, pos):
        if self.current_tooltip != text:
            self.current_tooltip = text
            self.hover_start = pygame.time.get_ticks()
            self.position = pos
            
    def clear(self):
        self.current_tooltip = None
        self.hover_start = 0
        
    def draw(self, surface):
        if self.current_tooltip is None:
            return
            
        elapsed = pygame.time.get_ticks() - self.hover_start
        if elapsed < self.DELAY_MS:
            return
            
        # Draw tooltip
        text_surf = self.font.render(self.current_tooltip, True, TEXT_COLOR)
        padding = 8
        bg_rect = text_surf.get_rect(topleft=self.position).inflate(padding * 2, padding * 2)
        
        # Ensure tooltip stays on screen
        if bg_rect.right > surface.get_width():
            bg_rect.right = surface.get_width() - 8
        if bg_rect.bottom > surface.get_height():
            bg_rect.bottom = self.position[1] - 8
            
        pygame.draw.rect(surface, (50, 52, 65), bg_rect, border_radius=4)
        pygame.draw.rect(surface, (80, 82, 95), bg_rect, 1, border_radius=4)
        
        text_rect = text_surf.get_rect(center=bg_rect.center)
        surface.blit(text_surf, text_rect)