import unittest
import pygame
from src.settings import *
from src.level.level import Level
from src.main import Game
import os

# Dummy joystick for headless testing
class MockJoystick:
    def init(self): pass
    def get_axis(self, axis): return 0.0
    def get_button(self, button): return False
    def get_hat(self, hat): return (0, 0)
    def get_numaxes(self): return 6
    def get_numbuttons(self): return 10

class TestGameLoop(unittest.TestCase):
    def setUp(self):
        # Initialize pygame headless
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((WIDTH, HEIGHT))

    def tearDown(self):
        pygame.quit()

    def test_level_initialization(self):
        """Verify Level creates map and player without error."""
        joysticks = []
        game_data = {
            'credits': 0,
            'base_stats': {'max_health': 100, 'max_speed': 400, 'damage': 10},
            'stage': 0,
            'xp': 0,
            'level': 1,
            'skill_points': 0,
            'skills_unlocked': []
        }
        level = Level(joysticks, game_data)
        self.assertIsNotNone(level.player)
        self.assertIsNotNone(level.visible_sprites)

    def test_game_state_machine(self):
        """Verify Game class initializes states correctly."""
        game = Game()
        self.assertEqual(game.state, 'menu')
        self.assertIsNotNone(game.level)

    def test_game_cycle(self):
        """Run a single update cycle of the level to check for runtime crashes."""
        joysticks = [MockJoystick()]
        game_data = {
            'credits': 0,
            'base_stats': {'max_health': 100, 'max_speed': 400, 'damage': 10},
            'stage': 0,
            'xp': 0,
            'level': 1,
            'skill_points': 0,
            'skills_unlocked': []
        }
        level = Level(joysticks, game_data)
        dt = 0.016 # Mock 60fps

        # Simulate update loop
        try:
            level.run(dt)
        except Exception as e:
            self.fail(f"Level.run() raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
