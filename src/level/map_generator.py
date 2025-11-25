import random
from src.settings import TILESIZE

class MapGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [['x' for _ in range(width)] for _ in range(height)]
        self.rooms = []

    def generate(self, is_boss=False):
        if is_boss:
            return self.generate_arena()

        # 1. Create Rooms
        attempts = 0
        while len(self.rooms) < 8 and attempts < 100:
            w = random.randint(5, 12)
            h = random.randint(5, 12)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = Rect(x, y, w, h)

            failed = False
            for other in self.rooms:
                if new_room.intersect(other):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                self.rooms.append(new_room)

            attempts += 1

        # 2. Connect Rooms
        for i in range(1, len(self.rooms)):
            # Connect current room to previous room
            self.connect_rooms(self.rooms[i-1], self.rooms[i])

        # 3. Place Entities
        return self.place_entities()

    def create_room(self, room):
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                self.grid[y][x] = ' ' # Space

    def connect_rooms(self, room_a, room_b):
        # Get center points
        cx1 = room_a.x + room_a.w // 2
        cy1 = room_a.y + room_a.h // 2
        cx2 = room_b.x + room_b.w // 2
        cy2 = room_b.y + room_b.h // 2

        # Horizontal then Vertical
        if random.choice([True, False]):
            self.create_h_tunnel(cx1, cx2, cy1)
            self.create_v_tunnel(cy1, cy2, cx2)
        else:
            self.create_v_tunnel(cy1, cy2, cx1)
            self.create_h_tunnel(cx1, cx2, cy2)

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = ' '
            self.grid[y+1][x] = ' ' # Wide corridors?

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = ' '
            self.grid[y][x+1] = ' '

    def generate_arena(self):
        # Create one giant room
        margin = 5
        room = Rect(margin, margin, self.width - margin*2, self.height - margin*2)
        self.create_room(room)
        self.rooms.append(room)

        # Place Player (Bottom Center)
        self.grid[self.height - margin - 2][self.width // 2] = 'p'

        # Place Boss (Top Center)
        self.grid[margin + 2][self.width // 2] = 'B'

        return ["".join(row) for row in self.grid]

    def place_entities(self):
        # Convert grid to list of strings for compatibility
        # But first, place special tiles

        # Player in first room
        start_room = self.rooms[0]
        self.grid[start_room.y + start_room.h // 2][start_room.x + start_room.w // 2] = 'p'

        # Shop in last room (or random) - NO SHOP IN STAGES, only Hub
        # shop_room = self.rooms[-1]
        # self.grid[shop_room.y + shop_room.h // 2][shop_room.x + shop_room.w // 2] = 'S'

        # Enemies in other rooms
        for room in self.rooms[1:]: # Start from room 1 (skip player room)
            num_enemies = random.randint(1, 3)
            for _ in range(num_enemies):
                ex = random.randint(room.x + 1, room.x + room.w - 2)
                ey = random.randint(room.y + 1, room.y + room.h - 2)
                if self.grid[ey][ex] == ' ':
                    self.grid[ey][ex] = 'e'

        return ["".join(row) for row in self.grid]

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def intersect(self, other):
        return (self.x <= other.x + other.w and self.x + self.w >= other.x and
                self.y <= other.y + other.h and self.y + self.h >= other.y)
