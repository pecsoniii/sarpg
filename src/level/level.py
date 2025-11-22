import pygame
from src.settings import *
from src.level.tile import Tile
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.projectile import Projectile
from src.entities.item import Item
from src.entities.particle import Particle
from src.map_data import WORLD_MAP
from src.ui.inventory import Inventory
from src.ui.ui import UI
import random

class Shop(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((255, 215, 0)) # Gold
        # Label
        font = pygame.font.Font(None, 20)
        text = font.render("SHOP", True, (0,0,0))
        self.image.blit(text, (10, 25))
        self.rect = self.image.get_rect(topleft = pos)

class Level:
    def __init__(self):
        
        # Sprite Groups
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group() 
        self.attackable_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.shop_sprites = pygame.sprite.Group()
        
        # UI
        self.inventory = Inventory()
        self.ui = UI()
        self.game_paused = False
        
        # Sprite Setup
        self.create_map()
        
    def create_map(self):
        self.player = None
        enemies = []
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                if col == 'x':
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'wall')
                elif col == 'p':
                    Tile((x, y), [self.visible_sprites], 'floor') 
                    self.player = Player(
                        (x, y), 
                        [self.visible_sprites], 
                        self.obstacle_sprites,
                        self.create_projectile
                    )
                elif col == 'e':
                    Tile((x, y), [self.visible_sprites], 'floor')
                    enemy = Enemy((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.create_item)
                    enemies.append(enemy)
                elif col == 'S':
                    Tile((x, y), [self.visible_sprites], 'floor')
                    Shop((x, y), [self.visible_sprites, self.shop_sprites])
                else:
                    Tile((x, y), [self.visible_sprites], 'floor')
        
        # Give enemies reference to player
        for enemy in enemies:
            enemy.player = self.player

    def create_projectile(self, pos, direction):
        Projectile(pos, direction, [self.visible_sprites, self.attack_sprites], self.obstacle_sprites)
        self.visible_sprites.add_shake()

    def create_item(self, pos, item_type):
        Item(pos, [self.visible_sprites, self.item_sprites], item_type)
        
    def create_particles(self, pos, color):
        for _ in range(5):
            Particle(pos, [self.visible_sprites], color)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.show_health(self.player.health, self.player.max_health)
        self.ui.show_credits(self.inventory.credits)
        
        if self.game_paused:
            self.inventory.display()
        else:
            self.visible_sprites.update()
            self.attack_sprites.update()
            
            # Projectile -> Enemy
            hits = pygame.sprite.groupcollide(self.attackable_sprites, self.attack_sprites, False, True)
            for enemy, projectiles in hits.items():
                for projectile in projectiles:
                    enemy.take_damage(projectile.damage)
                    self.create_particles(enemy.rect.center, RED)
                    self.visible_sprites.add_shake(5) 

            # Player -> Enemy (Damage)
            hits = pygame.sprite.spritecollide(self.player, self.attackable_sprites, False)
            for enemy in hits:
                self.player.take_damage(enemy.damage)
                self.visible_sprites.add_shake(10) 

            # Player -> Item (Pickup)
            hits = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            for item in hits:
                self.inventory.add_item(item.item_type)
                self.create_particles(self.player.rect.center, (255, 215, 0))
                
            # Player -> Shop (Sell)
            hits = pygame.sprite.spritecollide(self.player, self.shop_sprites, False)
            if hits:
                if self.inventory.items['scrap'] > 0:
                    amount = self.inventory.items['scrap']
                    self.inventory.items['scrap'] = 0
                    self.inventory.add_credits(amount * 10)
                    self.create_particles(self.player.rect.center, (255, 215, 0))

            if self.player.health <= 0:
                self.create_map()

    def toggle_menu(self):
        self.game_paused = not self.game_paused
        self.inventory.toggle()

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        
        # Screen Shake
        self.shake_timer = 0
        self.shake_intensity = 0
        
    def add_shake(self, intensity=2):
        self.shake_intensity = intensity
        self.shake_timer = 10 
        
    def custom_draw(self, player):
        # Shake offset
        shake_offset = pygame.math.Vector2()
        if self.shake_timer > 0:
            self.shake_timer -= 1
            shake_offset.x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_offset.y = random.randint(-self.shake_intensity, self.shake_intensity)
            
        self.offset.x = player.rect.centerx - self.half_width + shake_offset.x
        self.offset.y = player.rect.centery - self.half_height + shake_offset.y
        
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
