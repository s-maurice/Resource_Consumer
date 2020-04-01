import pygame

from RCMachines import *


class RCScreenGUI(object):
    # class for the gui of the game
    def __init__(self, rcg, selected_machine_callback):
        # pass through
        self.rcg = rcg
        self.selected_machine_callback = selected_machine_callback

        self.buttons = []

        for index, machine in enumerate(machine_id_lookup.values()):
            self.buttons.append(BuildButton((1000 - 50*(index+1), 700), machine, self.selected_callback_passthrough))

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

    def selected_callback_passthrough(self, selected_machine):
        for button in self.buttons:
            button.selected = False
            button.hovered = False
            button.redraw = True

        self.selected_machine_callback(selected_machine)


class GUIButton(object):
    # class for an individual button on the gui
    def __init__(self, pos):

        self.pos = pos

        self.rect_size = (50, 50)
        self.colour = (100, 100, 100)
        self.rect = [950, 700, 50, 50]

        self.rect[0], self.rect[1] = pos[0], pos[1]

        self.rect = pygame.Rect(self.rect)

        self.cur_draw_hover_state = True
        self.hovered = False
        self.hover_drawn = False

        self.selected = False

        self.redraw = False

    def draw(self, surface):
        # only draw on hover state change
        if self.hovered != self.cur_draw_hover_state:
            self.cur_draw_hover_state = self.hovered
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
    machine_texture_location = "mineindustry_sprites/machines/{}.png"

    def __init__(self, pos, machine, selected_machine_callback):
        super().__init__(pos)
        self.machine = machine

        # load the texture
        image_location = self.machine_texture_location.format(machine.image_name)
        machine_texture = pygame.image.load(image_location)
        self.machine_texture = pygame.transform.scale(machine_texture, (self.rect_size[0], self.rect_size[1]))

        self.selected_machine_callback = selected_machine_callback

    def draw(self, surface):
        # only draw if hover state changes
        if self.hovered != self.cur_draw_hover_state or self.redraw:
            self.redraw = False
            self.cur_draw_hover_state = self.hovered

            temp_surface = pygame.Surface(self.rect_size, pygame.SRCALPHA)
            temp_surface.fill((255, 255, 255))

            temp_surface.blit(self.machine_texture, (0, 0))

            if self.hovered:
                pygame.draw.rect(temp_surface, (255, 255, 255, 50), (0, 0, self.rect_size[0], self.rect_size[1]))
            if self.selected:
                pygame.draw.rect(temp_surface, (30, 30, 30, 200), (0, 0, self.rect_size[0], self.rect_size[1]), 7)

            surface.blit(temp_surface, (self.pos[0], self.pos[1]))

    def button_pressed(self):
        # overridden method
        print("pressed", self.machine)

        # preserve the state
        selected = self.selected

        # callback - also sets selected for all machines to false and redraws them
        self.selected_machine_callback(self.machine)

        # flip selected status and redraw again
        self.selected = False if selected else True
        self.redraw = True
