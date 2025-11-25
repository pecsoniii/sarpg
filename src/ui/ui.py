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
        color = NEON_LIME if current > 30 else NEON_RED
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, WHITE, self.health_bar_rect, 2) # Border

    def show_credits(self, amount):
        text_surf = self.font.render(f"Credits: {amount}", True, (255, 215, 0))
        rect = text_surf.get_rect(topright = (WIDTH - 20, 20))
        
        # Background box
        bg_rect = rect.inflate(10, 10)
        pygame.draw.rect(self.display_surface, (20, 20, 20), bg_rect)
        pygame.draw.rect(self.display_surface, (255, 215, 0), bg_rect, 2)
        
    def show_xp(self, level, xp, needed):
        # Level Text
        lvl_surf = self.font.render(f"Lvl {level}", True, WHITE)
        self.display_surface.blit(lvl_surf, (10, 40))

        # Bar
        bar_rect = pygame.Rect(60, 45, 150, 10)
        pygame.draw.rect(self.display_surface, (60, 60, 60), bar_rect)

        ratio = xp / max(1, needed)
        curr_rect = bar_rect.copy()
        curr_rect.width = bar_rect.width * ratio
        pygame.draw.rect(self.display_surface, (0, 255, 255), curr_rect)
        pygame.draw.rect(self.display_surface, WHITE, bar_rect, 1)

    def display(self, player):
        self.show_health(player.health, player.max_health)
        pass
