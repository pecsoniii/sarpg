import pygame
from src.settings import *

class MainMenu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font_title = pygame.font.Font(None, 80)
        self.font_sub = pygame.font.Font(None, 40)
        self.active = True

    def input(self, joysticks):
        keys = pygame.key.get_pressed()
        # Keyboard
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            return 'playing'

        # Gamepad
        if len(joysticks) > 0:
            if joysticks[0].get_button(7) or joysticks[0].get_button(0): # Start or A
                return 'playing'

        return 'menu'

    def draw(self):
        self.display_surface.fill(BG_COLOR)

        # Neon Title
        title = self.font_title.render("NEON DRIFTER", True, (0, 255, 255))
        # Glow effect
        glow = self.font_title.render("NEON DRIFTER", True, (0, 100, 100))

        rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.display_surface.blit(glow, rect.move(2, 2))
        self.display_surface.blit(title, rect)

        # Instructions
        msg = "Press SPACE or START to Begin"
        sub = self.font_sub.render(msg, True, WHITE)
        sub_rect = sub.get_rect(center=(WIDTH//2, HEIGHT//2))

        # Pulse alpha
        alpha = (pygame.time.get_ticks() % 1000) / 1000.0
        if alpha > 0.5: alpha = 1.0 - alpha
        alpha *= 510 # map 0-0.5 to 0-255
        sub.set_alpha(int(alpha))

        self.display_surface.blit(sub, sub_rect)

        # Credits
        creds = self.font_sub.render("WASD/L-Stick to Move | Mouse/R-Stick to Aim", True, (100, 100, 100))
        creds_rect = creds.get_rect(center=(WIDTH//2, HEIGHT * 0.8))
        self.display_surface.blit(creds, creds_rect)

class GameOver:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font_title = pygame.font.Font(None, 80)
        self.font_sub = pygame.font.Font(None, 40)
        self.score = 0

    def set_score(self, score):
        self.score = score

    def input(self, joysticks):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            return 'restart'

        if len(joysticks) > 0:
            if joysticks[0].get_button(7) or joysticks[0].get_button(0):
                return 'restart'

        return 'game_over'

    def draw(self):
        # Overlay existing screen (transparent black)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(10) # Slow fade
        overlay.fill((0,0,0))
        self.display_surface.blit(overlay, (0,0))

        # Text
        title = self.font_title.render("GAME OVER", True, (255, 0, 0))
        rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.display_surface.blit(title, rect)

        score_text = self.font_sub.render(f"Credits Collected: {self.score}", True, (255, 215, 0))
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.display_surface.blit(score_text, score_rect)

        retry = self.font_sub.render("Press SPACE/START to Retry", True, WHITE)
        retry_rect = retry.get_rect(center=(WIDTH//2, HEIGHT * 0.7))
        self.display_surface.blit(retry, retry_rect)
