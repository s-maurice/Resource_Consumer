import pygame

from InputHandler import InputHandler
from RCGame import ResourceConsumerGame
from DrawHandlers import BackgroundTileDrawHandler


class RCScreen(object):
    # class to handle the overall window, interaction and rendering of a ResourceConsumerGame object
    def __init__(self, rcg: ResourceConsumerGame):
        self.rcg = rcg

        self.input_handler = InputHandler()

        # set up window
        self.window_size = (1000, 750)

        self.screen = pygame.display.set_mode(self.window_size)
        self.screen.fill((0, 100, 100))  # base colour
        pygame.display.set_caption("resource consumer screen")

        # set up surfaces
        self.bg_surface = pygame.Surface(self.window_size)
        self.machine_surface = pygame.Surface(self.window_size, pygame.SRCALPHA)  # per pixel alpha
        self.surface_hud = pygame.Surface(self.window_size, pygame.SRCALPHA)  # per pixel alpha

        # zoom and camera position limits
        self.tile_size_min = 10
        self.tile_size_max = 75
        self.offsets_max = (1000, 1000)  # (x, y) pairs or (h, v) pairs
        self.offsets_min = (-1000, -1000)  # (x, y) pairs or (h, v) pairs

        # set up base zoom and camera position
        self.tile_size = 50
        self.offsets = (0, 0)

    def draw(self):
        # draw a single frame of the game
        self.rcg.game_map.draw_handler.draw_background(self.bg_surface, self.offsets, self.tile_size)

