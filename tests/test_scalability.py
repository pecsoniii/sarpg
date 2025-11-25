import unittest
import pygame
from src.main import Game
from src.level.level import Level
from src.entities.enemy import Enemy
from src.settings import *

# Dummy joystick for headless testing
class MockJoystick:
    def init(self): pass
    def get_axis(self, axis): return 0.0
    def get_button(self, button): return False
    def get_hat(self, hat): return (0, 0)
    def get_numaxes(self): return 6
    def get_numbuttons(self): return 10

class TestScalability(unittest.TestCase):
    def setUp(self):
        # Initialize pygame headless
        import os
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((WIDTH, HEIGHT))

        self.game_data = {
            'credits': 0,
            'base_stats': {'max_health': 100, 'max_speed': 400, 'damage': 10},
            'stage': 1,
            'xp': 0,
            'level': 1,
            'skill_points': 0,
            'skills_unlocked': [],
            'equipped_mods': {}
        }
        self.joysticks = [MockJoystick()]

    def tearDown(self):
        pygame.quit()

    def test_mass_enemy_spawn(self):
        """Torture Test: Spawn 100 enemies and run update loop."""
        level = Level(self.joysticks, self.game_data)

        # Force clear and spawn 100 enemies
        level.visible_sprites.empty()
        level.attackable_sprites.empty()

        for i in range(100):
            x = (i % 10) * 50
            y = (i // 10) * 50
            Enemy((x, y), [level.visible_sprites, level.attackable_sprites], level.obstacle_sprites, level.create_item)

        self.assertEqual(len(level.attackable_sprites), 100)

        # Run update loop for 60 frames (1 second)
        dt = 0.016
        try:
            for _ in range(60):
                level.run(dt)
        except Exception as e:
            self.fail(f"Torture test failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
