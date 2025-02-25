from pytmx import TiledMap, TiledTileLayer
import pygame 

class Map_tiles:
    def __init__(self, tmx_data: TiledMap):
        self.tmx_data = tmx_data
        self.tiles: list[tuple[pygame.Surface, int, int]] = []

    def get_tiles(self) -> list[tuple[pygame.Surface, int, int]]:
        tiles = []
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)

                    if tile:
                      tiles.append((tile, x * self.tmx_data.tilewidth, y  * self.tmx_data.tileheight))

        self.tiles = tiles
        return tiles


    def get_tiles_as_rects(self):
        rects = []
        for tile, x, y in self.tiles:
            rects.append(pygame.Rect(x, y, tile.get_width(), tile.get_width()))
        
        return rects
    

    