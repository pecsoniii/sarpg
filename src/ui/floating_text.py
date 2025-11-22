import pygame
from src.settings import *

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, pos, text, groups):
        super().__init__(groups)
        font = pygame.font.Font(None, 24)
        self.image = font.render(str(text), True, WHITE)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(0, -1) # float up
        self.alpha = 255
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

    def update(self, dt):
        # Velocity -1 per frame -> -60 per sec
        self.pos.y += -60 * dt
        self.rect.center = self.pos

        # Fade out
        time_alive = pygame.time.get_ticks() - self.spawn_time
        if time_alive > self.lifetime:
            self.kill()
        elif time_alive > self.lifetime * 0.5:
             # Fade
             self.alpha -= 5
             if self.alpha < 0: self.alpha = 0
             self.image.set_alpha(self.alpha)
