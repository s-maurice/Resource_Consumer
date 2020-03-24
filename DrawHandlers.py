from random import random

import pygame


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
                    bg_add_renderer = BackgroundTileDrawHandler(tile_id_add, (x, y))
                    self.bg_add_draw_handlers.append(bg_add_renderer)

    def draw_background(self, surface, offsets, size):
        # iterates through the draw handlers for each tile and renders them with the given surface, offsets, and size
        # the additions need to be drawn on top
        for draw_handler in self.bg_draw_handlers:
            draw_handler.draw(surface, offsets, size)
        for draw_handler in self.bg_add_draw_handlers:
            draw_handler.draw(surface, offsets, size)


class BackgroundTileDrawHandler(BaseDrawHandler):
    # class for handling the drawing of background tiles
    base_image_location = "mineindustry_sprites/background/{}.png"

    def __init__(self, image_id, board_pos):

        rotation = random.randint(0, 3)  # randomise rotation between (0 and 3)

        super().__init__(image_id, board_pos, rotation)

