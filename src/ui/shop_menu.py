import pygame
from src.settings import *

class ShopMenu:
    def __init__(self, inventory, player, joysticks):
        self.inventory = inventory
        self.player = player
        self.joysticks = joysticks
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 36)

        # Options
        self.options = [
            {'name': 'Speed Upgrade', 'cost': 100, 'stat': 'speed', 'increase': 1, 'max': 12},
            {'name': 'Damage Upgrade', 'cost': 200, 'stat': 'damage', 'increase': 5, 'max': 50},
            {'name': 'Health Upgrade', 'cost': 150, 'stat': 'max_health', 'increase': 20, 'max': 300},
            {'name': 'Exit', 'cost': 0}
        ]
        self.selection_index = 0
        self.visible = False

        # Cooldown for input to prevent scrolling too fast
        self.input_cooldown = 0

    def toggle(self):
        self.visible = not self.visible
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
            if self.selection_index < 0: self.selection_index = len(self.options) - 1
            if self.selection_index >= len(self.options): self.selection_index = 0
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
        option = self.options[self.selection_index]

        if option['name'] == 'Exit':
            self.toggle()
            return

        if self.inventory.credits >= option['cost']:
            # Apply Upgrade
            success = False

            if option['stat'] == 'speed':
                if self.player.max_speed < option['max']:
                    self.player.max_speed += option['increase']
                    success = True
            elif option['stat'] == 'damage':
                # Damage is stored on projectile, but usually player determines it
                # We need to add a damage stat to player to pass to projectile
                # For now let's hack it or add it to player
                if not hasattr(self.player, 'projectile_damage'):
                    self.player.projectile_damage = 10 # Base

                if self.player.projectile_damage < option['max']:
                    self.player.projectile_damage += option['increase']
                    success = True
            elif option['stat'] == 'max_health':
                if self.player.max_health < option['max']:
                    self.player.max_health += option['increase']
                    self.player.health += option['increase'] # Heal the difference
                    success = True

            if success:
                self.inventory.credits -= option['cost']
                # Increase cost for next time?
                option['cost'] = int(option['cost'] * 1.5)

    def display(self):
        if not self.visible: return

        # Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.display_surface.blit(overlay, (0,0))

        # Title
        title = self.font.render("UPGRADE STATION", True, (255, 215, 0))
        self.display_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Credits
        credits_text = self.font.render(f"Credits: {self.inventory.credits}", True, WHITE)
        self.display_surface.blit(credits_text, (WIDTH // 2 - credits_text.get_width() // 2, 100))

        # Options
        y = 150
        for index, option in enumerate(self.options):
            color = WHITE
            if index == self.selection_index:
                color = (255, 215, 0) # Gold selection

            text_str = option['name']
            if option['cost'] > 0:
                 text_str += f" - {option['cost']} Cr"

            text = self.font.render(text_str, True, color)
            self.display_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 50
