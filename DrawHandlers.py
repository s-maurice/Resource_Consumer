from random import random

import pygame


class BaseDrawHandler(pygame.sprite.Sprite):
    # base class for pygame drawing
    def __init__(self, image_location, board_pos, rotation):
        pygame.sprite.Sprite.__init__(self)

        self.board_pos = board_pos

        # load the image up
        self.full_size_image = pygame.image.load(image_location)
        self.full_size = self.full_size_image.get_size()

        # rotate according to rotation - TODO check if center rotation
        self.full_size_image = pygame.transform.rotate(self.full_size_image, 90*rotation)

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


class MachineDrawHandler(BaseDrawHandler):
    # class for handling the drawing of machines
    # possibly implement some sort of animation
    pass


class ConveyorDrawHandler(MachineDrawHandler):
    # class for handling the drawing of conveyor machines
    # possibly implement some sort of animation
    # will also need to draw the ingots on the conveyor
    pass


class BackgroundTileDrawHandler(BaseDrawHandler):
    # class for handling the drawing of background tiles
    def __init__(self, image_location, board_pos):

        rotation = random.randint(0, 3)  # randomise rotation between (0 and 3)

        super().__init__(image_location, board_pos, rotation)

