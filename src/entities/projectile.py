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

        # Pre-render glow (Projectile is smaller)
        self.glow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surf, (*self.glow_color, 50), (16, 16), 16)

    def draw_projectile(self):
        # Glowing orb
        pygame.draw.circle(self.image, NEON_YELLOW, (8, 8), 4)
        pygame.draw.circle(self.image, WHITE, (8, 8), 2)

    def update(self, dt):
        # Speed needs to be adapted for DT. Originally 12 per frame (60fps) = 720 per sec
        speed_per_sec = 720
        self.rect.x += self.direction.x * speed_per_sec * dt
        self.rect.y += self.direction.y * speed_per_sec * dt
        
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
             self.kill()
            
        self.collision()

    def collision(self):
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                self.kill()
