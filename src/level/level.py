import pygame
from src.settings import *
from src.level.tile import Tile
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.projectile import Projectile
from src.entities.item import Item
from src.entities.particle import Particle
from src.entities.boss import Boss
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

    def update(self, dt):
        pass

class Level:
    def __init__(self, joysticks, game_data, is_hub=False):
        self.joysticks = joysticks
        self.game_data = game_data
        self.is_hub = is_hub
        
        # Sprite Groups
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group() 
        self.attackable_sprites = pygame.sprite.Group()
        self.enemy_attack_sprites = pygame.sprite.Group() # Projectiles hurting player
        self.item_sprites = pygame.sprite.Group()
        self.shop_sprites = pygame.sprite.Group()
        
        # UI
        # Load credits from game_data
        self.inventory = Inventory()
        self.inventory.credits = self.game_data['credits']

        self.ui = UI()
        self.game_paused = False
        
        # Sprite Setup
        if self.is_hub:
            self.setup_hub()
        else:
            self.create_map()

        # Shop Menu
        self.shop_menu = ShopMenu(self.inventory, self.player, self.joysticks, self.game_data)

    def setup_hub(self):
        # Simple static room
        w, h = 20, 15
        self.player = None

        # Create Walls
        for x in range(0, w * TILESIZE, TILESIZE):
            Tile((x, 0), [self.visible_sprites, self.obstacle_sprites], 'wall')
            Tile((x, (h-1) * TILESIZE), [self.visible_sprites, self.obstacle_sprites], 'wall')
        for y in range(0, h * TILESIZE, TILESIZE):
            Tile((0, y), [self.visible_sprites, self.obstacle_sprites], 'wall')
            Tile(((w-1) * TILESIZE, y), [self.visible_sprites, self.obstacle_sprites], 'wall')

        # Floor
        for row in range(1, h-1):
            for col in range(1, w-1):
                 Tile((col * TILESIZE, row * TILESIZE), [self.visible_sprites], 'floor')

        # Player
        self.player = Player(
            (WIDTH//2, HEIGHT//2),
            [self.visible_sprites],
            self.obstacle_sprites,
            self.create_projectile,
            self.joysticks
        )
        # Apply Persistent Stats
        self.apply_player_stats()

        # Shop
        Shop((WIDTH//2 - 200, HEIGHT//2 - 100), [self.visible_sprites, self.shop_sprites])

        # Warp (To Level 1)
        # We need a Warp Entity. For now using a placeholder or creating it in next step.
        # I will assume Warp entity exists or create a placeholder logic here.
        # Let's create a placeholder using a Tile or Item logic for now,
        # but the plan says create src/entities/warp.py next.
        # So I will call self.create_warp() which I'll define.
        self.create_warp((WIDTH//2 + 200, HEIGHT//2))

    def create_map(self):
        # Determine Biome & Boss Status
        stage = self.game_data['stage']

        # 1-3: Area 1 (Neon), 3 is Boss
        # 4-6: Area 2 (Industrial), 6 is Boss
        # 7-9: Area 3 (Alien), 9 is Boss

        is_boss = (stage % 3 == 0)

        from src.settings import BIOME_NEON, BIOME_INDUSTRIAL, BIOME_ALIEN
        biome = BIOME_NEON
        boss_type = 1

        if stage <= 3:
            biome = BIOME_NEON
            boss_type = 1
        elif stage <= 6:
            biome = BIOME_INDUSTRIAL
            boss_type = 2
        else:
            biome = BIOME_ALIEN
            boss_type = 3

        # Generate random map
        generator = MapGenerator(40, 40)
        self.map_data = generator.generate(is_boss=is_boss)

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
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'wall', biome)
                elif col == 'p':
                    Tile((x, y), [self.visible_sprites], 'floor', biome)
                    self.player = Player(
                        (x, y), 
                        [self.visible_sprites], 
                        self.obstacle_sprites,
                        self.create_projectile,
                        self.joysticks
                    )
                elif col == 'e':
                    Tile((x, y), [self.visible_sprites], 'floor', biome)
                    enemy = Enemy((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.create_item, biome)
                    enemies.append(enemy)
                elif col == 'B':
                    Tile((x, y), [self.visible_sprites], 'floor', biome)
                    # Pass create_warp to boss so it can spawn exit on death
                    boss = Boss((x, y), [self.visible_sprites, self.attackable_sprites], self.obstacle_sprites, self.create_item, self.create_enemy_projectile, biome, boss_type)
                    boss.create_warp = self.create_warp
                    enemies.append(boss)
                else:
                    Tile((x, y), [self.visible_sprites], 'floor', biome)
        
        # Apply Persistent Stats
        if self.player:
            self.apply_player_stats()

        # Give enemies reference to player
        for enemy in enemies:
            enemy.player = self.player

        # Spawn Warp
        if not is_boss:
            self.place_warp_in_level()
        # If boss, warp spawns on death (handled in update check or boss die logic)
        # Actually, let's handle Boss death spawning warp in Level.run or Boss.die

    def create_enemy_projectile(self, pos, direction):
        # Boss projectiles
        Projectile(pos, direction, [self.visible_sprites, self.enemy_attack_sprites], self.obstacle_sprites, damage=10)

    def apply_player_stats(self):
        # Start with Base Stats
        base = self.game_data['base_stats']

        self.player.max_speed = base['max_speed']
        self.player.projectile_damage = base['damage']
        self.player.max_health = base['max_health']

        # Apply Mods
        equipped = self.game_data.get('equipped_mods', {})
        from src.data.mods import MODS

        for slot, mod_id in equipped.items():
            if mod_id and mod_id in MODS:
                mod = MODS[mod_id]
                if 'stats' in mod:
                    for stat, val in mod['stats'].items():
                        if stat == 'max_speed': self.player.max_speed += val
                        elif stat == 'damage': self.player.projectile_damage += val
                        elif stat == 'max_health': self.player.max_health += val

                # Apply Logic Flags
                if slot == 'weapon':
                    self.player.weapon_mod = mod_id
                if slot == 'engine':
                    # e.g. boost cooldown logic
                    pass

        if self.is_hub:
            self.player.health = self.player.max_health

    def place_warp_in_level(self):
        # Find a valid spot
        # For now, random
        valid = False
        attempts = 0
        while not valid and attempts < 100:
             row = random.randint(0, len(self.map_data)-1)
             col = random.randint(0, len(self.map_data[0])-1)
             if self.map_data[row][col] == ' ': # Empty floor (space char in generator output?)
                 # Wait, map_data from generator returns strings. ' ' is space/tunnel?
                 # Tile creation loop: ' ' is not handled in the loop above?
                 # Ah, generator returns: 'x' wall, 'p' player, 'e' enemy, 'S' shop.
                 # Where are the empty floors?
                 # Looking at MapGenerator:
                 # self.grid[y][x] = ' ' # Space
                 # In Level.create_map loop:
                 # if col == 'x': wall...
                 # else: floor (Tile created).
                 # So anything not x, p, e, S is floor.
                 # So if it is ' ', it is floor.

                 # Check collision with other sprites?
                 x, y = col * TILESIZE, row * TILESIZE
                 # Just spawn
                 self.create_warp((x, y))
                 valid = True
             attempts += 1

    def create_warp(self, pos):
        from src.entities.warp import Warp
        Warp(pos, [self.visible_sprites, self.shop_sprites])

    def create_projectile(self, pos, direction):
        damage = getattr(self.player, 'projectile_damage', 10)
        Projectile(pos, direction, [self.visible_sprites, self.attack_sprites], self.obstacle_sprites, damage)
        self.visible_sprites.add_shake()

    def create_item(self, pos, item_type):
        Item(pos, [self.visible_sprites, self.item_sprites], item_type)
        
    def create_particles(self, pos, color):
        for _ in range(5):
            Particle(pos, [self.visible_sprites], color)

    def run(self, dt):
        self.visible_sprites.custom_draw(self.player)
        self.ui.show_health(self.player.health, self.player.max_health)
        self.ui.show_credits(self.inventory.credits)
        
        # Show XP
        from src.systems.xp_manager import XPManager
        xp_sys = XPManager(self.game_data)
        self.ui.show_xp(self.game_data['level'], self.game_data['xp'], xp_sys.get_xp_needed(self.game_data['level']))

        # Sync credits back to game_data
        self.game_data['credits'] = self.inventory.credits

        # Sync stats back to game_data (Upgrades)
        if self.player:
            # Note: We shouldn't sync BACK calculated stats if they include Mod modifiers,
            # otherwise they stack infinitely. We should only sync 'base_stats' if they changed (via Shop).
            # But Shop modifies game_data directly.
            # So Level shouldn't overwrite base_stats unless Player gained stats in-level (XP?).
            # Actually, XP manager handles that.
            # So we DON'T sync back base_stats here to avoid corruption.
            pass

        # Always update shop menu ref if player changed (e.g. death)
        if self.shop_menu.player != self.player:
            self.shop_menu.player = self.player

        if self.game_paused:
            self.inventory.display()
        elif self.shop_menu.visible:
            self.shop_menu.input()
            self.shop_menu.display()
        else:
            self.visible_sprites.update(dt)
            self.attack_sprites.update(dt)
            
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

            # Player -> Enemy Projectiles
            hits = pygame.sprite.spritecollide(self.player, self.enemy_attack_sprites, True)
            for projectile in hits:
                self.player.take_damage(projectile.damage)
                self.visible_sprites.add_shake(5)

            # Player -> Item (Pickup)
            hits = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            for item in hits:
                if item.item_type == 'xp':
                    # Handle XP
                    from src.systems.xp_manager import XPManager
                    xp_sys = XPManager(self.game_data)
                    xp_sys.add_xp(10) # 10 XP per orb
                    self.create_particles(self.player.rect.center, (0, 255, 255))
                else:
                    self.inventory.add_item(item.item_type)
                    self.create_particles(self.player.rect.center, (255, 215, 0))

            # Player -> Interactables (Shop / Warp)
            # We are reusing shop_sprites group for Interactables for now
            hits = pygame.sprite.spritecollide(self.player, self.shop_sprites, False)
            if hits:
                for hit in hits:
                    # Check if Warp
                    if hasattr(hit, 'is_warp'):
                        return 'warp'

                    # Check if Shop
                    # 1. Auto Sell Scrap
                    if self.inventory.items['scrap'] > 0:
                        amount = self.inventory.items['scrap']
                        self.inventory.items['scrap'] = 0
                        self.inventory.add_credits(amount * 10)
                        self.create_particles(self.player.rect.center, (255, 215, 0))

                    # 2. Open Menu
                    keys = pygame.key.get_pressed()
                    interact = False
                    if keys[pygame.K_e]: interact = True

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

            # Simple Bloom/Glow (Draw cached surface)
            if hasattr(sprite, 'glow_surf'):
                 # Center the glow surf on the sprite
                 glow_rect = sprite.glow_surf.get_rect(center=sprite.rect.center)
                 glow_pos = glow_rect.topleft - render_offset
                 self.display_surface.blit(sprite.glow_surf, glow_pos, special_flags=pygame.BLEND_ADD)

            self.display_surface.blit(sprite.image, offset_pos)
