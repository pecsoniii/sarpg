import math

class XPManager:
    def __init__(self, game_data):
        self.game_data = game_data

    def add_xp(self, amount):
        self.game_data['xp'] += amount
        self.check_level_up()

    def check_level_up(self):
        # Curve: 100 * level^1.5
        needed = self.get_xp_needed(self.game_data['level'])
        if self.game_data['xp'] >= needed:
            self.game_data['xp'] -= needed
            self.game_data['level'] += 1
            self.game_data['skill_points'] += 1
            # Recursively check in case massive XP drop
            self.check_level_up()

    def get_xp_needed(self, level):
        return int(100 * (level ** 1.5))
