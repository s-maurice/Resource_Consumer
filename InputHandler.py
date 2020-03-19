import pygame


class InputHandler(object):
    def __init__(self):
        self.action = {"pan_left": False,
                       "pan_right": False,
                       "pan_up": False,
                       "pan_down": False,
                       "zoom_in": False,
                       "zoom_out": False}

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

    def get_inputs(self):
        return self.action
