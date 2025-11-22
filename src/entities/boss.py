import pygame
import math
import random
from src.settings import *
from src.entities.enemy import Enemy

class Boss(Enemy):
    def __init__(self, pos, groups, obstacle_sprites, create_item, create_projectile, biome, boss_type):
        super().__init__(pos, groups, obstacle_sprites, create_item, biome)
        self.boss_type = boss_type
        self.create_projectile = create_projectile
        self.create_warp = None # Assigned by Level

        # Stats
        self.health = 500
        self.max_health = 500
        self.speed = 3 if boss_type == 2 else 1
        self.attack_cooldown = 1000
        self.last_attack = 0

        # Visuals overwrite
        self.image = pygame.Surface((TILESIZE*2, TILESIZE*2), pygame.SRCALPHA)
        self.hitbox = self.rect.inflate(20, 20) # Big hitbox
        self.rect = self.image.get_rect(center=pos)
        self.draw_boss()

        self.glow_surf = pygame.Surface((TILESIZE*4, TILESIZE*4), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surf, (*self.glow_color, 80), (TILESIZE*2, TILESIZE*2), TILESIZE*2)

    def draw_boss(self):
        w, h = TILESIZE*2, TILESIZE*2
        if self.boss_type == 1: # The Prism (Neon)
            points = [(w//2, 0), (w, h//2), (w//2, h), (0, h//2)]
            pygame.draw.polygon(self.image, (0, 20, 20), points)
            pygame.draw.polygon(self.image, NEON_CYAN, points, 4)
            self.glow_color = NEON_CYAN

        elif self.boss_type == 2: # The Crusher (Industrial)
            pygame.draw.rect(self.image, (50, 20, 0), (0,0,w,h))
            pygame.draw.line(self.image, NEON_ORANGE, (0,0), (w,h), 5)
            pygame.draw.line(self.image, NEON_ORANGE, (w,0), (0,h), 5)
            pygame.draw.rect(self.image, NEON_ORANGE, (0,0,w,h), 4)
            self.glow_color = NEON_ORANGE

        elif self.boss_type == 3: # The Hive Mind (Alien)
            pygame.draw.circle(self.image, (30, 0, 30), (w//2, h//2), w//2)
            pygame.draw.circle(self.image, NEON_LIME, (w//2, h//2), w//2, 4)
            pygame.draw.circle(self.image, NEON_MAGENTA, (w//2, h//2), w//4)
            self.glow_color = NEON_MAGENTA

    def actions(self, player):
        # Boss AI
        current_time = pygame.time.get_ticks()

        if self.boss_type == 1: # Stationary Turret
            self.direction = pygame.math.Vector2(0,0)
            if current_time - self.last_attack > 2000:
                self.last_attack = current_time
                self.fire_pattern_spread()

        elif self.boss_type == 2: # Chaser
            super().actions(player) # Standard chase
            if current_time - self.last_attack > 1500:
                self.last_attack = current_time
                # Dash or fire? Let's fire shotgun
                self.fire_pattern_shotgun()

        elif self.boss_type == 3: # Teleporter (Mock)
            if current_time - self.last_attack > 3000:
                self.last_attack = current_time
                # Teleport random
                self.hitbox.center = (random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100))
                self.rect.center = self.hitbox.center
                self.fire_pattern_circle()

    def fire_pattern_spread(self):
        # Fire 8 bullets in circle
        for i in range(0, 360, 45):
            rad = math.radians(i)
            direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
            self.create_projectile(self.rect.center, direction)

    def die(self):
        super().die() # Drops XP/Scrap
        if self.create_warp:
            self.create_warp(self.rect.center)

    def fire_pattern_shotgun(self):
        if not self.player: return
        # Fire at player
        target = pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)
        if target.magnitude() > 0:
            angle = math.degrees(math.atan2(target.y, target.x))
            for offset in [-20, 0, 20]:
                rad = math.radians(angle + offset)
                direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                self.create_projectile(self.rect.center, direction)

    def fire_pattern_circle(self):
        # Massive circle
        for i in range(0, 360, 20):
            rad = math.radians(i)
            direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
            self.create_projectile(self.rect.center, direction)
