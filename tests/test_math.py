import unittest
import math
import pygame

class TestMath(unittest.TestCase):
    def test_atan2_usage(self):
        """Verify math.atan2 behaves as expected for player rotation logic."""
        # Right
        x, y = 1, 0
        angle = math.degrees(-math.atan2(y, x)) - 90
        self.assertEqual(angle, -90.0)

        # Down
        x, y = 0, 1
        angle = math.degrees(-math.atan2(y, x)) - 90
        self.assertEqual(angle, -180.0) # or 180 depending on wrap

        # Up
        x, y = 0, -1
        angle = math.degrees(-math.atan2(y, x)) - 90
        self.assertEqual(angle, 0.0)

    def test_vector_operations(self):
        """Verify pygame Vector2 behavior used in physics."""
        vec = pygame.math.Vector2(10, 0)
        self.assertEqual(vec.magnitude(), 10)

        normalized = vec.normalize()
        self.assertEqual(normalized.x, 1.0)
        self.assertEqual(normalized.y, 0.0)

if __name__ == '__main__':
    unittest.main()
