import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.Surface((64, 64)) 
        self.rect = self.image.get_rect()
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.obstacle_sprites = None # Will be set by child classes or passed in

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        
        self.rect.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.y += self.direction.y * speed
        self.collision('vertical')

    def collision(self, direction):
        if self.obstacle_sprites:
            if direction == 'horizontal':
                for sprite in self.obstacle_sprites:
                    if sprite.rect.colliderect(self.rect):
                        if self.direction.x > 0: # moving right
                            self.rect.right = sprite.rect.left
                        if self.direction.x < 0: # moving left
                            self.rect.left = sprite.rect.right
                            
            if direction == 'vertical':
                for sprite in self.obstacle_sprites:
                    if sprite.rect.colliderect(self.rect):
                        if self.direction.y > 0: # moving down
                            self.rect.bottom = sprite.rect.top
                        if self.direction.y < 0: # moving up
                            self.rect.top = sprite.rect.bottom
