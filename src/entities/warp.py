import pygame
from src.settings import *

class Warp(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((0, 0, 0)) # Black center

        # Neon ring visual handled in draw or via separate entity?
        # Let's just draw on the surface
        pygame.draw.circle(self.image, (0, 255, 255), (TILESIZE//2, TILESIZE//2), TILESIZE//2, 3)
        pygame.draw.circle(self.image, (255, 0, 255), (TILESIZE//2, TILESIZE//2), TILESIZE//2 - 5, 2)

        self.rect = self.image.get_rect(topleft=pos)
        self.is_warp = True # Tag for collision

        # Add a glow effect property for the renderer
        self.glow_color = (0, 100, 255)
        self.glow_surf = pygame.Surface((TILESIZE*2, TILESIZE*2), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surf, (*self.glow_color, 100), (TILESIZE, TILESIZE), TILESIZE)

    def update(self, dt):
        # Pulsate?
        pass
