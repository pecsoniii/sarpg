import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, groups, color):
        super().__init__(groups)
        self.color = color
        self.size = random.randint(3, 6)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center = pos)
        
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.speed = random.randint(2, 5)
        
        self.alpha = 255
        self.decay_rate = random.randint(10, 20)
        
    def update(self, dt):
        # Speed originally 2-5 pixels/frame. 60fps -> 120-300 pixels/sec
        speed_per_sec = self.speed * 60
        self.rect.x += self.direction.x * speed_per_sec * dt
        self.rect.y += self.direction.y * speed_per_sec * dt
        
        # Alpha decay 10-20 per frame. 60fps -> 600-1200 per sec
        decay_per_sec = self.decay_rate * 60
        self.alpha -= decay_per_sec * dt
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
