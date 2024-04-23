import pygame
from enum import Enum
import random

"""
Assets credits:
Player: https://opengameart.org/content/skull-in-a-ufo-spacecraft
Asteroid1: https://clipart-library.com/clip-art/168-1688863_clip-free-png-images-transparent-free-download-pngmart.htm
Asteroid2: https://www.hiclipart.com/free-transparent-background-png-clipart-dplug
Asteroid3: https://www.pngwing.com/en/free-png-zvitc
"""

# Variables and constants
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (0, 0, 0) # Black, we are in space
PLAYER_RESCALE = 30
MOVEMENT_SPEED = 4
FPS = 60
ASTEROID_COUNT = 5 # The number of asteroids on the screen
ASTEROID_SPRITES = ["Assets\Asteroid1.png", "Assets\Asteroid2.png", "Assets\Asteroid3.png"]
ASTEROID_RESCALE = 20
ENEMY_COUNT = 2 # The number of enemies on the screen
AMMO_COUNT = 1 # The number of collectable ammo boxes on the screen
main_loop = True

# Initialize the game
pygame.init()
pygame.display.set_caption("Game Name")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


class object_type(Enum):
    ASTEROID = 1
    ENEMY = 2
    AMMO = 3
    BULLET = 4    # Maybe?
    EXPLOSION = 5 # Maybe?

class genericSprite(pygame.sprite.Sprite):
    """
    Generic class for all sprites with basic functionalities that are not type-specific
    """
    def __init__(self):
        super().__init__()

    def draw(self):
        screen.blit(self.image, self.rect)

    def moveLeft(self):
        self.rect.x -= MOVEMENT_SPEED

    def moveRight(self):
        self.rect.x += MOVEMENT_SPEED

    def moveDown(self):
        self.rect.y += MOVEMENT_SPEED
    
    def positionUp(self):
        # Asteroids have a chance to change their picture
        if isinstance(self, asteroidSprite):
            self.reRollPicture()
        # Bring the sprite to the top, slighty above the frame.
        self.rect.y = -self.rect.height
        # Move object to random x position
        self.rect.x = random.randint(0, SCREEN_WIDTH-self.rect.width)
        

class asteroidSprite(genericSprite):
    def __init__(self):
        super().__init__()
        self.positionUp() # Start at the top of the screen and choose a sprite picture

    def reRollPicture(self):
        #Change the sprite to a random asteroid
        imageIndex = random.randint(0, len(ASTEROID_SPRITES)-1)
        self.image = pygame.image.load(ASTEROID_SPRITES[imageIndex]).convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//ASTEROID_RESCALE, self.rect.height//ASTEROID_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling


class playerSprite(genericSprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Assets\Player.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//PLAYER_RESCALE, self.rect.height//PLAYER_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT-self.rect.height) # Start at the bottom center

# Initialize the game sprites
player = playerSprite()
player.draw()
allSprites = pygame.sprite.Group()
allSprites.add(player)
for _ in range(ASTEROID_COUNT): allSprites.add(asteroidSprite())


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

    # Move all sprites except the player and bullets down:
    for sprite in allSprites:
        if sprite != player:
            sprite.moveDown()
            if sprite.rect.y > SCREEN_HEIGHT:
                sprite.positionUp()
    

    # Draw a new frame
    screen.fill(BACKGROUND_COLOR)
    allSprites.draw(screen)
    pygame.time.Clock().tick(FPS)
    pygame.display.update()


pygame.quit()
