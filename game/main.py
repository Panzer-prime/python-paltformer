import pygame
import pygame.camera
from src.loadPlayer import LoadPlayer
from src.backgrounds import Background
from src.camera import Camera
from pytmx.util_pygame import load_pygame
from src.tileset import Map_tiles
from src.enemy import Enemy

SCREEN_WIDTH = 1270
SCREEN_HEIGHT = 720
TILE_SIZE = 24

canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.init()

fps_limit = 60
animation_cooldown = 80

player_path = 'game/assets/player/animations/_TurnAround.png'
player = LoadPlayer( 120, 80, animation_cooldown=animation_cooldown,x= 200,y= 100//2, scale=3)
# player.x , player.y = 200, 400

background_paths = [
    "game/assets/woods/background/background_layer_1.png",
    "game/assets/woods/background/background_layer_2.png",
    "game/assets/woods/background/background_layer_3.png"
]

base_ground_height = 660
background = Background(SCREEN_WIDTH, SCREEN_HEIGHT, background_paths)

tmx_data = load_pygame("game/map/map/newMap.tmx")
game_map = Map_tiles(tmx_data)
tiles  = game_map.get_tiles()
all_tiles = game_map.get_tiles_as_rects()

camera = Camera(screen, player)


enemy = Enemy(400, 100, 150, 100, 2, animation_cooldown)


run = True
while run: 
    clock.tick(fps_limit)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    

    
    cameraX, cameraY = camera.follow(200000, 1000, player.x, player.y,base_ground_height)

    background.draw(screen, player.velocity.x)

    
 
    camera.draw(screen, tiles)
    player.update(screen, cameraX, cameraY)
    player.movement(all_tiles) #ground height 
    # print(player.y -  cameraY, player.y, player.x - cameraX,player.x) 

    enemy.update(cameraX, cameraY, screen, all_tiles)
    
    pygame.display.flip() 
    
    
    
pygame.quit()
    
    
