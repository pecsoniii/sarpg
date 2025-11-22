import pygame
from src.settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type='wall'):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        
        if sprite_type == 'wall':
            self.draw_wall()
        else:
            self.draw_floor()
            
        self.rect = self.image.get_rect(topleft = pos)

    def draw_wall(self):
        # Sci-fi panel wall
        self.image.fill((40, 40, 50))
        pygame.draw.rect(self.image, (60, 60, 70), (2, 2, TILESIZE-4, TILESIZE-4))
        pygame.draw.rect(self.image, (20, 20, 30), (10, 10, TILESIZE-20, TILESIZE-20))
        # Tech lines
        pygame.draw.line(self.image, (0, 255, 255), (TILESIZE//2, 10), (TILESIZE//2, TILESIZE-10), 1)

    def draw_floor(self):
        # Dark grid floor
        self.image.fill((20, 20, 30))
        pygame.draw.rect(self.image, (30, 30, 40), (0, 0, TILESIZE, TILESIZE), 1)
        pygame.draw.circle(self.image, (25, 25, 35), (TILESIZE//2, TILESIZE//2), 2)
