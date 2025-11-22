import pygame
import sys
from src.settings import *
from src.level.level import Level
from src.ui.menus import MainMenu, GameOver

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Drifter")
        self.clock = pygame.time.Clock()
        
        # Joystick Init
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in self.joysticks:
            joystick.init()

        # States
        self.state = 'menu' # menu, playing, game_over
        self.main_menu = MainMenu()
        self.game_over = GameOver()
        self.level = Level(self.joysticks)
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Global Menu Toggles (Only in game)
                if self.state == 'playing':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                            self.level.toggle_menu()
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 7: # Start button
                            self.level.toggle_menu()
            
            if self.state == 'menu':
                next_state = self.main_menu.input(self.joysticks)
                self.main_menu.draw()
                if next_state == 'playing':
                    self.state = 'playing'
            
            elif self.state == 'playing':
                self.screen.fill(BG_COLOR)
                self.level.run()

                if self.level.player.health <= 0:
                    self.state = 'game_over'
                    self.game_over.set_score(self.level.inventory.credits)

            elif self.state == 'game_over':
                next_state = self.game_over.input(self.joysticks)
                self.game_over.draw()

                if next_state == 'restart':
                    self.level = Level(self.joysticks) # Restart
                    self.state = 'playing'
            
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
