import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.Surface((64, 64)) 
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy() # Physics collider
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = None # Will be set by child classes or passed in

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def update(self, dt):
        # Default update, can be overridden or used for dt calc
        pass

    def collision(self, direction):
        if self.obstacle_sprites:
            if direction == 'horizontal':
                for sprite in self.obstacle_sprites:
                    if sprite.rect.colliderect(self.hitbox):
                        if self.direction.x > 0: # moving right
                            self.hitbox.right = sprite.rect.left
                        if self.direction.x < 0: # moving left
                            self.hitbox.left = sprite.rect.right
                            
            if direction == 'vertical':
                for sprite in self.obstacle_sprites:
                    if sprite.rect.colliderect(self.hitbox):
                        if self.direction.y > 0: # moving down
                            self.hitbox.bottom = sprite.rect.top
                        if self.direction.y < 0: # moving up
                            self.hitbox.top = sprite.rect.bottom
