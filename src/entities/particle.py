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
        
    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        self.alpha -= self.decay_rate
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
