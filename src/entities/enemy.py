import pygame
from src.settings import *
from src.entities.entity import Entity
import random

class Enemy(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_item, biome=None):
        super().__init__(groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)

        # Determine visual style based on biome
        self.biome = biome
        self.draw_enemy()

        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.obstacle_sprites = obstacle_sprites
        self.create_item = create_item
        
        # Stats
        self.speed = 2
        self.health = 30
        self.damage = 10
        self.notice_radius = 400
        self.attack_radius = 50
        self.glow_color = NEON_RED
        
        # Pre-render glow
        self.glow_surf = pygame.Surface((TILESIZE*2, TILESIZE*2), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surf, (*self.glow_color, 50), (TILESIZE, TILESIZE), TILESIZE)

        self.player = None 

    def draw_enemy(self):
        w, h = TILESIZE, TILESIZE

        color = NEON_RED

        # Biome Variations
        # Assuming we pass biome dict, let's check keys or something distinct
        # Actually Level passes BIOME dict.
        # Let's guess based on wall_border color or just default red if none.

        if self.biome:
            if self.biome['wall_border'] == (255, 100, 0): # Industrial (Orange)
                color = NEON_ORANGE
                # Square shape
                pygame.draw.rect(self.image, (50, 30, 0), (10, 10, w-20, h-20))
                pygame.draw.rect(self.image, color, (10, 10, w-20, h-20), 2)
                return
            elif self.biome['wall_border'] == (50, 255, 50): # Alien (Green)
                color = NEON_LIME
                # Organic/Blob shape
                pygame.draw.circle(self.image, (20, 50, 20), (w//2, h//2), 20)
                pygame.draw.circle(self.image, color, (w//2, h//2), 20, 2)
                return

        # Default (Neon/Red Spiky)
        points = [
            (w//2, 10), (w-10, h//2), (w//2, h-10), (10, h//2)
        ]
        pygame.draw.polygon(self.image, (20, 0, 0), points)
        pygame.draw.polygon(self.image, color, points, 2)
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
                # Safely iterate collision sprites if available, or fallback to checking groups
                # We know obstacle_sprites is usually passed, but we want to avoid other enemies.
                # Best way is to use the group we are in that contains enemies.
                # Let's iterate through all sprites in the first group (visible) as before, but safely.
                for sprite in self.groups()[0]:
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
        # Drop Scrap
        if random.random() < 0.5:
            self.create_item(self.rect.center, 'scrap')

        # Drop XP
        self.create_item(self.rect.center, 'xp')

    def update(self, dt):
        if self.player:
            self.actions(self.player)
            # Speed 2 per frame -> 120 per sec
            self.move(120 * dt)
