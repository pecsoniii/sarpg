import pygame
from src.settings import *

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, groups, item_type='scrap'):
        super().__init__(groups)
        self.item_type = item_type
        self.image = pygame.Surface((20, 20))
        
        if item_type == 'scrap':
            self.image.fill((200, 200, 200)) # Silver
        elif item_type == 'fuel':
            self.image.fill((255, 165, 0)) # Orange
            
        self.rect = self.image.get_rect(center=pos)
