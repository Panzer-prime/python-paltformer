from src.animator import Animator
import pygame

class Enemy: 
    def __init__(self, x, y, width, height, scale, animation_cooldown):
        self.x = x
        self.y = y

        self.width = width
        self.height = height
        self.scale = scale

        self.animations_paths = {
            "idle":{
                "frames": "game/assets/enemies/Skeleton/idle.png",
                "loop": True
            }
        }
        self.animator = Animator(x, y, width, height, animation_cooldown, self.animations_paths ,scale)


        self.position = pygame.Vector2(x,x)
        self.acceleration = pygame.Vector2(0,0)
        self.velocity = pygame.Vector2(0,0)

               # Kinematic constants
        self.friction = 0.2
        self.speed = 1.4
        self.gravity = 1
        self.jumpForce = -20
    

    def apply_physics(self,all_tiles = [] ):
        self.acceleration = pygame.Vector2(0, self.gravity)
        self.acceleration.x -= self.velocity.x * self.friction
        self.velocity += self.acceleration

        self.position += self.velocity + 0.5 * self.acceleration


        self.check_collision(all_tiles)

    def update(self, camera_x, camera_y, screen,all_tiles ):

        self.cameraX = camera_x
        self.cameraY = camera_y

        self.apply_physics(all_tiles)
        self.degbug_visual(screen)
        self.animator.update(screen, camera_x, camera_y)

             
        self.x, self.y = self.position.x, self.position.y
        self.animator.update_position(self.x, self.y)

    def get_rect(self) -> tuple[pygame.Rect, pygame.Rect]:
        rect:pygame.Rect = self.animator.current_animation_frames[0].get_rect()

        rect.topleft = (self.x - self.cameraX, self.y - self.cameraY )
        rect2 = pygame.Rect(0,0,0,0)
        return rect, rect2

    def degbug_visual(self, screen):
        player, actual_rect = self.get_rect()
        pygame.draw.rect(screen, (254, 0, 0), player, 1)
        pygame.draw.rect(screen, (0,254,0), actual_rect, 1)

    
    def check_collision(self, tiles):
        player_rect,  _= self.get_rect()
        
        allowed_side_overlap = player_rect.width // 2 - 20
        
        for tile in tiles:
            # Adjust tile position for camera
            adjusted_tile = tile.move(-self.cameraX, -self.cameraY)
            
            if player_rect.colliderect(adjusted_tile):

                overlap_left = player_rect.right - adjusted_tile.left
                overlap_right = adjusted_tile.right - player_rect.left
                overlap_top = player_rect.bottom - adjusted_tile.top
                overlap_bottom = adjusted_tile.bottom - player_rect.top
                
                overlaps = [
                    ("left", overlap_left),
                    ("right", overlap_right),
                    ("top", overlap_top),
                    ("bottom", overlap_bottom)
                ]
                collision_side, overlap = min(overlaps, key=lambda x: x[1])
                
                if collision_side == "top" and self.velocity.y > 0:
                    self.position.y -= overlap
                    self.velocity.y = 0
                    self.on_ground = True
                
                elif collision_side == "bottom" and self.velocity.y < 0:
                    self.position.y += overlap
                    self.velocity.y = 0
                
                elif collision_side == "left" and self.velocity.x > 0:

                    if overlap > allowed_side_overlap:
                        self.position.x -= (overlap - allowed_side_overlap)
                        self.velocity.x = 0
                
                elif collision_side == "right" and self.velocity.x < 0:
                    if overlap > allowed_side_overlap:
                        self.position.x += (overlap - allowed_side_overlap)
                        self.velocity.x = 0