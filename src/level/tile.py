import pygame
from src.settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type='wall', biome=None):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.biome = biome
        
        if not self.biome:
            from src.settings import BIOME_NEON
            self.biome = BIOME_NEON # Default

        if sprite_type == 'wall':
            self.draw_wall()
        else:
            self.draw_floor()
            
        self.rect = self.image.get_rect(topleft = pos)

    def draw_wall(self):
        # Uses Biome colors
        self.image.fill(self.biome['wall'])
        # Border
        pygame.draw.rect(self.image, self.biome['wall_border'], (0,0, TILESIZE, TILESIZE), 2)
        # Inner Detail
        pygame.draw.rect(self.image, (0,0,0), (10, 10, TILESIZE-20, TILESIZE-20))

    def draw_floor(self):
        # Uses Biome colors
        self.image.fill(self.biome['floor'])
        # Detail
        pygame.draw.rect(self.image, self.biome['floor_detail'], (0, 0, TILESIZE, TILESIZE), 1)

    def update(self, dt):
        # Tiles are static
        pass
