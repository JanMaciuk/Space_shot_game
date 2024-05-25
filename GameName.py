import random, contextlib, sys, json, subprocess, ctypes
with contextlib.redirect_stdout(None):
    import pygame


"""
Assets credits:
Player:    https://opengameart.org/content/skull-in-a-ufo-spacecraft
Asteroid1: https://clipart-library.com/clip-art/168-1688863_clip-free-png-images-transparent-free-download-pngmart.htm
Asteroid2: https://www.hiclipart.com/free-transparent-background-png-clipart-dplug
Asteroid3: https://www.pngwing.com/en/free-png-zvitc
Enemy1:    https://toppng.com/free-image/enemy-spaceship-sprite-PNG-free-PNG-Images_170745
Enemy2:    https://www.anyrgb.com/en-clipart-gqgxl
Enemy3:    https://www.kindpng.com/imgv/TohbRh_download-2d-spaceship-png-spaceship-sprite-png-transparent/
Enemy4:    https://www.pngwing.com/en/free-png-muhwz
Missile:   https://opengameart.org/content/space-shooter-extension-250
Heart:     https://www.pngegg.com/en/png-invqg
SupplyBox: https://www.kindpng.com/imgv/hTmRmoh_ammunition-box-commando-ammo-box-pixel-art-hd/
"""


# Variables and constants
SCREEN_WIDTH:int = 1366
SCREEN_HEIGHT:int = 768
PLAYER_RESCALE:int = 30
MOVEMENT_SPEED:int = 5
FPS:int = 60
ASTEROID_SPRITES = [r"Assets\Asteroid1.png", r"Assets\Asteroid2.png", r"Assets\Asteroid3.png"]
ASTEROID_RESCALE:int = 10
SUPPLYBOX_RESCALE:int = 16
ENEMY_SPRITES:list[str] = [r"Assets\Enemy1.png", r"Assets\Enemy2.png", r"Assets\Enemy3.png", r"Assets\Enemy4.png"]
ENEMY_RESCALE:int = 6
DEFAULT_PROFILE_PATH:str = "default.json"
BACKGROUND_IMAGES:list[str] = [r"Assets\Bg1.jpg", r"Assets\Bg2.jpg", r"Assets\Bg3.jpeg"]
BACKGROUND_IMAGE:pygame.Surface = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGES[random.randint(0, len(BACKGROUND_IMAGES)-1)]), (SCREEN_WIDTH, SCREEN_HEIGHT))

class Game():
    def __init__(self) -> None:
        self.displayedAmmo:int = 0
        self.ammoSprites:pygame.sprite.Group = pygame.sprite.Group()
        self.displayedHealth:int = 0
        self.healthSprites:pygame.sprite.Group = pygame.sprite.Group()
        self.doLoop:bool = True
        self.profileFilePath:str = DEFAULT_PROFILE_PATH
        self.profileDict:dict[str, int] = dict()
        # Try to read the profile from the command line argument
        if len(sys.argv) > 1: 
            self.profileFilePath = sys.argv[1]
            if not self.tryReadProfile():
                self.profileFilePath = DEFAULT_PROFILE_PATH

        # If the profile was not loaded, use the default settings
        if not self.profileDict:
            print("No valid profile path passed, using default settings.")
            if not self.tryReadProfile():
                    # Game cannot run without settings, unrecoverable error
                    raise FileNotFoundError("Unable to read default profile file, verify the file exists and is correctly formatted.")
        # Load the profile settings:
        self.playerScore:int = self.profileDict["Score"]
        self.PLAYER_HEALTH:int = self.profileDict["Health"]
        self.PLAYER_AMMO:int = self.profileDict["Ammo"]
        self.ENEMY_TRACKING_SPEED:int = self.profileDict["EnemySpeed"]
        self.ENEMY_HEALTH:int = self.profileDict["EnemyHealth"]
        self.ASTEROID_DURABILITY:int = self.profileDict["AsteroidDurability"]
        self.ENEMY_COUNT:int = self.profileDict["EnemyCount"]
        self.ASTEROID_COUNT:int = self.profileDict["AsteroidCount"]
        self.SUPPLY_COUNT:int = self.profileDict["SupplyCount"]
        self.HEALTH_PROBABILITY:int = self.profileDict["HealthProbability"]
        # Initialize the game
        pygame.init()
        pygame.display.set_caption("Space shot")
        self.screen:pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.allPhysicalSprites:pygame.sprite.Group = pygame.sprite.Group()
        # Initialize the game sprites
        self.player:playerSprite = playerSprite(self)
        self.player.draw()
        self.missile:missileSprite = missileSprite(self)
        self.missile.draw()
        self.allPhysicalSprites.add(self.missile)
        self.allPhysicalSprites.add(self.player)
        for _ in range(self.ASTEROID_COUNT): self.allPhysicalSprites.add(asteroidSprite(self))
        for _ in range(self.ENEMY_COUNT): self.allPhysicalSprites.add(enemySprite(self))
        for _ in range(self.SUPPLY_COUNT): self.allPhysicalSprites.add(supplySprite(self))
        ctypes.windll.user32.SetForegroundWindow(pygame.display.get_wm_info()['window']) # Focus the game window
        self.mainLoop()
    
    def tryReadProfile(self) -> bool:
        try:
            self.profileDict = json.load(open(self.profileFilePath, "r"))
            for key in ["Score", "Health", "Ammo", "EnemySpeed", "EnemyHealth", "EnemyCount", "AsteroidCount", "SupplyCount"]:
                if key not in self.profileDict or not isinstance(self.profileDict[key], int):
                    raise AssertionError()
        except:
            return False
        return True
    
    def mainLoop(self) -> None:
        scoreGiveIn = FPS
        while self.doLoop:
            # Check for game exit command
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.saveProfileQuit()

            # Check for player actions
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_LEFT] and self.player.rect.x > 0:
                self.player.moveLeft()
            if pressed_keys[pygame.K_RIGHT] and self.player.rect.x < SCREEN_WIDTH - self.player.rect.width:
                self.player.moveRight()
            if pressed_keys[pygame.K_SPACE]:
                self.player.fireMissile()

            # Move all other sprites down and check if they collided with the player:
            for sprite in self.allPhysicalSprites:
                if sprite != self.player:
                    sprite.moveDown()
                    if sprite.rect.y > SCREEN_HEIGHT:
                        sprite.positionUp()
                    if sprite.rect.colliderect(self.player.rect):
                        print("Something collided with the player")
                        if not isinstance(sprite, supplySprite):
                            self.player.takeDamage()
                        else:
                            self.player.collectSupplyBox()
                        sprite.positionUp()
            
            #Check for missile hit:
            for sprite in self.allPhysicalSprites:
                if sprite != self.missile and sprite != self.player and self.missile.rect.colliderect(sprite.rect):
                    sprite.takeDamage()
                    self.missile.positionUp()

            #Increase player score
            scoreGiveIn -= 1
            if scoreGiveIn == 0:
                self.playerScore += 1
                scoreGiveIn = FPS

            #Update ammo and health indicators:
            self.updateAmmoIndicator()
            self.updateHealthIndicator()

            # Draw a new frame
            self.screen.blit(BACKGROUND_IMAGE, (0, 0))
            self.allPhysicalSprites.draw(self.screen)
            self.ammoSprites.draw(self.screen)
            self.healthSprites.draw(self.screen)
            pygame.time.Clock().tick(FPS)
            pygame.display.update()

    def saveProfileQuit(self) -> None:
        ''' 
        Save the current results and settings to the profile file (if its not default)
        Then open the main menu passing current profile path as argument
        '''
        self.doLoop = False    # Exit the game loop
        
        if self.profileFilePath != DEFAULT_PROFILE_PATH:    # Nothing to save if not using a profile file
            # Save players statistics, don't change difficulty settings
            self.profileDict["Score"] = self.playerScore
            self.profileDict["Health"] = self.player.health
            self.profileDict["Ammo"] = self.player.ammo
            try:
                with open(self.profileFilePath, "w") as file:
                    json.dump(self.profileDict, file)
            except:
                # Ignore save error, the game is exiting anyway
                print("Debug log: Error saving score, game exiting.")
        # Open the main menu
        subprocess.Popen(["python", "Menu.py", self.profileFilePath])
        pygame.quit()
        sys.exit()

    def updateAmmoIndicator(self) -> None:
        '''Make the displayed ammo match the player's ammo, by adding or deleting ammo sprites'''
        while self.displayedAmmo < self.player.ammo:
            newAmmoSprite = IndicatorSprite(self, r"Assets\Missile.png")
            newAmmoSprite.rect.x = self.displayedAmmo * newAmmoSprite.rect.width
            self.ammoSprites.add(newAmmoSprite)
            self.displayedAmmo += 1
        while self.displayedAmmo > self.player.ammo:
            self.ammoSprites.remove(self.ammoSprites.sprites()[-1])
            self.displayedAmmo -= 1

    def updateHealthIndicator(self) -> None:
        '''Make the displayed health match the player's health, by adding or deleting health sprites'''
        while self.displayedHealth < self.player.health:
            newHealthSprite = IndicatorSprite(self, r"Assets\Heart.png")
            newHealthSprite.rect.x = SCREEN_WIDTH - (self.displayedHealth * newHealthSprite.rect.width) - newHealthSprite.rect.width
            self.healthSprites.add(newHealthSprite)
            self.displayedHealth += 1
        while self.displayedHealth > self.player.health:
            self.healthSprites.remove(self.healthSprites.sprites()[-1])
            self.displayedHealth -= 1

class genericSprite(pygame.sprite.Sprite):
    """
    Generic class for all sprites with basic functionalities that are not type-specific
    """
    def __init__(self, gameInstance:Game) -> None:
        super().__init__()
        self.health:int = 1
        self.GI:Game = gameInstance
        # Empty image and rect for typing, will be overridden by subclasses
        self.image:pygame.Surface = pygame.Surface((0, 0))
        self.rect:pygame.Rect = self.image.get_rect()

    def draw(self) -> None:
        self.GI.screen.blit(self.image, self.rect)

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
        while len(pygame.sprite.spritecollide(self, self.GI.allPhysicalSprites, False)) > 1:
            self.rect.x = random.randint(0, SCREEN_WIDTH-self.rect.width)
            self.rect.y = -self.rect.height - random.randint(0, SCREEN_HEIGHT)
        
class asteroidSprite(genericSprite):
    def __init__(self, gameInstance:Game) -> None:
        super().__init__(gameInstance)
        self.health = self.GI.ASTEROID_DURABILITY
        self.positionUp() # Start at the top of the screen and choose a sprite picture

    def reRollPicture(self) -> None:
        #Change the sprite to a random asteroid
        self.health = self.GI.ASTEROID_DURABILITY  # Reset health as the asteroid respawns
        imageIndex = random.randint(0, len(ASTEROID_SPRITES)-1)
        self.image = pygame.image.load(ASTEROID_SPRITES[imageIndex]).convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//ASTEROID_RESCALE, self.rect.height//ASTEROID_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling

class enemySprite(genericSprite):
    def __init__(self, gameInstance:Game) -> None:
        super().__init__(gameInstance)
        self.health = self.GI.ENEMY_HEALTH
        self.positionUp() # Start at the top of the screen and choose a sprite picture

    def reRollPicture(self) -> None:
        #Change the sprite to a random enemy
        self.health = self.GI.ENEMY_HEALTH  # Reset health as the enemy respawns
        imageIndex = random.randint(0, len(ENEMY_SPRITES)-1)
        self.image = pygame.image.load(ENEMY_SPRITES[imageIndex]).convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//ENEMY_RESCALE, self.rect.height//ENEMY_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling

    def moveDown(self) -> None:
        self.rect.y += MOVEMENT_SPEED
        if self.rect.x < self.GI.player.rect.x-2 and not len(pygame.sprite.spritecollide(self, self.GI.allPhysicalSprites, False)) > 1:
            self.rect.x += self.GI.ENEMY_TRACKING_SPEED
        elif self.rect.x > self.GI.player.rect.x+2 and not len(pygame.sprite.spritecollide(self, self.GI.allPhysicalSprites, False)) > 1:
            self.rect.x -= self.GI.ENEMY_TRACKING_SPEED

class playerSprite(genericSprite):
    def __init__(self, gameInstance:Game) -> None:
        super().__init__(gameInstance)
        self.health = self.GI.PLAYER_HEALTH
        self.image = pygame.image.load(r"Assets\Player.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//PLAYER_RESCALE, self.rect.height//PLAYER_RESCALE))
        self.rect = self.image.get_rect()   # Get new rect after rescaling
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT-self.rect.height) # Start at the bottom center
        self.ammo = self.GI.PLAYER_AMMO

    def reRollPicture(self) -> None:
        # If this was called on the player, it means he died.
        self.health = 0  # Zero health means a dead player.
        self.GI.saveProfileQuit()

    def fireMissile(self) -> bool:
        if self.ammo > 0 and self.GI.missile.rect.y < 0:
            self.GI.missile.setAbovePlayer()
            self.ammo -= 1
            return True
        return False

    def takeDamage(self) -> None:
        if self.health <= 1:
            self.GI.saveProfileQuit()
        else:
            self.health -= 1

    def collectSupplyBox(self) -> None:
        '''Add health or ammo to the player, depending on health probability parameter'''
        randomnumber = random.randint(0, 100)
        if randomnumber < self.GI.HEALTH_PROBABILITY:
            self.health += 1
        else:
            self.ammo += 1

class missileSprite(genericSprite):
    def __init__(self, gameInstance:Game) -> None:
        super().__init__(gameInstance)
        self.image = pygame.image.load(r"Assets\Missile.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.positionUp() # Start above the screen, invisible
    
    def moveDown(self) -> None:
        self.rect.y -= MOVEMENT_SPEED   # Movement reversed for bullets

    def setAbovePlayer(self) -> None:
        ''' Position missle above player '''
        self.rect.center = (self.GI.player.rect.centerx, self.GI.player.rect.centery - self.GI.player.rect.height)

class supplySprite(genericSprite):
    def __init__(self, gameInstance:Game):
        super().__init__(gameInstance)
        self.image = pygame.image.load(r"Assets\SupplyBox.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width//SUPPLYBOX_RESCALE, self.rect.height//SUPPLYBOX_RESCALE))
        self.rect = self.image.get_rect()
        self.positionUp()

class IndicatorSprite(pygame.sprite.Sprite):
    '''Not a physical sprite, only used to display statistics'''
    def __init__(self, gameInstance:Game, assetPath:str) -> None:
        super().__init__()
        self.GI:Game = gameInstance
        self.image:pygame.Surface = pygame.image.load(assetPath).convert_alpha()
        self.rect:pygame.Rect = self.image.get_rect()
        self.rect.y = SCREEN_HEIGHT-self.rect.height
Game()
