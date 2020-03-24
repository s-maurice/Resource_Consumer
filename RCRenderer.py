import pygame

from InputHandler import InputHandler
from RCGame import ResourceConsumerGame
from DrawHandlers import BackgroundTileDrawHandler


class RCScreen(object):
    # class to handle the overall window, interaction and rendering of a ResourceConsumerGame object
    def __init__(self, rcg: ResourceConsumerGame):
        self.rcg = rcg

        self.input_handler = InputHandler()

    def draw(self):
        # draw a single frame of the game
        pass

