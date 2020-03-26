import math
import time
import asyncio

import pygame

from FramerateHandler import FramerateHandler
from InputHandler import InputHandler
from RCGame import ResourceConsumerGame, GenericMachine
from RCScreenGUI import RCScreenGUI


class RCScreen(object):
    # class to handle the overall window, interaction and rendering of a ResourceConsumerGame object
    def __init__(self, rcg: ResourceConsumerGame):
        self.rcg = rcg

        self.input_handler = InputHandler()
        self.framerate_handler = FramerateHandler(30)

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

        # set up GUI
        self.selected_machine = None  # used for the gui to callback to
        self.gui = RCScreenGUI(self.rcg, self.set_selected_machine)

        # zoom and camera position limits and speeds
        self.tile_size_min = 10
        self.tile_size_max = 75
        self.offsets_max = (1000, 1000)  # (x, y) pairs or (h, v) pairs
        self.offsets_min = (-1000, -1000)  # (x, y) pairs or (h, v) pairs
        # can be changed to be smooth/have acceleration
        self.offset_move_speed = 10  # n pixels change per frame
        self.tile_size_zoom_speed = 2  # n pixels change per frame

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
        self.rcg.game_map.draw_handler.draw_background(self.bg_surface, self.offsets, (self.tile_size, self.tile_size))

        # draw the machines
        for machine in self.rcg.placed_objects:
            machine.draw_handler.draw(self.machine_surface, self.offsets, (self.tile_size, self.tile_size))

        # draw the gui
        self.gui.draw(self.surface_hud)

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

        # Get and process events, including keypress and mouse position
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False  # handle exit flag
            elif event.type == pygame.KEYDOWN:
                self.input_handler.kb_input_start(event.key)
            elif event.type == pygame.KEYUP:
                self.input_handler.kb_input_stop(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for m_button, pressed in enumerate(pygame.mouse.get_pressed()):
                    if pressed == 1:
                        self.input_handler.m_down(m_button, mouse_pos, self.px_to_game_tile(mouse_pos))
            elif event.type == pygame.MOUSEBUTTONUP:
                for m_button, pressed in enumerate(pygame.mouse.get_pressed()):
                    if pressed == 0:
                        self.input_handler.m_up(m_button, mouse_pos, self.px_to_game_tile(mouse_pos))

        # handle inputHandler inputs, this can be moved into the input_handler
        kb_inputs, m_inputs = self.input_handler.get_inputs()

        # handle keyboard
        camera_offset_adjust = [0, 0]
        camera_zoom_adjust = 0
        if kb_inputs.get("pan_left"):
            camera_offset_adjust[0] -= 1
        if kb_inputs.get("pan_right"):
            camera_offset_adjust[0] += 1
        if kb_inputs.get("pan_up"):
            camera_offset_adjust[1] -= 1
        if kb_inputs.get("pan_down"):
            camera_offset_adjust[1] += 1
        if kb_inputs.get("zoom_in"):
            camera_zoom_adjust += 1
        if kb_inputs.get("zoom_out"):
            camera_zoom_adjust -= 1

        # apply the camera offset and zoom changes
        self.adjust_camera_offset(camera_offset_adjust)
        self.adjust_camera_zoom(camera_zoom_adjust)

        # handle mouse
        # left click place
        if m_inputs[0]["up_pos"] != [None, None]:
            if self.selected_machine is not None:  # check if a building is selected
                if self.is_on_map(m_inputs[0]["up_pos"][1]):
                    # need to check if on gui
                    if m_inputs[0]["down_pos"][1] == m_inputs[0]["up_pos"][1]:  # compare the game pos
                        print("place building at", m_inputs[0]["up_pos"][1], self.selected_machine)

                        machine = self.selected_machine(m_inputs[0]["up_pos"][1], 0)
                        a = self.rcg.build_tile(machine, ignore_check=True)
                        print("building built", a)

        # right click drag selection

        # update the gui with the mouse position and mouse input handler
        self.gui.update(mouse_pos, m_inputs)

    def is_on_map(self, game_pos):
        # game pos is tuple (x, y) of already converted px_to_game_tile() result for a position
        # checks if this position is within the map
        map_size = self.rcg.game_map.size
        if 0 <= game_pos[0] < map_size[0] and 0 <= game_pos[1] < map_size[1]:
            return True
        else:
            return False

    def px_to_game_tile(self, pixel_pos):
        # pixel_pos is a tuple (x, y) of a pixel position
        # converts the pixel_pos to the game_pos tuple (x, y) for the correct game tile

        tile_x = math.floor((pixel_pos[0] - self.offsets[0]) / self.tile_size)
        tile_y = math.floor((pixel_pos[1] - self.offsets[1]) / self.tile_size)

        return tile_x, tile_y

    def set_selected_machine(self, machine):
        # setter for setting the currently selected machine - used by the RCScreenGUI for callback
        assert issubclass(machine, GenericMachine)  # because not inited
        self.selected_machine = machine

    async def main(self):
        # main loop for handling every frame of the screen
        self.run = True
        while self.run:
            self.framerate_handler.frame_start()  # start the framerate_handler's frame

            # use input_handler and method to apply all the needed inputs/actions
            self.handle_events()

            # entire draw routine
            self.draw()

            # dynamically await using the framerate_handler
            await self.framerate_handler.frame_end()
