import pygame
from src.settings import *
from src.entities.entity import Entity
from src.entities.projectile import Projectile

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_projectile):
        super().__init__(groups)
        # Create a transparent surface for the spaceship
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft = pos)
        self.obstacle_sprites = obstacle_sprites
        
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

    def draw_ship(self):
        # Draw a sci-fi fighter shape
        w, h = TILESIZE, TILESIZE
        # Main fuselage
        pygame.draw.polygon(self.image, GREEN, [
            (w//2, 5),       # Nose
            (w-10, h-10),    # Right wing tip
            (w//2, h-20),    # Engine center
            (10, h-10)       # Left wing tip
        ])
        # Cockpit
        pygame.draw.circle(self.image, (100, 200, 255), (w//2, h//2), 5)
        # Engine glow
        pygame.draw.circle(self.image, (0, 255, 255), (w//2, h-20), 3)

    def input(self):
        keys = pygame.key.get_pressed()

        # Movement (WASD)
        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0
            
        # Shooting (Mouse)
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.can_shoot: # Left click
            self.shoot()

    def rotate_towards_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        player_screen_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        mouse_vec = pygame.math.Vector2(mouse_pos)
        
        rel_x, rel_y = mouse_vec.x - player_screen_pos.x, mouse_vec.y - player_screen_pos.y
        self.angle = (180 / 3.14159) * -pygame.math.atan2(rel_y, rel_x) - 90
        
        self.image = pygame.transform.rotate(self.base_image, int(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        self.can_shoot = False
        self.shoot_time = pygame.time.get_ticks()
        
        mouse_pos = pygame.mouse.get_pos()
        player_screen_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        mouse_vec = pygame.math.Vector2(mouse_pos)
        direction = (mouse_vec - player_screen_pos)
        
        if direction.magnitude() > 0:
            self.create_projectile(self.rect.center, direction)

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

    def update(self):
        self.input()
        self.cooldowns()
        self.move(self.speed)
        # Ideally we rotate, but collision rects get messy with rotation. 
        # For top-down 2D, usually we separate logic-rect and visual-image.
        # For now, let's NOT rotate the collision rect, just the image if possible? 
        # Or just don't rotate the sprite for this quick iteration, just the shooting aim.
        # The user wants polish, so I SHOULD rotate.
        # But updating self.image in update loop handles rotation.
        # NOTE: self.base_image was created in init.
        # Re-drawing base image in case of alpha changes? No, alpha is surface level.
        
        # Fix: Rotate visual only? 
        # If I rotate self.image, I need to reset it from base every frame to avoid quality loss.
        self.image = pygame.transform.rotate(self.base_image, int(self.angle))
        self.rotate_towards_mouse()
