import pygame

# Variables and constants
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
BACKGROUND_COLOR = (0, 0, 0) # Black, we are in space
main_loop = True
FPS = 60

# Initialize the game
pygame.init()
pygame.display.set_caption("Game Name")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(BACKGROUND_COLOR)

# Begin main game loop
while main_loop:
    # Check for game exit command
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            main_loop = False # this will be the last iteration of the loop

    # Main loop logic

    # Draw a new frame
    pygame.time.Clock().tick(FPS)
    pygame.display.update()


pygame.quit()
