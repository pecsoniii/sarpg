import pygame
from src.settings import *
from src.entities.entity import Entity
import random

class Enemy(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_item):
        super().__init__(groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.draw_enemy()
        self.rect = self.image.get_rect(topleft = pos)
        self.obstacle_sprites = obstacle_sprites
        self.create_item = create_item
        
        # Stats
        self.speed = 2
        self.health = 30
        self.damage = 10
        self.notice_radius = 400
        self.attack_radius = 50
        self.glow_color = NEON_RED
        
        self.player = None 

    def draw_enemy(self):
        # Draw a Neon Spiky shape
        w, h = TILESIZE, TILESIZE

        # Diamond shape
        points = [
            (w//2, 10), (w-10, h//2), (w//2, h-10), (10, h//2)
        ]
        pygame.draw.polygon(self.image, (20, 0, 0), points)
        pygame.draw.polygon(self.image, NEON_RED, points, 2)

        # Core
        pygame.draw.circle(self.image, WHITE, (w//2, h//2), 4)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
            
        return (distance, direction)

    def get_status(self, player):
        distance, direction = self.get_player_distance_direction(player)
        
        if distance <= self.attack_radius:
            return 'attack'
        elif distance <= self.notice_radius:
            return 'move'
        else:
            return 'idle'

    def actions(self, player):
        if self.player:
            status = self.get_status(player)
            
            if status == 'move':
                # Flocking / Separation logic
                self.direction = self.get_player_distance_direction(player)[1]

                # Avoid other enemies
                separation_vector = pygame.math.Vector2()
                for sprite in self.groups()[0]: # Visible sprites
                    if sprite != self and isinstance(sprite, Enemy):
                         dist = (pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(sprite.rect.center)).magnitude()
                         if dist < TILESIZE and dist > 0:
                             diff = (pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(sprite.rect.center)).normalize()
                             separation_vector += diff

                if separation_vector.magnitude() > 0:
                    self.direction = (self.direction + separation_vector).normalize()

            else:
                self.direction = pygame.math.Vector2()

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()
    
    def die(self):
        self.kill()
        if random.random() < 0.5: # 50% drop rate
            self.create_item(self.rect.center, 'scrap')

    def update(self):
        if self.player:
            self.actions(self.player)
            self.move(self.speed)
