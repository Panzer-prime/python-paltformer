import pygame
import math

class Background:
    def __init__(self, width: int, height: int, filenames=[]):
        self.filenames = filenames
        self.width = width
        self.height = height
        self.images = self.load_backgrounds()
        self.scroll = 0

    def load_backgrounds(self) -> list:
        images = []
        for path in self.filenames:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (self.width, self.height))
            images.append(image)
        return images

    def tile_background(self, screen: pygame.Surface, image: pygame.Surface, speed: float) -> None:
        screen_width, _ = screen.get_size()
        image_width, _ = image.get_size()

        offset = (self.scroll * speed) % image_width
        tiles_x = math.ceil(screen_width / image_width) + 1

        for x in range(tiles_x): 
            screen.blit(image, (x * image_width - offset, 0))

    def draw(self, screen: pygame.Surface, velocity_x: int,):
        for i, image in enumerate(self.images):
            speed = 0.2 + i * 0.3 
            self.scroll += velocity_x * speed
            self.tile_background(screen, image, speed)
