import pygame
from src.settings import *
from src.level.tile import Tile
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.projectile import Projectile
from src.entities.item import Item
from src.entities.particle import Particle
from src.map_data import WORLD_MAP
from src.level.map_generator import MapGenerator
from src.ui.inventory import Inventory
from src.ui.shop_menu import ShopMenu
from src.ui.ui import UI
from src.ui.floating_text import FloatingText
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
    def __init__(self, joysticks):
        self.joysticks = joysticks
        
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
        
        # Shop Menu
        self.shop_menu = ShopMenu(self.inventory, self.player, self.joysticks)

    def create_map(self):
        # Generate random map
        generator = MapGenerator(40, 40)
        self.map_data = generator.generate()

        self.player = None
        enemies = []

        # Clear existing sprites if regenerating
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.attack_sprites.empty()
        self.attackable_sprites.empty()
        self.item_sprites.empty()
        self.shop_sprites.empty()

        for row_index, row in enumerate(self.map_data):
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
                        self.create_projectile,
                        self.joysticks
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
        damage = getattr(self.player, 'projectile_damage', 10)
        Projectile(pos, direction, [self.visible_sprites, self.attack_sprites], self.obstacle_sprites, damage)
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
        
        # Always update shop menu ref if player changed (e.g. death)
        if self.shop_menu.player != self.player:
            self.shop_menu.player = self.player

        if self.game_paused:
            self.inventory.display()
        elif self.shop_menu.visible:
            self.shop_menu.input()
            self.shop_menu.display()
        else:
            self.visible_sprites.update()
            self.attack_sprites.update()
            
            # Projectile -> Enemy
            hits = pygame.sprite.groupcollide(self.attackable_sprites, self.attack_sprites, False, True)
            for enemy, projectiles in hits.items():
                for projectile in projectiles:
                    enemy.take_damage(projectile.damage)
                    self.create_particles(enemy.rect.center, NEON_RED)
                    self.visible_sprites.add_shake(5) 
                    FloatingText(enemy.rect.center, str(projectile.damage), [self.visible_sprites])

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
                
            # Player -> Shop (Interact)
            hits = pygame.sprite.spritecollide(self.player, self.shop_sprites, False)
            if hits:
                # 1. Auto Sell Scrap
                if self.inventory.items['scrap'] > 0:
                    amount = self.inventory.items['scrap']
                    self.inventory.items['scrap'] = 0
                    self.inventory.add_credits(amount * 10)
                    self.create_particles(self.player.rect.center, (255, 215, 0))

                # 2. Open Menu if interaction button pressed (handled via update loop usually, but here we can just auto open or hint)
                # Let's make it auto-open if you stand there? No, that's annoying.
                # Let's say if you hit 'Interact' (I/A). But we are in the update loop.
                # Actually, let's just check for a key press here or assume the player pressed interact.
                # Since we don't have a centralized input manager for "Interact", we'll check keys.
                keys = pygame.key.get_pressed()
                interact = False
                if keys[pygame.K_e]: interact = True

                # Check joystick A button
                if len(self.joysticks) > 0:
                    if self.joysticks[0].get_button(0): interact = True # A button

                if interact and not self.shop_menu.visible:
                     self.shop_menu.toggle()

            # Game Over logic handled in main loop
            pass

    def toggle_menu(self):
        if self.shop_menu.visible:
            self.shop_menu.toggle()
        else:
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
        
        # Grid
        self.grid_surf = pygame.Surface((2 * WIDTH, 2 * HEIGHT), pygame.SRCALPHA)
        self.draw_grid()

    def draw_grid(self):
        # Draw a retro grid
        color = (0, 40, 40)
        gap = 100
        for x in range(0, 2 * WIDTH, gap):
            pygame.draw.line(self.grid_surf, color, (x, 0), (x, 2 * HEIGHT))
        for y in range(0, 2 * HEIGHT, gap):
            pygame.draw.line(self.grid_surf, color, (0, y), (2 * WIDTH, y))

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
            
        # Target Offset (Camera Follow)
        target_x = player.rect.centerx - self.half_width
        target_y = player.rect.centery - self.half_height

        # Simple Lerp (Smooth Camera)
        self.offset.x += (target_x - self.offset.x) * 0.1
        self.offset.y += (target_y - self.offset.y) * 0.1

        # Apply Shake
        render_offset = self.offset + shake_offset

        # Draw Background Grid (Parallax-ish)
        grid_x = -(render_offset.x * 0.5) % 100
        grid_y = -(render_offset.y * 0.5) % 100
        # Just tiling the pre-drawn grid is cleaner but let's just draw lines offset?
        # Actually drawing lines every frame is cheap enough for grid.
        # But let's use the blit method for now.
        # Actually, simpler: just draw lines relative to offset.

        start_x = int(render_offset.x // 100) * 100
        start_y = int(render_offset.y // 100) * 100

        # Draw grid
        for x in range(start_x - 100, start_x + WIDTH + 100, 100):
            pygame.draw.line(self.display_surface, (20, 30, 40),
                             (x - render_offset.x, 0),
                             (x - render_offset.x, HEIGHT))
        for y in range(start_y - 100, start_y + HEIGHT + 100, 100):
            pygame.draw.line(self.display_surface, (20, 30, 40),
                             (0, y - render_offset.y),
                             (WIDTH, y - render_offset.y))
        
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - render_offset

            # Simple Bloom/Glow (Draw scaled up transparent version below)
            # Only for specific entities to save perf
            if hasattr(sprite, 'glow_color'):
                # We can't scale efficiently every frame.
                # Instead, draw a circle of glow color at center.
                radius = sprite.rect.width
                glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*sprite.glow_color, 50), (radius, radius), radius)
                self.display_surface.blit(glow_surf,
                                          (sprite.rect.centerx - render_offset.x - radius,
                                           sprite.rect.centery - render_offset.y - radius),
                                          special_flags=pygame.BLEND_ADD)

            self.display_surface.blit(sprite.image, offset_pos)
