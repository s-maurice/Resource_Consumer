import pygame


class InputHandler(object):
    def __init__(self):
        self.action = {"pan_left": False,
                       "pan_right": False,
                       "pan_up": False,
                       "pan_down": False,
                       "zoom_in": False,
                       "zoom_out": False,
                       "rotate": False}

        # list[0] is the pixel pos, list[1] is the game pos
        self.mouse = [{"down_pos": [None, None], "up_pos": [None, None]} for _ in range(3)]

    def kb_input_start(self, key):
        if key == pygame.K_w:
            self.action["pan_up"] = True
        elif key == pygame.K_s:
            self.action["pan_down"] = True
        elif key == pygame.K_a:
            self.action["pan_left"] = True
        elif key == pygame.K_d:
            self.action["pan_right"] = True
        elif key == pygame.K_MINUS:
            self.action["zoom_out"] = True
        elif key == pygame.K_EQUALS:
            self.action["zoom_in"] = True
        elif key == pygame.K_r:
            self.action["rotate"] = True

    def kb_input_stop(self, key):
        if key == pygame.K_w:
            self.action["pan_up"] = False
        elif key == pygame.K_s:
            self.action["pan_down"] = False
        elif key == pygame.K_a:
            self.action["pan_left"] = False
        elif key == pygame.K_d:
            self.action["pan_right"] = False
        elif key == pygame.K_MINUS:
            self.action["zoom_out"] = False
        elif key == pygame.K_EQUALS:
            self.action["zoom_in"] = False
        elif key == pygame.K_r:
            self.action["rotate"] = False

    def m_down(self, m_button, d_pos_px, d_pos_game):
        self.mouse[m_button]["up_pos"] = [None, None]  # reset the up pos

        self.mouse[m_button]["down_pos"][0] = d_pos_px
        self.mouse[m_button]["down_pos"][1] = d_pos_game

    def m_up(self, m_button, u_pos_px, u_pos_game):
        # checks if mouse was down, if mouse was not, ignore
        if self.mouse[m_button]["down_pos"] != [None, None]:
            self.mouse[m_button]["up_pos"][0] = u_pos_px
            self.mouse[m_button]["up_pos"][1] = u_pos_game

    def kb_set_input(self, key, value):
        # allows for values in the kb inputs to be set externally
        self.action[key] = value

    def m_set_input(self, key, value):
        # allows for values in the mouse inputs to be set externally
        self.mouse[key] = value

    def get_inputs(self):
        # returns the inputs

        # for the mouse, if on return both the down_pos and up_pos values are not None, reset back to None
        # make a copy for returning with the values before removal
        mouse = self.mouse.copy()
        # remove the completed mouse movement values
        for m_index, m_dict in enumerate(self.mouse):
            if m_dict["down_pos"] != [None, None] and m_dict["up_pos"] != [None, None]:
                self.mouse[m_index] = {"down_pos": [None, None], "up_pos": [None, None]}

        return self.action, mouse
