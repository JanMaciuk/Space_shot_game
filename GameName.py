import pygame

SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
main_loop = True

pygame.init()
pygame.display.set_caption("Game Name")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

while main_loop:
    # Check for game exit command
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            main_loop = False # this will be the last iteration of the loop

    # Main loop logic here
    pygame.display.update()



pygame.quit()
