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

        # Persistent Game Data
        self.game_data = {
            'credits': 0,
            # XP System
            'xp': 0,
            'level': 1,
            'skill_points': 0,
            'skills_unlocked': [],

            # Inventory & Loadout
            'mods_inventory': [], # List of Mod IDs
            'consumables': {'repair_kit': 0},
            'equipped_mods': {
                'weapon': None, # e.g. 'spread_shot'
                'engine': None, # e.g. 'turbo_boost'
                'hull': None    # e.g. 'heavy_plating'
            },

            # Base Stats (modified by Skills/Mods)
            'base_stats': {
                'max_health': 100,
                'max_speed': 400,
                'damage': 10
            },

            'stage': 0 # 0 = Hub
        }

        # States
        self.state = 'menu' # menu, hub, playing, game_over
        self.main_menu = MainMenu()
        self.game_over = GameOver()

        # Initial Level (Hub)
        self.load_level(is_hub=True)

        # Skill Tree Menu (Global overlay for Hub)
        from src.ui.skill_tree import SkillTreeMenu
        self.skill_tree = SkillTreeMenu(self.game_data, self.joysticks)

    def load_level(self, is_hub=True):
        if is_hub:
            self.game_data['stage'] = 0
        else:
            self.game_data['stage'] += 1

        self.level = Level(self.joysticks, self.game_data, is_hub)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Global Menu Toggles
                if self.state in ['playing', 'hub']:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                            self.level.toggle_menu()
                        if event.key == pygame.K_t and self.state == 'hub': # 'T' for Tree
                            self.skill_tree.toggle()

                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 7: # Start button
                            self.level.toggle_menu()
                        if event.button == 6 and self.state == 'hub': # Select/Back button usually
                            self.skill_tree.toggle()
            
            if self.state == 'menu':
                next_state = self.main_menu.input(self.joysticks)
                self.main_menu.draw()
                if next_state == 'playing':
                    self.state = 'hub'
                    self.load_level(is_hub=True)
            
            elif self.state in ['hub', 'playing']:
                dt = self.clock.tick(FPS) / 1000.0
                self.screen.fill(BG_COLOR)

                # Run Level
                result = self.level.run(dt)

                # Draw Skill Tree Overlay (Hub Only)
                if self.state == 'hub' and self.skill_tree.visible:
                    self.skill_tree.input()
                    self.skill_tree.draw()

                # Check Transitions
                if result == 'warp':
                    if self.state == 'hub':
                        self.state = 'playing'
                        self.load_level(is_hub=False)
                    else:
                        # Next Level
                        self.load_level(is_hub=False)

                elif self.level.player.health <= 0:
                    self.state = 'game_over'
                    self.game_over.set_score(self.game_data['credits'])

            elif self.state == 'game_over':
                self.clock.tick(FPS)
                next_state = self.game_over.input(self.joysticks)
                self.game_over.draw()

                if next_state == 'restart':
                    self.state = 'hub'
                    self.load_level(is_hub=True)
            
            else:
                self.clock.tick(FPS)

            pygame.display.update()

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()
