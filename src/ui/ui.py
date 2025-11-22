import pygame
from src.settings import *

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 24)
        
        # Health Bar
        self.health_bar_rect = pygame.Rect(10, 10, 200, 20)
        
    def show_health(self, current, max_amount):
        # Background
        pygame.draw.rect(self.display_surface, (60, 60, 60), self.health_bar_rect)
        
        # Ratio
        current_width = self.health_bar_rect.width * (current / max_amount)
        current_rect = self.health_bar_rect.copy()
        current_rect.width = current_width
        
        # Bar
        color = GREEN if current > 30 else RED
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, WHITE, self.health_bar_rect, 2) # Border

    def show_credits(self, amount):
        text_surf = self.font.render(f"Credits: {amount}", True, (255, 215, 0))
        rect = text_surf.get_rect(topright = (WIDTH - 20, 20))
        
        # Background box
        bg_rect = rect.inflate(10, 10)
        pygame.draw.rect(self.display_surface, (20, 20, 20), bg_rect)
        pygame.draw.rect(self.display_surface, (255, 215, 0), bg_rect, 2)
        
        self.display_surface.blit(text_surf, rect)

    def display(self, player):
        self.show_health(player.health, player.max_health)
        # We need access to inventory for credits. 
        # We can pass it in or store ref. 
        pass # Handled in Level for now via direct call
