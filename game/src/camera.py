import pygame
from src.loadPlayer import LoadPlayer


class Camera:
    def __init__(self, screen: pygame.SurfaceType, player: LoadPlayer):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.buffer_width = self.screen_width // 3
        self.buffer_height = self.screen_height //3
        self.percentage = .25

        self.player = player
    def follow(self, map_width, map_height, player_x, player_y, base_ground_height):
        self.camera_x = player_x - (self.screen_width // 2) + 300 
        self.camera_y = player_y - (self.screen_height // 2)

     
        self.camera_x =  min(self.camera_x, map_width - self.screen_width)
        self.camera_y = max(0, min(self.camera_y, base_ground_height - self.screen_height))

        return self.camera_x, self.camera_y


    def apply(self, entity):
        return entity.get_rect().move(-self.camera_x, -self.camera_y)
    
    def draw(self, screen: pygame.Surface, group):
        for element, x, y in group:
            screen.blit(element, (x - self.camera_x , y - self.camera_y))