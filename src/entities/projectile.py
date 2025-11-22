import pygame
from src.settings import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups, obstacle_sprites, damage=10):
        super().__init__(groups)
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.draw_projectile()
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction.normalize()
        self.speed = 12
        self.obstacle_sprites = obstacle_sprites
        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000 
        self.glow_color = NEON_YELLOW

    def draw_projectile(self):
        # Glowing orb
        pygame.draw.circle(self.image, NEON_YELLOW, (8, 8), 4)
        pygame.draw.circle(self.image, WHITE, (8, 8), 2)

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
             self.kill()
            
        self.collision()

    def collision(self):
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                self.kill()
