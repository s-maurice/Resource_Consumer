import pygame

from RCMachines import *


class RCScreenGUI(object):
    # class for the gui of the game
    def __init__(self, rcg, selected_machine_callback):
        self.rcg = rcg  # passed through so buttons can interact

        self.buttons = []

        colour1 = (20, 50, 60)
        colour2 = (120, 150, 160)

        for index, machine in enumerate(machine_id_lookup.values()):
            self.buttons.append(BuildButton((1000 - 50*(index+1), 700), colour1, machine, selected_machine_callback))

    def draw(self, surface):
        # takes a surface and draws the gui and all of the buttons onto it
        for button in self.buttons:
            button.draw(surface)

    def update(self, mouse_pos, m_inputs):
        # mouse pos is a tuple of the (x, y) pixel position of the mouse
        # m_inputs is the mouse portion of the input handler

        # updates the visuals of the gui, ready for the next draw call
        for button in self.buttons:
            button.update(mouse_pos, m_inputs)


class GUIButton(object):
    # class for an individual button on the gui
    def __init__(self, pos, colour):

        self.rect_size = (50, 50)
        self.colour = (100, 100, 100)
        self.rect = [950, 700, 50, 50]

        self.colour = colour
        self.rect[0], self.rect[1] = pos[0], pos[1]

        self.rect = pygame.Rect(self.rect)
        self.hovered = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.colour, self.rect)

    def button_pressed(self):
        # called when the button is pressed, mainly to be overridden
        print("button pressed", self.rect)

    def update(self, mouse_pos, m_inputs):
        # mouse pos is a tuple of the (x, y) pixel position of the mouse
        # m_inputs is the mouse portion of the input handler

        # checks if the mouse if hovering the the tile, updating param
        self.hovered = False
        if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            self.hovered = True
            if m_inputs[0]["up_pos"] != [None, None] and m_inputs[0]["down_pos"] != [None, None]:
                if self.rect.collidepoint(m_inputs[0]["down_pos"][0]):
                    # do what the button does here
                    self.button_pressed()


class BuildButton(GUIButton):
    # class for selecting a building
    def __init__(self, pos, colour, machine, selected_machine_callback):
        super().__init__(pos, colour)
        self.machine = machine
        self.selected_machine_callback = selected_machine_callback

    def button_pressed(self):
        # overridden method
        print("selected", self.machine)
        self.selected_machine_callback(self.machine)
