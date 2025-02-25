from typing import Any
import pygame

class Animator:
    def __init__(self, x, y, width, heigh, animation_cooldown, animations_path, scale = 1):
        self.x = x
        self.y = y
        self.width = width
        self.height = heigh
        self.scale = scale

        self.isFinished = False
        self.lastUpdate = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown
        self.current_frame = 0
        self.animations = self.add_animations(animations_path)


        self.current_animation = "idle"
        self.current_animation_frames = self.animations[self.current_animation]['frames']
        self.direction = "right"


    def add_animations(self, animations: dict[str, dict[str, Any]]):
        loaded = {}
        for key, items in animations.items():
            frames = self.load_frames(items["frames"])
            loaded[key] = {"frames": frames, "loop": items["loop"]}
        return loaded


    def load_frames(self, filename):
        sprite = pygame.image.load(filename).convert_alpha()
        width = sprite.get_width()
        frames = []
    
        animations_steps = width // self.width
        for i in range(animations_steps):
            frame = self.get_sprite(sprite, self.width * i, 1)
            frames.append(frame)
        return frames

    def get_sprite(self, sprite, x, y):
        image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        image.blit(sprite,(0,0), (x, y, self.width, self.height))
        image = pygame.transform.scale(image, (self.width * self.scale, self.height * self.scale))
        image.set_colorkey((0,0,0))
        return image
    
    
    def flip_animation(self, animation):
        get_animation = self.animations[animation]["frames"]
        frames = []
        
        for frame in get_animation:
            smt = pygame.transform.flip(frame, True, False)
            frames.append(smt)
        return frames 
    
    def update(self, screen: pygame.Surface, camera_x = 0, camera_y = 0):
        current_update = pygame.time.get_ticks()

        if current_update - self.lastUpdate >= self.animation_cooldown:

            self.current_frame +=  1 
            if self.current_frame >= len(self.current_animation_frames):
                self.current_frame = 0
                if not self.animations[self.current_animation]["loop"]:
                    self.isFinished = True

            self.lastUpdate = current_update
        screen.blit(self.current_animation_frames[self.current_frame], (self.x - camera_x, self.y - camera_y))
    

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def set_animations_state(self, To: str, direction: str):

        
        self.current_animation = To
        self.current_animation_frames = self.animations[self.current_animation]["frames"]
        self.current_frame = 0
        
        if direction != self.direction:

            if direction == "left":
                self.current_animation_frames = self.flip_animation(self.current_animation)
                self.direction == "left"
            else:
                self.current_animation_frames = self.animations[self.current_animation]
            

            
