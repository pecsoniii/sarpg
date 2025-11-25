import unittest
import pygame
from src.entities.particle import Particle
from src.entities.item import Item

class TestEntities(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Mock groups
        self.dummy_group = pygame.sprite.Group()

    def test_particle_update_dt(self):
        """Verify Particle update accepts dt and decays."""
        p = Particle((0,0), [self.dummy_group], (255, 255, 255))
        initial_alpha = p.alpha

        # Update with 1 second dt
        p.update(1.0)

        # Alpha should decrease significantly (decay_rate * 60)
        # Decay rate is random 10-20, so 600-1200. Alpha starts at 255.
        # It should be dead (killed)
        self.assertFalse(p.alive())

    def test_item_update_dt(self):
        """Verify Item update accepts dt without crashing."""
        item = Item((0,0), [self.dummy_group])
        try:
            item.update(0.016)
        except TypeError:
            self.fail("Item.update() raised TypeError with dt argument")

if __name__ == '__main__':
    unittest.main()
