import random

import pygame
import numpy as np


class BaseDrawHandler(pygame.sprite.Sprite):
    # base class for pygame drawing
    base_image_location = "{}"

    def __init__(self, image_id, board_pos, rotation):
        pygame.sprite.Sprite.__init__(self)

        self.board_pos = board_pos

        # load the image up
        image_location = self.base_image_location.format(image_id)  # format the base location to get the full path
        self.full_size_image = pygame.image.load(image_location)
        self.full_size = self.full_size_image.get_size()

        # rotate according to rotation - TODO check if center rotation
        self.rotation = 0  # base rotation
        self.rotate(rotation)  # this will update self.rotation to the correct value

        self.current_size_image = self.full_size_image
        self.current_size = self.full_size

    def draw(self, surface, offsets, size):
        # surface given as a pygame surface for the sprite to be drawn on
        # offsets given as a tuple for the (horizontal, vertical) pixel offset values
        # size given as a tuple for the (x, y) size for the sprite to be drawn with

        # update the size if there has been a change
        if size != self.current_size:
            self.current_size_image = pygame.transform.scale(self.full_size_image, size)
            self.current_size = size

        draw_pos_x = self.board_pos[0] * self.current_size[0] + offsets[0]
        draw_pos_y = self.board_pos[1] * self.current_size[1] + offsets[1]

        # can add out of bound checking to avoid drawing off-screen sprites
        surface.blit(self.current_size_image, (draw_pos_x, draw_pos_y))

    def rotate(self, rotation):
        # sets the rotation to the given rotation range(0, 3)
        if self.rotation != rotation:
            # calculate the rotation difference
            rot_difference = rotation - self.rotation

            self.full_size_image = pygame.transform.rotate(self.full_size_image, 90*rot_difference)
            self.rotation = rotation


class MachineDrawHandler(BaseDrawHandler):
    # class for handling the drawing of machines
    # possibly implement some sort of animation
    base_image_location = "mineindustry_sprites/machines/{}.png"


class ConveyorDrawHandler(MachineDrawHandler):
    # class for handling the drawing of conveyor machines
    # possibly implement some sort of animation
    # will also need to draw the ingots on the conveyor
    base_image_location = "mineindustry_sprites/conveyors/{}.png"


class BackgroundDrawHandler(object):
    # class for handling the drawing of the whole background and background additions
    def __init__(self, size, background_map, background_addition_map):
        self.size = size

        self.bg_draw_handlers = []
        self.bg_add_draw_handlers = []

        # iterate through the tiles and create the background
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                tile_id = background_map[x, y]
                if tile_id != 0:
                    bg_renderer = BackgroundTileDrawHandler(tile_id, (x, y))
                    self.bg_draw_handlers.append(bg_renderer)

                tile_id_add = background_addition_map[x, y]
                if tile_id_add != 0:
                    bg_add_renderer = BackgroundTileAdditionDrawHandler(tile_id_add, (x, y))
                    self.bg_add_draw_handlers.append(bg_add_renderer)

    def draw_background(self, surface, offsets, size):
        # iterates through the draw handlers for each tile and renders them with the given surface, offsets, and size
        # the additions need to be drawn on top
        for draw_handler in self.bg_draw_handlers:
            draw_handler.draw(surface, offsets, size)
        for draw_handler in self.bg_add_draw_handlers:
            draw_handler.draw(surface, offsets, size)


class MachineDrawHandler2(object):
    # handles the drawing of the machines - all machines handled by one object

    machine_texture_location = "mineindustry_sprites/machines/{}.png"

    def __init__(self, machine_list):
        self.machine_list = machine_list

        self.machine_texture_dict = {}
        self.machine_texture_cur_size_dict = {}

        self.current_size = (50, 50)

        # on init, iterate over machines and generate a texture dict
        for machine in machine_list:
            if self.machine_texture_dict.get(machine.image_name, None) is None:
                self.load_machine_texture(machine.image_name)

    def load_machine_texture(self, texture_name):
        # takes texture id of a machine texture, loads it, and adds it to the texture dict
        if texture_name != 0:
            image_location = self.machine_texture_location.format(texture_name)  # format base location for full path
            image = pygame.image.load(image_location)
            self.machine_texture_dict[texture_name] = image

            # also load resized version
            cur_image_full_size = image.get_size()
            cur_size_x = round((cur_image_full_size[0] / 50) * (self.current_size[0] / 50) * 50)
            cur_size_y = round((cur_image_full_size[1] / 50) * (self.current_size[1] / 50) * 50)

            self.machine_texture_cur_size_dict[texture_name] = pygame.transform.scale(image, (cur_size_x, cur_size_y))

    def draw_machines(self, surface, offsets, size):
        # draws all the machines onto the surface

        # if size changed, handle resizing
        if size != self.current_size:
            self.current_size = size
            for key, item in self.machine_texture_dict.items():
                # get the size ratio - 2*2 tiles are 100*100px instead of 50*50px, so appropriate scaling
                cur_image_full_size = item.get_size()
                cur_new_size_x = round((cur_image_full_size[0] / 50) * (size[0] / 50) * 50)
                cur_new_size_y = round((cur_image_full_size[1] / 50) * (size[1] / 50) * 50)
                # scale the texture
                scaled_texture = pygame.transform.scale(item, (cur_new_size_x, cur_new_size_y))
                self.machine_texture_cur_size_dict[key] = scaled_texture

        # iterate through machines and draw using the scaled dict
        for machine in self.machine_list:
            # load the texture if not currently loaded
            if self.machine_texture_dict.get(machine.image_name, None) is None:
                self.load_machine_texture(machine.image_name)

            # get the draw position
            draw_pos_x = machine.position[0] * self.current_size[0] + offsets[0]
            draw_pos_y = machine.position[1] * self.current_size[1] + offsets[1]

            # get the texture from the dict
            machine_texture = self.machine_texture_cur_size_dict[machine.image_name]

            # handle machine rotation - for machines this is done every frame
            if machine.rotation != 0:
                machine_texture = pygame.transform.rotate(machine_texture, machine.rotation * 90)

            # draw to surface
            surface.blit(machine_texture, (draw_pos_x, draw_pos_y))


class BackgroundDrawHandler2(object):
    # class for handling the drawing of the whole background and background additions
    bg_texture_location = "mineindustry_sprites/background/{}.png"
    bga_texture_location = "mineindustry_sprites/background_additions/{}.png"

    def __init__(self, size, background_map, background_addition_map):
        self.size = size

        self.background_map = background_map
        self.background_addition_map = background_addition_map

        # generate the random rotation maps
        self.background_rotation_map = np.random.randint(0, 4, size=size)
        self.background_addition_rotation_map = np.random.randint(0, 4, size=size)

        self.bg_texture_dict = {}
        self.bga_texture_dict = {}

        self.bg_texture_cur_size_dict = {}
        self.bga_texture_cur_size_dict = {}
        self.current_size = (50, 50)

        # on init, iterate over both maps to build texture dicts
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                bg_item = self.background_map[x, y]
                bga_item = self.background_addition_map[x, y]

                if self.bg_texture_dict.get(bg_item, None) is None:
                    self.load_new_bg_texture(bg_item)
                if self.bga_texture_dict.get(bga_item, None) is None:
                    self.load_new_bga_texture(bga_item)

        # copy the full-size texture dicts to the current size ones
        # the cur_size_dicts will store a list for every rotation - for speed
        for key, item in self.bg_texture_dict.items():
            self.bg_texture_cur_size_dict[key] = [pygame.transform.rotate(item, i*90) for i in range(4)]
        for key, item in self.bga_texture_dict.items():
            self.bga_texture_cur_size_dict[key] = [pygame.transform.rotate(item, i*90) for i in range(4)]

    def load_new_bg_texture(self, texture_id):
        # takes texture id of a background texture, loads it, and adds it to the texture dict
        if texture_id != 0:
            image_location = self.bg_texture_location.format(texture_id)  # format base location for full path
            image = pygame.image.load(image_location)
            self.bg_texture_dict[texture_id] = image

    def load_new_bga_texture(self, texture_id):
        # takes texture id of a background texture, loads it, and adds it to the texture dict
        if texture_id != 0:
            image_location = self.bga_texture_location.format(texture_id)  # format base location for full path
            image = pygame.image.load(image_location)
            self.bga_texture_dict[texture_id] = image

    def draw_background(self, surface, offsets, size):
        # update the size if there has been a change
        if size != self.current_size:
            self.current_size = size
            for key, item in self.bg_texture_dict.items():
                # get the size ratio - 2*2 tiles are 100*100px instead of 50*50px, so appropriate scaling
                cur_image_full_size = item.get_size()
                cur_new_size_x = round((cur_image_full_size[0] / 50) * (size[0] / 50) * 50)
                cur_new_size_y = round((cur_image_full_size[1] / 50) * (size[1] / 50) * 50)
                # scale the texture
                scaled_texture = pygame.transform.scale(item, (cur_new_size_x, cur_new_size_y))
                # rotate the texture for the stored rotations
                self.bg_texture_cur_size_dict[key] = [pygame.transform.rotate(scaled_texture, i*90) for i in range(4)]

            for key, item in self.bga_texture_dict.items():
                # get the size ratio - 2*2 tiles are 100*100px instead of 50*50px, so appropriate scaling
                cur_image_full_size = item.get_size()
                cur_new_size_x = round((cur_image_full_size[0] / 50) * (size[0] / 50) * 50)
                cur_new_size_y = round((cur_image_full_size[1] / 50) * (size[1] / 50) * 50)
                # scale the texture
                scaled_texture = pygame.transform.scale(item, (cur_new_size_x, cur_new_size_y))
                # rotate the texture for the stored rotations
                self.bga_texture_cur_size_dict[key] = [pygame.transform.rotate(scaled_texture, i*90) for i in range(4)]

        # iterate through the map and draw using the dict of loaded textures
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                # can add offscreen checking to avoid drawing offscreen textures
                # can refer to rotation map to change up textures
                draw_pos_x = x * self.current_size[0] + offsets[0]
                draw_pos_y = y * self.current_size[1] + offsets[1]

                # get tile texture id
                bg_item = self.background_map[x, y]
                bga_item = self.background_addition_map[x, y]

                # handle the background
                if bg_item != 0:
                    # get the texture from dict
                    bg_rotation = self.background_rotation_map[x, y]
                    bg_texture = self.bg_texture_cur_size_dict[bg_item][bg_rotation]  # get pre-rotated texture
                    # draw to surface
                    surface.blit(bg_texture, (draw_pos_x, draw_pos_y))

                # handle the background additions
                if bga_item != 0:
                    # get the texture from dict
                    bga_rotation = self.background_addition_rotation_map[x, y]
                    bga_texture = self.bga_texture_cur_size_dict[bga_item][bga_rotation]  # get pre-rotated texture
                    # draw to surface
                    surface.blit(bga_texture, (draw_pos_x, draw_pos_y))


class SelectionDrawHandler(object):
    # class for handling the drawing of selected tiles on the map
    def __init__(self):
        self.tile_selection_colour = (255, 0, 0)
        self.mouse_selection_colour = (100, 0, 0)

        # selection widths
        self.tile_sel_width = 3
        self.tile_sel_width_ratio = 13
        self.tile_sel_min_width = 1

        self.mouse_sel_width = 2
        self.mouse_sel_width_ratio = 13
        self.mouse_sel_min_width = 1

        self.current_size = (50, 50)

    def draw(self, surface, offsets, size, selection):
        # draws the selections onto the given surface, mouse_input_down and mouse_input_cur are lists of tuples, for
        # pixel and tile position of the selection start and selection end/current - [(px_x, px_y), (tile_x, tile_y)]

        mouse_input_down = selection.get("down")
        mouse_input_cur = selection.get("cur")

        # only draw if there is a selection
        if mouse_input_down != [None, None] and mouse_input_cur != [None, None]:
            if size != self.current_size:
                self.current_size = size
                self.tile_sel_width = max(size[0] // self.tile_sel_width_ratio, self.tile_sel_min_width)
                self.mouse_sel_width = max(size[0] // self.mouse_sel_width_ratio, self.mouse_sel_min_width)

            # handle the tile positions, find the boundary tiles
            start_x = min(mouse_input_down[1][0], mouse_input_cur[1][0])
            start_y = min(mouse_input_down[1][1], mouse_input_cur[1][1])
            end_x = max(mouse_input_down[1][0], mouse_input_cur[1][0])
            end_y = max(mouse_input_down[1][1], mouse_input_cur[1][1])

            # draw all the tile boxes
            for x in range(start_x, end_x+1):
                for y in range(start_y, end_y+1):
                    draw_pos_x = x * size[0] + offsets[0]
                    draw_pos_y = y * size[1] + offsets[1]

                    pygame.draw.rect(surface,
                                     self.tile_selection_colour,
                                     (draw_pos_x, draw_pos_y, size[0], size[1]),
                                     self.tile_sel_width)

            # handle the overall pixel selection box, find the box size and origin - same as above
            start_x = min(mouse_input_down[0][0], mouse_input_cur[0][0])
            start_y = min(mouse_input_down[0][1], mouse_input_cur[0][1])
            end_x = max(mouse_input_down[0][0], mouse_input_cur[0][0])
            end_y = max(mouse_input_down[0][1], mouse_input_cur[0][1])

            # could just be done with min() and abs() value
            pixel_selection_size_x = end_x - start_x
            pixel_selection_size_y = end_y - start_y

            pygame.draw.rect(surface,
                             self.mouse_selection_colour,
                             (start_x, start_y, pixel_selection_size_x, pixel_selection_size_y),
                             self.mouse_sel_width)


class BackgroundTileDrawHandler(BaseDrawHandler):
    # class for handling the drawing of background tiles
    base_image_location = "mineindustry_sprites/background/{}.png"

    def __init__(self, image_id, board_pos):

        rotation = random.randint(0, 3)  # randomise rotation between (0 and 3)
        super().__init__(image_id, board_pos, rotation)


class BackgroundTileAdditionDrawHandler(BaseDrawHandler):
    # class for handling the drawing of background tiles
    base_image_location = "mineindustry_sprites/background_additions/{}.png"

    def __init__(self, image_id, board_pos):

        rotation = random.randint(0, 3)  # randomise rotation between (0 and 3)
        super().__init__(image_id, board_pos, rotation)
