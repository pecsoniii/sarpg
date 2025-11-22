MODS = {
    'spread_shot': {
        'name': 'Spread Shot',
        'type': 'weapon',
        'desc': 'Fires 3 bullets in a spread',
        'cost': 500,
        'stats': {'damage': -2} # Slightly less damage per bullet
    },
    'rapid_fire': {
        'name': 'Rapid Fire',
        'type': 'weapon',
        'desc': 'Doubles fire rate',
        'cost': 800,
        'stats': {'damage': -4}
    },
    'heavy_plating': {
        'name': 'Heavy Plating',
        'type': 'hull',
        'desc': '+50 HP, -50 Speed',
        'cost': 400,
        'stats': {'max_health': 50, 'max_speed': -50}
    },
    'turbo_boost': {
        'name': 'Turbo Boost',
        'type': 'engine',
        'desc': '+100 Speed, +200 Dash Speed',
        'cost': 600,
        'stats': {'max_speed': 100}
    }
}
