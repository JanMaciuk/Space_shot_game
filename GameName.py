import pygame
from enum import Enum

"""
Assets credits:
PlayerSprite: https://opengameart.org/content/skull-in-a-ufo-spacecraft
"""

# Variables and constants
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (0, 0, 0) # Black, we are in space
PLAYER_RESCALE = 30
MOVEMENT_SPEED = 3
FPS = 60
OBSTACKLE_COUNT = 5 # The number of obstacles on the screen
ENEMY_COUNT = 2 # The number of enemies on the screen
AMMO_COUNT = 1 # The number of collectable ammo boxes on the screen
main_loop = True

# Initialize the game
pygame.init()
pygame.display.set_caption("Game Name")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


class object_type(Enum):
    OBSTACLE = 1
    ENEMY = 2
    AMMO = 3
    BULLET = 4    # Maybe?
    EXPLOSION = 5 # Maybe?

class playerSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Assets\PlayerSprite.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//PLAYER_RESCALE, self.rect.height//PLAYER_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT-self.rect.height) # Start at the bottom center

    def draw(self):
        screen.blit(self.image, self.rect)

    def moveLeft(self):
        self.rect.x -= MOVEMENT_SPEED

    def moveRight(self):
        self.rect.x += MOVEMENT_SPEED
    
player = playerSprite()
player.draw()

# Begin main game loop
while main_loop:
    # Check for game exit command
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            main_loop = False # this will be the last iteration of the loop

    # Check for player movement
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_LEFT] and player.rect.x > 0:
        player.moveLeft()
    if pressed_keys[pygame.K_RIGHT] and player.rect.x < SCREEN_WIDTH - player.rect.width:
        player.moveRight()
    


    # Draw a new frame
    screen.fill(BACKGROUND_COLOR)
    player.draw()
    pygame.time.Clock().tick(FPS)
    pygame.display.update()


pygame.quit()
