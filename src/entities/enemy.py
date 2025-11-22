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
        
        self.player = None 

    def draw_enemy(self):
        # Draw a spiky alien ship
        w, h = TILESIZE, TILESIZE
        pygame.draw.circle(self.image, RED, (w//2, h//2), 20)
        # Spikes
        pygame.draw.polygon(self.image, (150, 0, 0), [(w//2, 0), (w//2+5, 10), (w//2-5, 10)])
        pygame.draw.polygon(self.image, (150, 0, 0), [(w//2, h), (w//2+5, h-10), (w//2-5, h-10)])
        pygame.draw.polygon(self.image, (150, 0, 0), [(0, h//2), (10, h//2+5), (10, h//2-5)])
        pygame.draw.polygon(self.image, (150, 0, 0), [(w, h//2), (w-10, h//2+5), (w-10, h//2-5)])
        # Eye
        pygame.draw.circle(self.image, (255, 255, 0), (w//2, h//2), 8)
        pygame.draw.line(self.image, BLACK, (w//2-5, h//2), (w//2+5, h//2), 2)

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
                self.direction = self.get_player_distance_direction(player)[1]
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
