SKILL_TREE = {
    'vitality_1': {
        'name': 'Reinforced Hull I',
        'desc': '+20 Max Health',
        'cost': 1,
        'effect': {'stat': 'max_health', 'value': 20},
        'parent': None,
        'pos': (640, 600) # Bottom Center start
    },
    'vitality_2': {
        'name': 'Reinforced Hull II',
        'desc': '+30 Max Health',
        'cost': 2,
        'effect': {'stat': 'max_health', 'value': 30},
        'parent': 'vitality_1',
        'pos': (540, 500)
    },
    'engine_1': {
        'name': 'Ion Thrusters I',
        'desc': '+50 Max Speed',
        'cost': 1,
        'effect': {'stat': 'max_speed', 'value': 50},
        'parent': 'vitality_1',
        'pos': (740, 500)
    },
    'weapon_1': {
        'name': 'Plasma Overclock',
        'desc': '+5 Damage',
        'cost': 2,
        'effect': {'stat': 'damage', 'value': 5},
        'parent': 'engine_1',
        'pos': (740, 400)
    }
}
