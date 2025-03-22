import pygame
import os
import json
import base64


class level_editor:
    def __init__(self, tile_size, screen_x, screen_y):
        self.tile_size = tile_size
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.grid = [[ None for _ in range((screen_y // tile_size) + 1)] for _ in range((screen_x // tile_size) + 1)]
        self.level_layers = {
            "default": self.grid
        }
        self.tiles_layers = {}
        self.current_layer = ""

        self.selected_tile = None
        
        self.panning_tile = False
        self.panning_level = False
        self.old_pos_x = 0
        self.old_pos_y = 0
        self.tile_camera = (0,0)
        self.level_camera = (0,0)

        self.drawing = False
        self.select = False

        self.last_update = pygame.time.get_ticks()

    def sprite_to_grid(self, filename: str):
        if not os.path.exists(filename):
            print("filename is not invalid")
            return
        grid = []
        image = pygame.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()


        for j in range(0, image_width, self.tile_size):  
            row = []
            for i in range(0, image_height, self.tile_size):
                tile = image.subsurface((j, i, self.tile_size, self.tile_size))
                tile = pygame.transform.scale(tile, (self.tile_size, self.tile_size))
                row.append(tile)
            grid.append(row)
        
        return grid
    

    def draw_tileset(self, screen: pygame.Surface, ):

        if self.current_layer not in self.tiles_layers:
            return 
        
        grid = self.sprite_to_grid(self.current_layer) 
        for i, row in enumerate(grid): 
            for j, tile in enumerate(row):
                screen.blit(tile, (i * self.tile_size + self.tile_camera[0], j * self.tile_size + self.tile_camera[1]))
    
    
    
    def draw_editor_grid(self, screen: pygame.Surface):
        for i, row in enumerate(self.grid):
            for j, value in enumerate(row):
                color = "white"
                border = 1

                if self.grid[i][j] != None:
                    screen.blit(value, (i * self.tile_size + self.level_camera[0], j * self.tile_size + self.level_camera[1]))
                else:
                    
                    pygame.draw.rect(screen, color, (i * self.tile_size + self.level_camera[0], j * self.tile_size + self.level_camera[1],  self.tile_size, self.tile_size), border)
    

    def add_sprites(self, sprites = ""):


        valid_sprites = []
        for sprite in sprites:
            if  not os.path.exists(sprite):
                print("filepath invalid please write a valid path to a sprite image", sprite)
                return
            else:
                valid_sprites.append(sprite)


        for sprite in valid_sprites:
            self.tiles_layers[sprite] = self.sprite_to_grid(sprite)

        if sprites:
            self.current_layer = sprites[0]
            

    def handle_panning(self, event, tile_selector: pygame.Rect, level_editor: pygame.Rect):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            self.old_pos_x, self.old_pos_y = event.pos

            if tile_selector.collidepoint(event.pos):
                self.panning_tile = True

            if level_editor.collidepoint(event.pos):
                self.panning_level = True
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            print("we are cooking up")
            self.panning_tile = False
            self.panning_level = False
        elif event.type == pygame.MOUSEMOTION:

            dx,dy = event.pos[0] - self.old_pos_x, event.pos[1] - self.old_pos_y
            friction = 0.5
            if self.panning_tile:
                self.tile_camera = (self.tile_camera[0] + dx * friction, self.tile_camera[1] +  dy * friction)
                print("panning_tile", self.tile_camera, self.old_pos_x, self.old_pos_y, self.panning_level, self.panning_tile)
            
            elif self.panning_level:
                self.level_camera = (self.level_camera[0] + dx * friction, self.level_camera[1] +  dy * friction)
                print("panning_tile", self.level_camera, self.old_pos_x, self.old_pos_y, self.panning_level, self.panning_tile)
            
            self.old_pos_x , self.old_pos_y= event.pos


    def calculate_pos(self, x, y, camera, screen):
        return (
            int((y - camera[1] - screen.topleft[1]) // self.tile_size), 
            int((x - camera[0] - screen.topleft[0]) // self.tile_size)   
        )

    def delete_from_grid(self, event, level_editor: pygame.Rect):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and level_editor.collidepoint(event.pos):
            x, y = event.pos
            grid_y, grid_x = self.calculate_pos(x, y, self.level_camera, level_editor) 
            print("we are here deleting bitch ")
            if self.is_valid_position(grid_x, grid_y, self.grid):
                self.grid[grid_x][grid_y] = None

    def draw(self, event, level_editor: pygame.Rect, tile_selector: pygame.Rect):
       

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and level_editor.collidepoint(event.pos):    
            x, y = event.pos  
            self.drawing = True  
            grid_y, grid_x = self.calculate_pos(x, y, self.level_camera, level_editor) 

            
            # Place a tile immediately on click
            if self.is_valid_position(grid_x, grid_y, self.grid):
                self.grid[grid_x][grid_y] = self.selected_tile

        # Stop drawing when mouse is released
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and level_editor.collidepoint(event.pos):    
            x, y = event.pos  
            self.drawing = False

        # Select a tile from the tile selector
        elif event.type == pygame.MOUSEBUTTONUP and tile_selector.collidepoint(event.pos):    
            x, y = event.pos  
            grid_y, grid_x = self.calculate_pos(x, y, self.tile_camera, tile_selector) 

            if self.is_valid_position(grid_x, grid_y, self.tiles_layers[self.current_layer]):
                self.selected_tile = self.tiles_layers[self.current_layer][grid_x][grid_y]

        # Draw tiles when moving while holding click
        elif event.type == pygame.MOUSEMOTION and self.drawing and level_editor.collidepoint(event.pos):    
            x, y = event.pos  
            grid_y, grid_x = self.calculate_pos(x, y, self.level_camera, level_editor) 

            if self.is_valid_position(grid_x, grid_y, self.grid):
                self.grid[grid_x][grid_y] = self.selected_tile


    def is_valid_position(self, x, y, grid):
        return 0 <= y < len(grid[0]) and 0 <= x < len(grid)

    def handle_select(self , event, screen: pygame.Rect):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and screen.collidepoint(event.pos):
                self.old_pos_x, self.old_pos_y = event.pos
                self.select = True
                print("are we doing something")
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.select = False

        elif event.type == pygame.MOUSEMOTION and self.select and screen.collidepoint(event.pos):
            dx, dy = event.pos[0] - self.old_pos_x, event.pos[1] - self.old_pos_y


    def export(self):

        json_data = {
            "tile_set" :  "woods.png",
            "layers": []
        }

        for name, grid in self.level_layers.items():
            tiles = []
            for y in range(len(self.grid)):
                for x in range(len(self.grid[0])):
                    if self.grid[y][x] is not None:
                        surface_bites = pygame.image.tostring(grid[y][x], "RGBA")
                        tile = base64.b64encode(surface_bites).decode()
                        tiles.append({"x": x * self.tile_size, "y": y * self.tile_size, "data": tile})
            
            json_data["layers"].append({"name": name, "tiles": tiles})


        with open("export.json", "w") as json_file:
            json.dump(json_data, json_file, indent=4)

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.screen_x, self.screen_y), pygame.SRCALPHA)
        clock = pygame.time.Clock()
        
        run = True

        tile_selection_rect = pygame.Rect(0, 0, int(self.screen_x * 0.3), self.screen_y)
        level_editor_rect = pygame.Rect(int(self.screen_x * 0.3), 0, int(self.screen_x * 0.7), self.screen_y)


        tile_selection = screen.subsurface(tile_selection_rect)
        level_editor = screen.subsurface(level_editor_rect)

       
        self.add_sprites(["woods.png"])
        print(self.current_layer)
        while run: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        print("we are pressing")
                        self.level_camera = (0,0)

                self.draw(event, level_editor_rect, tile_selection_rect)
                self.delete_from_grid(event, level_editor_rect)
                self.handle_panning(event, tile_selection_rect, level_editor_rect)
                self.handle_select(event, level_editor_rect)

            screen.fill("black")
            
           

            pygame.draw.rect(screen, "gray", tile_selection_rect)  
            pygame.draw.rect(screen, "darkgray", level_editor_rect)

            self.draw_tileset(tile_selection)
            self.draw_editor_grid(level_editor) 


            pygame.display.flip()
            clock.tick(60)

editor =  level_editor(24, 1270, 720)

editor.run()
editor.export()



# if event.type == pygame.MOUSEMOTION:
#     x, y = event.pos
#     for surface in windows:
#         if surface.rect.collidepoint(event.pos):
#             hitx = x - surface.rect.x
#             hity = y - surface.rect.y
#             surface.collision(hitx, hity)