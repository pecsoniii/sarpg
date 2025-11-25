import pygame
from src.settings import *
from src.data.mods import MODS
import random

class ShopMenu:
    def __init__(self, inventory, player, joysticks, game_data):
        self.inventory = inventory
        self.player = player
        self.joysticks = joysticks
        self.game_data = game_data
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 36)

        self.visible = False
        self.selection_index = 0
        self.input_cooldown = 0

        self.generated_items = []
        self.generate_shop_items()

    def generate_shop_items(self):
        self.generated_items = []

        # 1. Consumables
        self.generated_items.append({'type': 'consumable', 'id': 'repair_kit', 'name': 'Repair Kit', 'cost': 50, 'desc': 'Heals 50 HP'})

        # 2. Random Mods (2 slots)
        all_mods = list(MODS.keys())
        for _ in range(2):
            mod_id = random.choice(all_mods)
            mod = MODS[mod_id]
            self.generated_items.append({
                'type': 'mod',
                'id': mod_id,
                'name': mod['name'],
                'cost': mod['cost'],
                'desc': mod['desc']
            })

        self.generated_items.append({'type': 'exit', 'name': 'Exit', 'cost': 0, 'desc': ''})

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.generate_shop_items() # Refresh stock? Or keep persistent per visit?
            # Usually per run or per visit. Let's refresh for now.
            self.selection_index = 0

    def input(self):
        # Only allow input every 200ms
        if pygame.time.get_ticks() - self.input_cooldown < 200:
            return

        keys = pygame.key.get_pressed()

        moved = False

        # Navigation (W/S or Up/Down)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.selection_index -= 1
            moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.selection_index += 1
            moved = True

        if len(self.joysticks) > 0:
            joystick = self.joysticks[0]
            hat = joystick.get_hat(0)
            if hat[1] == 1: # Up
                self.selection_index -= 1
                moved = True
            elif hat[1] == -1: # Down
                self.selection_index += 1
                moved = True

            # Stick navigation
            if joystick.get_numaxes() >= 2:
                axis_y = joystick.get_axis(1)
                if axis_y < -0.5:
                    self.selection_index -= 1
                    moved = True
                elif axis_y > 0.5:
                    self.selection_index += 1
                    moved = True

        if moved:
            if self.selection_index < 0: self.selection_index = len(self.generated_items) - 1
            if self.selection_index >= len(self.generated_items): self.selection_index = 0
            self.input_cooldown = pygame.time.get_ticks()

        # Selection (Space / Enter / A Button)
        select = False
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            select = True

        if len(self.joysticks) > 0:
            joystick = self.joysticks[0]
            if joystick.get_button(0): # A button usually
                select = True

        if select:
            self.input_cooldown = pygame.time.get_ticks()
            self.select_option()

    def select_option(self):
        item = self.generated_items[self.selection_index]

        if item['type'] == 'exit':
            self.toggle()
            return

        if self.inventory.credits >= item['cost']:
            if item['type'] == 'consumable':
                # Add to consumables
                self.game_data['consumables'][item['id']] += 1
                self.inventory.credits -= item['cost']

            elif item['type'] == 'mod':
                # Add to mod inventory if not owned? Or duplicate ok?
                # Let's allow duplicates for selling later maybe?
                self.game_data['mods_inventory'].append(item['id'])
                self.inventory.credits -= item['cost']

                # Auto-equip if slot empty?
                mod_type = MODS[item['id']]['type']
                if self.game_data['equipped_mods'][mod_type] is None:
                    self.game_data['equipped_mods'][mod_type] = item['id']
                    # Apply immediately if player present
                    # (Requires calling apply_player_stats on level again? Or assume next run)
                    # Let's not complicate. Next run/re-enter applies it.

    def display(self):
        if not self.visible: return

        # Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.display_surface.blit(overlay, (0,0))

        # Title
        title = self.font.render("BLACK MARKET", True, (255, 0, 255))
        self.display_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Credits
        credits_text = self.font.render(f"Credits: {self.inventory.credits}", True, WHITE)
        self.display_surface.blit(credits_text, (WIDTH // 2 - credits_text.get_width() // 2, 100))

        # Items
        y = 150
        for index, item in enumerate(self.generated_items):
            color = WHITE
            if index == self.selection_index:
                color = (255, 215, 0) # Gold selection

            text_str = item['name']
            if item['cost'] > 0:
                 text_str += f" - {item['cost']} Cr"

            text = self.font.render(text_str, True, color)
            self.display_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, y))

            # Description if selected
            if index == self.selection_index and item['desc']:
                desc_text = self.font.render(item['desc'], True, (100, 255, 255))
                self.display_surface.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, HEIGHT - 100))

            y += 50
