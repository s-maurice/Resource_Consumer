import time
import asyncio

import pygame

from InputHandler import InputHandler
from RCGame import ResourceConsumerGame


class RCScreen(object):
    # class to handle the overall window, interaction and rendering of a ResourceConsumerGame object
    def __init__(self, rcg: ResourceConsumerGame):
        self.rcg = rcg

        self.input_handler = InputHandler()

        pygame.init()

        # set up window
        self.window_size = (1000, 750)
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(self.window_size)
        self.screen.fill((0, 100, 100))  # base colour
        pygame.display.set_caption("resource consumer screen")

        # set up surfaces
        self.bg_surface = pygame.Surface(self.window_size)
        self.machine_surface = pygame.Surface(self.window_size, pygame.SRCALPHA)  # per pixel alpha
        self.surface_hud = pygame.Surface(self.window_size, pygame.SRCALPHA)  # per pixel alpha

        # zoom and camera position limits and speeds
        self.tile_size_min = 10
        self.tile_size_max = 75
        self.offsets_max = (1000, 1000)  # (x, y) pairs or (h, v) pairs
        self.offsets_min = (-1000, -1000)  # (x, y) pairs or (h, v) pairs
        # can be changed to be smooth/have acceleration
        self.offset_move_speed = 10  # n pixels change per frame
        self.tile_size_zoom_speed = 1  # n pixels change per frame

        # set up base zoom and camera position
        self.tile_size = 50
        self.offsets = [0, 0]

        # run flag for main
        self.run = False

    def draw(self):
        # draw a single frame of the game

        # reset the surfaces to blank
        self.bg_surface.fill((0, 0, 0))
        self.machine_surface.fill((0, 0, 0, 0))  # alpha value of 0 needed
        self.surface_hud.fill((0, 0, 0, 0))  # alpha value of 0 needed

        # draw the background
        self.rcg.game_map.draw_handler.draw_background(self.bg_surface, self.offsets, self.tile_size)
        # draw the machines
        for machine in self.rcg.placed_objects:
            machine.draw_handler.draw(self.machine_surface, self.offsets, self.tile_size)

        # Update screen surface
        self.screen.blit(self.bg_surface, (0, 0))
        self.screen.blit(self.machine_surface, (0, 0))
        self.screen.blit(self.surface_hud, (0, 0))
        pygame.display.flip()

    def adjust_camera_offset(self, direction):
        # takes direction tuple, (x, y) or (h, v) of either -1, 0, 1 and moves one time in that direction

        # handle horizontal
        if direction[0] != 0:
            if direction[0] > 0:
                self.offsets[0] = min(self.offsets[0] + self.offset_move_speed, self.offsets_max[0])
            elif direction[0] < 0:
                self.offsets[0] = max(self.offsets[0] - self.offset_move_speed, self.offsets_min[0])
        # handle vertical
        if direction[1] != 0:
            if direction[1] > 0:
                self.offsets[1] = min(self.offsets[1] + self.offset_move_speed, self.offsets_max[1])
            elif direction[1] < 0:
                self.offsets[1] = max(self.offsets[1] - self.offset_move_speed, self.offsets_min[1])

    def adjust_camera_zoom(self, direction):
        # takes direction value, either -1, 0, 1 and zooms one time in that direction
        if direction != 0:  # for later, if this is called every tick with a smooth camera
            if direction > 0:
                self.tile_size = min(self.tile_size + self.tile_size_zoom_speed, self.tile_size_max)
            elif direction < 0:
                self.tile_size = max(self.tile_size - self.tile_size_zoom_speed, self.tile_size_min)

    def handle_events(self):
        # uses the input_handler to record the key states
        # updates the input_handler with input changes
        # handles the inputs given by the input handler

        # Get and process events, including keypress
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False  # handle exit flag
            elif event.type == pygame.KEYDOWN:
                self.input_handler.kb_input_start(event.key)
            elif event.type == pygame.KEYUP:
                self.input_handler.kb_input_stop(event.key)

        # handle inputHandler inputs, this can be moved into the input_handler
        camera_offset_adjust = [0, 0]
        camera_zoom_adjust = 0
        player_inputs = self.input_handler.get_inputs()
        if player_inputs.get("pan_left"):
            camera_offset_adjust[0] -= 1
        if player_inputs.get("pan_right"):
            camera_offset_adjust[0] += 1
        if player_inputs.get("pan_up"):
            camera_offset_adjust[1] -= 1
        if player_inputs.get("pan_down"):
            camera_offset_adjust[1] += 1
        if player_inputs.get("zoom_in"):
            camera_zoom_adjust += 1
        if player_inputs.get("zoom_out"):
            camera_zoom_adjust -= 1

        # apply the camera offset and zoom changes
        self.adjust_camera_offset(camera_offset_adjust)
        self.adjust_camera_zoom(camera_zoom_adjust)

    async def main(self):
        # main loop for handling every frame of the screen
        self.run = True
        while self.run:
            # use input_handler and method to apply all the needed inputs/actions
            self.handle_events()

            # entire draw routine
            self.draw()

            # Frame-rate limit
            # await self.clock.tick(60)
            await asyncio.sleep(1)

            print("FRAME FINISHED ---------")
