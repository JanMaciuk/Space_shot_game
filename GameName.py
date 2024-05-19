from enum import Enum
import random, contextlib, sys, json
with contextlib.redirect_stdout(None):
    import pygame


"""
Assets credits:
Player: https://opengameart.org/content/skull-in-a-ufo-spacecraft
Asteroid1: https://clipart-library.com/clip-art/168-1688863_clip-free-png-images-transparent-free-download-pngmart.htm
Asteroid2: https://www.hiclipart.com/free-transparent-background-png-clipart-dplug
Asteroid3: https://www.pngwing.com/en/free-png-zvitc
Enemy1: https://toppng.com/free-image/enemy-spaceship-sprite-PNG-free-PNG-Images_170745
Enemy2: https://www.anyrgb.com/en-clipart-gqgxl
Enemy3: https://www.kindpng.com/imgv/TohbRh_download-2d-spaceship-png-spaceship-sprite-png-transparent/
Enemy4: https://www.pngwing.com/en/free-png-muhwz
Missile: https://opengameart.org/content/space-shooter-extension-250
"""

'''
TODO features:

Player health and ammo display.
Manage player health.
Add supply boxes.
Save game state to file, main menu process stdin.

Auto difficulty mode, increases with score.
Everything object-oriented.

'''
# Variables and constants
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
PLAYER_RESCALE = 30
MOVEMENT_SPEED = 5
FPS = 60
ASTEROID_SPRITES = [r"Assets\Asteroid1.png", r"Assets\Asteroid2.png", r"Assets\Asteroid3.png"]
ASTEROID_RESCALE = 10
ENEMY_SPRITES = [r"Assets\Enemy1.png", r"Assets\Enemy2.png", r"Assets\Enemy3.png", r"Assets\Enemy4.png"]
ENEMY_RESCALE = 6
DEFAULT_PROFILE_PATH = "default.json"
BACKGROUND_IMAGES = [r"Assets\Bg1.jpg", r"Assets\Bg2.jpg", r"Assets\Bg3.jpeg"]
BACKGROUND_IMAGE = pygame.image.load(BACKGROUND_IMAGES[random.randint(0, len(BACKGROUND_IMAGES)-1)])
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
mainLoop = True
profileFilePath = DEFAULT_PROFILE_PATH
profileDict = None

#Try reading the profile from command line argument
def tryReadProfile() -> bool:
    global profileDict
    try:
        profileDict = json.load(open(profileFilePath, "r"))
        for key in ["Score", "Health", "Ammo", "EnemySpeed", "EnemyHealth", "EnemyCount", "AsteroidCount", "SupplyCount"]:
            if key not in profileDict or not isinstance(profileDict[key], int):
                raise AssertionError()
    except:
        return False
    return True



# Try to read the profile from the command line argument
if len(sys.argv) > 1: 
    profileFilePath = sys.argv[1]
    if not tryReadProfile():
        profileFilePath = DEFAULT_PROFILE_PATH

# If the profile was not loaded, use the default settings
if not profileDict:
    print("No valid profile path passed, using default settings.")
    if not tryReadProfile():
            # Game cannot run without settings, unrecoverable error
            raise FileNotFoundError("Unable to read default profile file, verify the file exists and is correctly formatted.")

# Load the profile settings
playerScore = profileDict["Score"]
PLAYER_HEALTH = profileDict["Health"]
PLAYER_AMMO = profileDict["Ammo"]
ENEMY_TRACKING_SPEED = profileDict["EnemySpeed"]
ENEMY_HEALTH = profileDict["EnemyHealth"]
ASTEROID_DURABILITY = profileDict["AsteroidDurability"]
ENEMY_COUNT = profileDict["EnemyCount"]
ASTEROID_COUNT = profileDict["AsteroidCount"]
SUPPLY_COUNT = profileDict["SupplyCount"]

# Initialize the game
pygame.init()
pygame.display.set_caption("Game Name")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
allSprites = pygame.sprite.Group()

class genericSprite(pygame.sprite.Sprite):
    """
    Generic class for all sprites with basic functionalities that are not type-specific
    """
    def __init__(self) -> None:
        super().__init__()
        self.health = 1

    def draw(self) -> None:
        screen.blit(self.image, self.rect)

    def moveLeft(self) -> None:
        self.rect.x -= MOVEMENT_SPEED

    def moveRight(self) -> None:
        self.rect.x += MOVEMENT_SPEED

    def moveDown(self) -> None:
        self.rect.y += MOVEMENT_SPEED

    def reRollPicture(self) -> None:
        pass   # Will be overridden by objects that change their pictures, avoid isInstance checks

    def takeDamage(self) -> None:
        if self.health <= 1:
            self.positionUp()
        else:
            self.health -= 1
    
    def positionUp(self) -> None:
        '''
        Respawn sprite above the screen.
        '''
        # Change picture (only implemented for some objects)
        self.reRollPicture()
        # Bring the sprite to the top, slighty above the frame.
        self.rect.y = -self.rect.height - random.randint(0, SCREEN_HEIGHT)
        # Move object to random x position
        self.rect.x = random.randint(0, SCREEN_WIDTH-self.rect.width)
        # If the move caused a collision, try again
        while len(pygame.sprite.spritecollide(self, allSprites, False)) > 1:
            self.rect.x = random.randint(0, SCREEN_WIDTH-self.rect.width)
            self.rect.y = -self.rect.height - random.randint(0, SCREEN_HEIGHT)
        
class asteroidSprite(genericSprite):
    def __init__(self) -> None:
        super().__init__()
        self.health = ASTEROID_DURABILITY
        self.positionUp() # Start at the top of the screen and choose a sprite picture

    def reRollPicture(self) -> None:
        #Change the sprite to a random asteroid
        self.health = ASTEROID_DURABILITY  # Reset health as the asteroid respawns
        imageIndex = random.randint(0, len(ASTEROID_SPRITES)-1)
        self.image = pygame.image.load(ASTEROID_SPRITES[imageIndex]).convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//ASTEROID_RESCALE, self.rect.height//ASTEROID_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling

class enemySprite(genericSprite):
    def __init__(self) -> None:
        super().__init__()
        self.health = ENEMY_HEALTH
        self.positionUp() # Start at the top of the screen and choose a sprite picture

    def reRollPicture(self) -> None:
        #Change the sprite to a random enemy
        self.health = ENEMY_HEALTH  # Reset health as the enemy respawns
        imageIndex = random.randint(0, len(ENEMY_SPRITES)-1)
        self.image = pygame.image.load(ENEMY_SPRITES[imageIndex]).convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//ENEMY_RESCALE, self.rect.height//ENEMY_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling

    def moveDown(self) -> None:
        self.rect.y += MOVEMENT_SPEED
        if self.rect.x < player.rect.x-2 and not len(pygame.sprite.spritecollide(self, allSprites, False)) > 1:
            self.rect.x += ENEMY_TRACKING_SPEED
        elif self.rect.x > player.rect.x+2 and not len(pygame.sprite.spritecollide(self, allSprites, False)) > 1:
            self.rect.x -= ENEMY_TRACKING_SPEED

class playerSprite(genericSprite):
    def __init__(self) -> None:
        super().__init__()
        self.health = PLAYER_HEALTH
        self.image = pygame.image.load(r"Assets\Player.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//PLAYER_RESCALE, self.rect.height//PLAYER_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT-self.rect.height) # Start at the bottom center
        self.ammo = PLAYER_AMMO

    def reRollPicture(self) -> None:
        # If this was called on the player, it means he died.
        self.health = 0  # Zero health means a dead player.
        saveProfileQuit()

    def fireMissile(self) -> bool:
        if self.ammo > 0 and missile.rect.y < 0:
            missile.setAbovePlayer()
            self.ammo -= 1
            return True
        return False

    def takeDamage(self) -> None:
        pass #TODO: Implement player damage

class missileSprite(genericSprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load(r"Assets\Missile.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.positionUp() # Start above the screen, invisible
    
    def moveDown(self) -> None:
        self.rect.y -= MOVEMENT_SPEED   # Movement reversed for bullets

    def setAbovePlayer(self) -> None:
        ''' Position missle above player '''
        self.rect.center = (player.rect.centerx, player.rect.centery - player.rect.height)


def saveProfileQuit() -> None:
    ''' 
    Save the current results and settings to the profile file (if its not default)
    Then open the main menu passing current profile path as argument
    '''
    global mainLoop
    mainLoop = False    # Exit the game loop
    #TODO: Save the current results to the profile file


# Initialize the game sprites
player = playerSprite()
player.draw()
missile = missileSprite()
missile.draw()
allSprites.add(missile)
allSprites.add(player)
for _ in range(ASTEROID_COUNT): allSprites.add(asteroidSprite())
for _ in range(ENEMY_COUNT): allSprites.add(enemySprite())


# Begin main game loop
while mainLoop:
    # Check for game exit command
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            saveProfileQuit()

    # Check for player actions
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_LEFT] and player.rect.x > 0:
        player.moveLeft()
    if pressed_keys[pygame.K_RIGHT] and player.rect.x < SCREEN_WIDTH - player.rect.width:
        player.moveRight()
    if pressed_keys[pygame.K_SPACE]:
        player.fireMissile()

    # Move all other sprites down and check if they collided with the player:
    for sprite in allSprites:
        if sprite != player:
            sprite.moveDown()
            if sprite.rect.y > SCREEN_HEIGHT:
                sprite.positionUp()
            if sprite.rect.colliderect(player.rect):
                print("Something collided with the player")
                player.takeDamage()
                sprite.positionUp()
    
    #Check for missile hit:
    for sprite in allSprites:
        if sprite != missile and sprite != player:
            if missile.rect.colliderect(sprite.rect):
                sprite.takeDamage()
                missile.positionUp()


    

    # Draw a new frame
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    allSprites.draw(screen)
    pygame.time.Clock().tick(FPS)
    pygame.display.update()


pygame.quit()
