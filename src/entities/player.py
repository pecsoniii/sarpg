import pygame
import math
from src.settings import *
from src.entities.entity import Entity
from src.entities.projectile import Projectile

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_projectile, joysticks):
        super().__init__(groups)
        # Create a transparent surface for the spaceship
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10, -10) # Smaller collider
        self.obstacle_sprites = obstacle_sprites
        self.joysticks = joysticks
        
        # Redraw the ship
        self.draw_ship()
        
        # Stats
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.create_projectile = create_projectile
        
        # Cooldowns
        self.can_shoot = True
        self.shoot_time = 0
        self.shoot_cooldown = 400
        
        self.invulnerable = False
        self.hurt_time = 0
        self.invulnerability_duration = 500
        
        # Visuals
        self.base_image = self.image.copy() # Store base rotation
        self.angle = 0
        self.glow_color = NEON_CYAN

        # Pre-render glow
        self.glow_surf = pygame.Surface((TILESIZE*2, TILESIZE*2), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surf, (*self.glow_color, 50), (TILESIZE, TILESIZE), TILESIZE)

        # Physics
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.velocity = pygame.math.Vector2(0, 0)
        # Tuning for Pixels/Second (assuming 60fps originally: 0.5 * 60 = 30, etc)
        self.acceleration = 600
        self.friction = 500
        self.max_speed = 400

        # Dash
        self.can_dash = True
        self.dash_time = 0
        self.dash_cooldown = 1000
        self.dash_speed = 1200

    def draw_ship(self):
        # Draw a Neon Fighter
        w, h = TILESIZE, TILESIZE

        # Outline style
        points = [
            (w//2, 5),       # Nose
            (w-10, h-10),    # Right wing tip
            (w//2, h-20),    # Engine center
            (10, h-10)       # Left wing tip
        ]

        # Fill (Dark)
        pygame.draw.polygon(self.image, (0, 20, 20), points)
        # Stroke (Neon)
        pygame.draw.polygon(self.image, NEON_CYAN, points, 2)

        # Cockpit
        pygame.draw.circle(self.image, WHITE, (w//2, h//2), 3)

        # Engine
        pygame.draw.line(self.image, NEON_ORANGE, (w//2, h-20), (w//2, h), 3)

    def input(self):
        keys = pygame.key.get_pressed()

        # 1. Aim Input (Mouse vs Joystick)
        aim_direction = pygame.math.Vector2(0, 0)
        using_mouse = True

        if len(self.joysticks) > 0:
             # Right stick for aim (Axis 2 and 3 usually)
            joystick = self.joysticks[0] # Assume player 1
            if joystick.get_numaxes() >= 4:
                axis_x = joystick.get_axis(2)
                axis_y = joystick.get_axis(3)
                if abs(axis_x) > 0.1 or abs(axis_y) > 0.1:
                    aim_direction = pygame.math.Vector2(axis_x, axis_y)
                    using_mouse = False

        # Mouse Aim Override
        if using_mouse:
             mouse_pos = pygame.mouse.get_pos()
             player_screen_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
             mouse_vec = pygame.math.Vector2(mouse_pos)
             aim_direction = mouse_vec - player_screen_pos

        # Update Rotation
        if aim_direction.magnitude() > 0:
             self.angle = math.degrees(-math.atan2(aim_direction.y, aim_direction.x)) - 90
             self.image = pygame.transform.rotate(self.base_image, int(self.angle))
             # Note: We update rect.center later to match physics pos/hitbox,
             # but for now we keep it centered to avoid jitter before physics update.
             self.rect = self.image.get_rect(center=self.rect.center)

        # 2. Movement Input
        move_vector = pygame.math.Vector2(0, 0)

        # Keyboard
        if keys[pygame.K_w]: move_vector.y = -1
        elif keys[pygame.K_s]: move_vector.y = 1
        if keys[pygame.K_d]: move_vector.x = 1
        elif keys[pygame.K_a]: move_vector.x = -1

        # Joystick Move
        if len(self.joysticks) > 0:
             joystick = self.joysticks[0]
             if joystick.get_numaxes() >= 2:
                axis_x = joystick.get_axis(0)
                axis_y = joystick.get_axis(1)
                if abs(axis_x) > 0.1: move_vector.x = axis_x
                if abs(axis_y) > 0.1: move_vector.y = axis_y

        # Apply Acceleration
        if move_vector.magnitude() > 0:
            move_vector = move_vector.normalize()
            self.velocity += move_vector * self.acceleration
        else:
            # Friction
            if self.velocity.magnitude() > 0:
                self.velocity -= self.velocity.normalize() * self.friction
                if self.velocity.magnitude() < self.friction:
                    self.velocity = pygame.math.Vector2(0,0)

        # Cap Speed
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
            
        self.direction = self.velocity # Entity.move uses self.direction

        # 3. Dash
        should_dash = False
        if keys[pygame.K_SPACE]: should_dash = True
        if len(self.joysticks) > 0:
            joystick = self.joysticks[0]
            if joystick.get_button(4): should_dash = True # L1 / LB
            if joystick.get_numaxes() > 4:
                if joystick.get_axis(4) > 0: should_dash = True # Left Trigger

        if should_dash and self.can_dash and self.velocity.magnitude() > 0:
            self.dash()

        # 4. Shooting
        mouse_buttons = pygame.mouse.get_pressed()
        should_shoot = mouse_buttons[0]
        
        if len(self.joysticks) > 0:
             # Right Trigger (Axis 5) or RB (Button 5)
             joystick = self.joysticks[0]
             if joystick.get_numaxes() > 5:
                 if joystick.get_axis(5) > 0: # Trigger pressed
                     should_shoot = True
             # Check button just in case
             if joystick.get_numbuttons() > 5:
                 if joystick.get_button(5):
                     should_shoot = True

        if should_shoot and self.can_shoot:
            self.shoot(aim_direction)

    def dash(self):
        self.can_dash = False
        self.dash_time = pygame.time.get_ticks()
        # Add big impulse
        if self.velocity.magnitude() > 0:
            self.velocity = self.velocity.normalize() * self.dash_speed

    def shoot(self, direction):
        self.can_shoot = False
        self.shoot_time = pygame.time.get_ticks()
        
        # Check Weapon Mod
        # Note: Player needs access to equipped_mods.
        # For now, let's assume Level passes it or sets a flag.
        # Actually, better to have 'shoot_pattern' strategy.

        if direction.magnitude() > 0:
            # Basic
            self.create_projectile(self.rect.center, direction)

            # Example Mod Logic (Hardcoded for now, ideally modular)
            if hasattr(self, 'weapon_mod') and self.weapon_mod == 'spread_shot':
                # Left/Right angles
                angle = math.degrees(math.atan2(direction.y, direction.x))
                for offset in [-15, 15]:
                    rad = math.radians(angle + offset)
                    new_dir = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                    self.create_projectile(self.rect.center, new_dir)

    def take_damage(self, amount):
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.hurt_time = pygame.time.get_ticks()
            if self.health <= 0:
                self.health = 0

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_shoot:
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

        if not self.can_dash:
            if current_time - self.dash_time >= self.dash_cooldown:
                self.can_dash = True

        if self.invulnerable:
            # Flash effect
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.invulnerable = False
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

    def wave_value(self):
        value = pygame.time.get_ticks()
        if int(value / 20) % 2 == 0: return 255
        else: return 0

    def update(self, dt):
        # 1. Handle Input (updates velocity target, triggers actions)
        self.input(dt)

        # 2. Physics Update (Movement, Collision)
        self.physics_update(dt)

        # 3. Status/Cooldowns
        self.cooldowns()

    def input(self, dt):
        # ... (Existing Input Logic needs to be wrapped or passed dt if needed,
        #      but most input sets flags. Acceleration needs dt)
        keys = pygame.key.get_pressed()

        # Aim Input ... (No dt needed for immediate aim)
        aim_direction = pygame.math.Vector2(0, 0)
        using_mouse = True
        if len(self.joysticks) > 0:
            joystick = self.joysticks[0]
            if joystick.get_numaxes() >= 4:
                axis_x = joystick.get_axis(2)
                axis_y = joystick.get_axis(3)
                if abs(axis_x) > 0.1 or abs(axis_y) > 0.1:
                    aim_direction = pygame.math.Vector2(axis_x, axis_y)
                    using_mouse = False
        if using_mouse:
             mouse_pos = pygame.mouse.get_pos()
             player_screen_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
             mouse_vec = pygame.math.Vector2(mouse_pos)
             aim_direction = mouse_vec - player_screen_pos
        if aim_direction.magnitude() > 0:
             self.angle = math.degrees(-math.atan2(aim_direction.y, aim_direction.x)) - 90
             self.image = pygame.transform.rotate(self.base_image, int(self.angle))
             self.rect = self.image.get_rect(center=self.rect.center)

        # Movement Input
        move_vector = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]: move_vector.y = -1
        elif keys[pygame.K_s]: move_vector.y = 1
        if keys[pygame.K_d]: move_vector.x = 1
        elif keys[pygame.K_a]: move_vector.x = -1
        
        if len(self.joysticks) > 0:
             joystick = self.joysticks[0]
             if joystick.get_numaxes() >= 2:
                axis_x = joystick.get_axis(0)
                axis_y = joystick.get_axis(1)
                if abs(axis_x) > 0.1: move_vector.x = axis_x
                if abs(axis_y) > 0.1: move_vector.y = axis_y

        # Apply Acceleration with DT
        if move_vector.magnitude() > 0:
            move_vector = move_vector.normalize()
            self.velocity += move_vector * self.acceleration * dt
        else:
            # Friction with DT
            if self.velocity.magnitude() > 0:
                friction_amount = self.friction * dt
                if self.velocity.magnitude() < friction_amount:
                     self.velocity = pygame.math.Vector2(0,0)
                else:
                     self.velocity -= self.velocity.normalize() * friction_amount

        # Cap Speed
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        self.direction = self.velocity

        # Dash
        should_dash = False
        if keys[pygame.K_SPACE]: should_dash = True
        if len(self.joysticks) > 0:
            joystick = self.joysticks[0]
            if joystick.get_button(4): should_dash = True
            if joystick.get_numaxes() > 4:
                if joystick.get_axis(4) > 0: should_dash = True

        if should_dash and self.can_dash and self.velocity.magnitude() > 0:
            self.dash()

        # Shooting
        mouse_buttons = pygame.mouse.get_pressed()
        should_shoot = mouse_buttons[0]

        if len(self.joysticks) > 0:
             joystick = self.joysticks[0]
             if joystick.get_numaxes() > 5:
                 if joystick.get_axis(5) > 0: should_shoot = True
             if joystick.get_numbuttons() > 5:
                 if joystick.get_button(5): should_shoot = True

        if should_shoot and self.can_shoot:
            self.shoot(aim_direction)

    def physics_update(self, dt):
        # Apply velocity to position using DT
        if self.velocity.magnitude() != 0:
            # Move X
            self.pos.x += self.velocity.x * dt
            self.hitbox.x = round(self.pos.x)
            self.collision('horizontal')
            self.pos.x = self.hitbox.x

            # Move Y
            self.pos.y += self.velocity.y * dt
            self.hitbox.y = round(self.pos.y)
            self.collision('vertical')
            self.pos.y = self.hitbox.y

            # Sync Visual Rect
            self.rect.center = self.hitbox.center
