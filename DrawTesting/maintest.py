import pygame
import numpy as np

pygame.init()

size = (1000, 750)
screen = pygame.display.set_mode(size)
screen.fill((0, 100, 100))
pygame.display.set_caption("resource consumer test")

clock = pygame.time.Clock()

surface_background = pygame.Surface(size)
test_image = pygame.image.load("mineindustry_sprites/1.png")
test_image2 = pygame.image.load("mineindustry_sprites/ice.png")
test_image3 = pygame.image.load("mineindustry_sprites/spore.png")

surface_object = pygame.Surface(size, pygame.SRCALPHA)  # per pixel alpha
test_object = pygame.image.load("mineindustry_sprites/rock.png")
test_object2 = pygame.image.load("mineindustry_sprites/titanium.png")


test_map = [[1, 1, 1, 1],
            [1, 1, 2, 1],
            [1, 1, 2, 3],
            [1, 1, 1, 1]]

test_obj_map = [[0, 0, 0, 0],
                [0, 1, 1, 1],
                [0, 1, 2, 2],
                [2, 0, 1, 0]]

test_map = np.ones((20, 20))
test_map[-1] = np.full(20, 2)
test_map[:, -1] = np.full(20, 2)
print(test_map)


px_square_size = 50
v_off = 0

run = True
while run:
    # Get and process events, including keypress
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:  # DEBUG
            if event.key == pygame.K_0:
                px_square_size = 25
                test_image = pygame.transform.scale(test_image, (int(test_image.get_size()[0] / 2), int(test_image.get_size()[1] / 2)))
                test_image2 = pygame.transform.scale(test_image2, (int(test_image2.get_size()[0] / 2), int(test_image2.get_size()[1] / 2)))
                test_image3 = pygame.transform.scale(test_image3, (int(test_image3.get_size()[0] / 2), int(test_image3.get_size()[1] / 2)))
                
                test_object = pygame.transform.scale(test_object, (int(test_object.get_size()[0] / 2), int(test_object.get_size()[1] / 2)))
                test_object2 = pygame.transform.scale(test_object2, (int(test_object2.get_size()[0] / 2), int(test_object2.get_size()[1] / 2)))
            if event.key == pygame.K_9:
                px_square_size = 50

                test_image = pygame.image.load("mineindustry_sprites/1.png")
                test_image2 = pygame.image.load("mineindustry_sprites/ice.png")
                test_image3 = pygame.image.load("mineindustry_sprites/spore.png")

                test_object = pygame.image.load("mineindustry_sprites/rock.png")
                test_object2 = pygame.image.load("mineindustry_sprites/titanium.png")
            if event.key == pygame.K_w:
                v_off -= 3
            if event.key == pygame.K_s:
                v_off += 3

    # reset surfaces to blank
    surface_background.fill((0, 0, 0))
    surface_object.fill((0, 0, 0, 0))  # alpha value of 0 needed

    # Draw the background on the background surface
    for index_y, row_x in enumerate(test_map):
        for index_x, item in enumerate(row_x):
            if item == 1:
                surface_background.blit(test_image, (index_x*px_square_size, index_y*px_square_size+v_off))
            elif item == 2:
                surface_background.blit(test_image2, (index_x*px_square_size, index_y*px_square_size+v_off))
            elif item == 3:
                surface_background.blit(test_image3, (index_x*px_square_size, index_y*px_square_size+v_off))

    # Draw the placed_objects on the object surface
    for index_y, row_x in enumerate(test_obj_map):
        for index_x, item in enumerate(row_x):
            if item == 1:
                surface_object.blit(test_object, (index_x*px_square_size, index_y*px_square_size+v_off))
            elif item == 2:
                surface_object.blit(test_object2, (index_x*px_square_size, index_y*px_square_size+v_off))

    # # Update screen surface
    screen.blit(surface_background, (0, 0))
    screen.blit(surface_object, (0, 0))
    pygame.display.flip()

    # Frame-rate limit
    clock.tick(60)
