import math

import pygame
import numpy as np

from TileSprite import *
from InputHandler import InputHandler

pygame.init()

size = (1000, 750)
screen = pygame.display.set_mode(size)
screen.fill((0, 100, 100))
pygame.display.set_caption("resource consumer test")

clock = pygame.time.Clock()

surface_background = pygame.Surface(size)
surface_object = pygame.Surface(size, pygame.SRCALPHA)  # per pixel alpha
surface_hud = pygame.Surface(size, pygame.SRCALPHA)  # per pixel alpha


# maps
object_map = np.random.randint(0, 3, size=(20, 20), dtype=int)
background_map = np.ones((20, 20), dtype=int)
selection_map = np.zeros((20, 20))

px_square_size = 50
px_square_size_min = 10
px_square_size_max = 75
v_off = 0
h_off = 0

bg_sprites = []
fg_sprites = []
hud_sprites = []

# on startup, create all the sprite placed_objects
for index_y, row_x in enumerate(background_map):
    for index_x, item in enumerate(row_x):
        bg_sprites.append(BackgroundTileSprite(surface_background, (index_x, index_y), item))
for index_y, row_x in enumerate(object_map):
    for index_x, item in enumerate(row_x):
        if item != 0:
            fg_sprites.append(ForegroundTileSprite(surface_background, (index_x, index_y), item))
for index_y, row_x in enumerate(selection_map):
    for index_x, item in enumerate(row_x):
        if item != 0:
            hud_sprites.append(SelectionTileShape(surface_hud, (index_x, index_y)))


def resize_sprites(resize_dir):
    global px_square_size  # temp bodge, move into class and use self.px_square_size
    global px_square_size_max
    global px_square_size_min

    # check that the change stays within the limits, adjust zoom
    if resize_dir <= 0:
        px_check_size = px_square_size - 3
        if px_check_size >= px_square_size_min:
            px_square_size = px_check_size
    else:
        px_check_size = px_square_size + 3
        if px_check_size <= px_square_size_max:
            px_square_size = px_check_size

    # resize sprites
    [i.resize((px_square_size, px_square_size)) for i in bg_sprites]
    [i.resize((px_square_size, px_square_size)) for i in fg_sprites]
    [i.resize((px_square_size, px_square_size)) for i in hud_sprites]


inputHandler = InputHandler()
run = True
while run:
    # Get and process events, including keypress
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            inputHandler.kb_input_start(event.key)
        elif event.type == pygame.KEYUP:
            inputHandler.kb_input_stop(event.key)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:  # left click pressed
                pass
            if mouse_pressed[2]:  # right click pressed
                rc_down_pos = pygame.mouse.get_pos()
                # calculate the tile the mouse is over, floor div
                down_tile_pos_x = math.floor((rc_down_pos[0] - h_off) / px_square_size)
                down_tile_pos_y = math.floor((rc_down_pos[1] - v_off) / px_square_size)
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed = pygame.mouse.get_pressed()
            if not mouse_pressed[0]:  # left click released
                pass
            if not mouse_pressed[2]:  # right click released
                pass

        if event.type == pygame.KEYDOWN:  # DEBUG
            if event.key == pygame.K_g:
                print("I")
                print(selection_map)

    # get mouse pos every frame if mouse is pressed
    mouse_pressed = pygame.mouse.get_pressed()
    if mouse_pressed[2]:  # right click pressed
        rc_cur_pos = pygame.mouse.get_pos()
        # calculate the tile the mouse is over
        cur_tile_pos_x = (rc_cur_pos[0] - h_off) / px_square_size
        cur_tile_pos_y = (rc_cur_pos[1] - v_off) / px_square_size
        # floor round for accurate 0-indexed index for the current hovered tile
        cur_tile_pos_x = math.floor(cur_tile_pos_x)
        cur_tile_pos_y = math.floor(cur_tile_pos_y)

        # getting the difference between the hovered tile and where right click was pressed
        tile_pos_dif_x = cur_tile_pos_x - down_tile_pos_x
        tile_pos_dif_y = cur_tile_pos_y - down_tile_pos_y

        # ceil round away from zero and add offset for bigger absolute value
        tile_pos_dif_x = math.ceil(abs(tile_pos_dif_x)) * (1 if tile_pos_dif_x > 0 else -1)
        tile_pos_dif_y = math.ceil(abs(tile_pos_dif_y)) * (1 if tile_pos_dif_y > 0 else -1)

        # range need direction for negative
        x_diff_dir = 1 if tile_pos_dif_x > 0 else -1
        y_diff_dir = 1 if tile_pos_dif_y > 0 else -1

        selection_map = np.zeros((20, 20))
        hud_sprites = []
        # loop through the tiles, add 1 or -1 to increase the absolute value by 1 for looping - not inclusive
        for y in range(0, tile_pos_dif_y + y_diff_dir, y_diff_dir):
            for x in range(0, tile_pos_dif_x + x_diff_dir, x_diff_dir):
                # check it fits within selection map before adding - checks simplified by ide
                position = (down_tile_pos_x + x, down_tile_pos_y + y)
                if selection_map.shape[0] > position[0] >= 0 and selection_map.shape[1] > position[1] >= 0:
                    selection_map[position[::-1]] = 1  # update the selection_map  # np.array indexed [y, x]
                    hud_sprites.append(SelectionTileShape(surface_hud, position))  # add sprite for drawing
        # instantly resize the boxes
        [i.resize((px_square_size, px_square_size)) for i in hud_sprites]

    # handle inputHandler inputs
    player_inputs = inputHandler.get_inputs()
    if player_inputs.get("pan_left"):
        h_off -= 10
    if player_inputs.get("pan_right"):
        h_off += 10
    if player_inputs.get("pan_up"):
        v_off -= 10
    if player_inputs.get("pan_down"):
        v_off += 10
    if player_inputs.get("zoom_in"):
        resize_sprites(1)
    if player_inputs.get("zoom_out"):
        resize_sprites(-1)

    # reset surfaces to blank
    surface_background.fill((0, 0, 0))
    surface_object.fill((0, 0, 0, 0))  # alpha value of 0 needed
    surface_hud.fill((0, 0, 0, 0))  # alpha value of 0 needed

    # call draw on all the sprites
    for bg_sprite in bg_sprites:
        bg_sprite.draw(h_off, v_off)

    for fg_sprite in fg_sprites:
        fg_sprite.draw(h_off, v_off)

    for hud_sprite in hud_sprites:
        hud_sprite.draw(h_off, v_off)

    # Update screen surface
    screen.blit(surface_background, (0, 0))
    screen.blit(surface_object, (0, 0))
    screen.blit(surface_hud, (0, 0))
    pygame.display.flip()

    # Frame-rate limit
    clock.tick(60)
