# Game Setup
WIDTH = 1280
HEIGHT = 800 # Steam Deck Native
FPS = 60
TILESIZE = 64

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (10, 10, 20) # Darker for bloom contrast

# Neon Palette
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_LIME = (50, 255, 50)
NEON_ORANGE = (255, 100, 0)
NEON_RED = (255, 20, 20)
NEON_YELLOW = (255, 255, 0)

# Biome Palettes
BIOME_NEON = {
    'wall': (0, 40, 40),
    'wall_border': (0, 255, 255),
    'floor': (10, 10, 20),
    'floor_detail': (20, 30, 40)
}
BIOME_INDUSTRIAL = {
    'wall': (50, 40, 30),
    'wall_border': (255, 100, 0), # Rust/Orange
    'floor': (20, 20, 20),
    'floor_detail': (40, 30, 20)
}
BIOME_ALIEN = {
    'wall': (40, 0, 40),
    'wall_border': (50, 255, 50), # Slime Green
    'floor': (20, 0, 20),
    'floor_detail': (50, 0, 50)
}
