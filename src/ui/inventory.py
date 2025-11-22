import pygame
from src.settings import *

class Inventory:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.items = {'scrap': 0, 'fuel': 0}
        self.credits = 0
        self.visible = False
        
    def toggle(self):
        self.visible = not self.visible
        
    def add_item(self, item_name):
        if item_name in self.items:
            self.items[item_name] += 1
        else:
            self.items[item_name] = 1
            
    def add_credits(self, amount):
        self.credits += amount
            
    def display(self):
        # Semi-transparent background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.display_surface.blit(overlay, (0,0))
        
        # Title
        title = self.font.render("Inventory (Press I to Close)", True, WHITE)
        self.display_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Credits
        credits_text = self.font.render(f"Credits: {self.credits}", True, (255, 215, 0))
        self.display_surface.blit(credits_text, (WIDTH // 2 - credits_text.get_width() // 2, 90))
        
        # Items
        y = 130
        for item, amount in self.items.items():
            text = self.font.render(f"{item}: {amount}", True, WHITE)
            self.display_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 40
