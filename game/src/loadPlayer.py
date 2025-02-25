import pygame
from src.animator import Animator

class LoadPlayer:
    def __init__(self, width, height, animation_cooldown, x, y, scale=1):
        # Initialize the Animator

        self.animations = {
            "idle": {"frames": "game/assets/player/animations/_Idle.png", "loop": True},
            "run": {"frames": "game/assets/player/animations/_Run.png", "loop": True},
            "fall":{"frames":  "game/assets/player/animations/_Fall.png", "loop": True},
            "jump": {"frames": "game/assets/player/animations/_Jump.png", "loop": True},
            "turnAround": {"frames": 'game/assets/player/animations/_TurnAround.png', "loop": False},
            "jump_transition":{"frames":  'game/assets/player/animations/_JumpFallInbetween.png', "loop": False},
            'crouch': {"frames": 'game/assets/player/animations/_Crouch.png', "loop": True},
            'crouch_run': {"frames": 'game/assets/player/animations/_CrouchWalk.png', "loop": True},
            "attack": {"frames": 'game/assets/player/animations/_Attack.png', "loop": False},
            "attack2": {"frames": 'game/assets/player/animations/_Attack2.png', "loop": False}
        }

        self.animator = Animator(x, y, width, height, animation_cooldown, self.animations,scale)
        self.height = height
        self.width = width
        # Kinematic constants
        self.friction = 0.2
        self.speed = 1.4
        self.gravity = 1
        self.jumpForce = -20

        self.isAttacking = False
        self.on_ground = False
        self.isCrouching = False
        self.direction = "right"
        self.new_state = "idle"
        self.smt = 0

        # Physics and movement
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.x = x
        self.y = y

        self.cameraX = 0
        self.cameraY = 0

    def update_animation(self):
        # Simplified state transitions for animations
        if self.isCrouching:
            if abs(self.velocity.x) < 0.1: 
                self.new_state = "crouch"
            else: 
                self.new_state = "crouch_run"
        elif not self.on_ground:  
            self.new_state = "jump" if self.velocity.y < 0 else "fall"
        elif self.isAttacking:
            self.new_state = "attack" if self.smt == 1 else "attack2"
        elif abs(self.velocity.x) > 0.8:
            self.new_state = "run"
        else:
            self.new_state = "idle"

        if self.new_state != self.animator.current_animation:
            self.animator.set_animations_state(self.new_state, self.direction)

    def movement(self,all_tiles ):
        self.acceleration = pygame.Vector2(0, self.gravity)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:  
            self.acceleration.x = self.speed
            self.direction = "right"
        if keys[pygame.K_a]:
            self.acceleration.x = -self.speed
            self.direction = "left"
            

        if keys[pygame.K_SPACE] and self.on_ground:  
            self.velocity.y = self.jumpForce
            self.on_ground = False


        if keys[pygame.K_LCTRL]:
            self.isCrouching = True
            if keys[pygame.K_a]:
                self.acceleration.x = -self.speed * 0.5
                self.direction = "left"
            elif keys[pygame.K_d]:
                self.acceleration.x = self.speed * 0.5
                self.direction = "right"
        else:
            self.isCrouching = False


        if pygame.mouse.get_pressed()[0]:
            self.isAttacking = True
            self.velocity.x = 0


        if self.isAttacking and self.animator.isFinished:
            self.isAttacking = False
            self.animator.isFinished = False
            self.smt = 0 if self.smt == 1 else 1
            print(self.smt)

        self.apply_physics(all_tiles )
        self.update_animation()

    def apply_physics(self, all_tiles = []):
        self.acceleration.x -= self.velocity.x * self.friction
        self.velocity += self.acceleration

        self.position += self.velocity + 0.5 * self.acceleration

        self.check_collision(all_tiles)
        
        self.x, self.y = self.position.x, self.position.y
        self.animator.update_position(self.x, self.y)

    

    def get_rect(self) -> tuple[pygame.Rect, pygame.Rect]:
    # Big red one 
        rect = self.animator.current_animation_frames[0].get_rect()
        rect.topleft = (self.x - self.cameraX, self.y - self.cameraY)

        # The green one 
        rect_offset_x = 10  
        rect_offset_y = 20
        rect_width = self.width - rect_offset_x * 2
        rect_height = self.height - rect_offset_y * 2

        rect2 = pygame.Rect(
            self.position.x + self.width * self.animator.scale // 2 - rect_width // 2,
            self.position.y + self.height * self.animator.scale // 2 - rect_height // 2,
            rect_width,
            self.height + 60
        )
        rect2.topleft = (rect2.x - self.cameraX, rect2.y - self.cameraY)
        return rect, rect2


    def degbug_visual(self, screen):
        player, actual_rect = self.get_rect()
        pygame.draw.rect(screen, (254, 0, 0), player, 1)
        pygame.draw.rect(screen, (0,254,0), actual_rect, 1)
    
    def check_collision(self, tiles):
        _, player_rect = self.get_rect()
        
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

    def update(self, screen, camera_x = 0, camera_y = 0):
        self.cameraX = camera_x
        self.cameraY = camera_y

        self.animator.update(screen, camera_x, camera_y)
        self.degbug_visual(screen)



    def deal_damage(self, enemies):
        hitbox, _ = self.get_rect()
        for enemy in enemies:
            if self.isAttacking:
                if hitbox.colliderect(enemy.get_rect()):
                    enemy.health -= 20


