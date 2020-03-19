import numpy as np
import pygame

sprite_id_path_bg = {1: "grass", 2: "ice", 3: "spore"}
sprite_id_path_fg = {1: "titanium", 2: "rock"}


class TileSprite(pygame.sprite.Sprite):
    load_folder = "background"
    sprite_id_path = sprite_id_path_bg

    def __init__(self, surface, board_pos, sprite_id):
        pygame.sprite.Sprite.__init__(self)

        self.full_size_image, self.full_size = self.load_image(sprite_id)

        self.surface = surface

        self.board_pos = board_pos

        self.current_size_image = self.full_size_image
        self.current_size = self.full_size

    def draw(self, h_offset, v_offset):
        # draws the sprite on the given surface, with pixel offset values in the horizontal and vertical position
        draw_pos_x = self.board_pos[0] * self.current_size[0] + h_offset
        draw_pos_y = self.board_pos[1] * self.current_size[1] + v_offset

        # can add out of bound checking to avoid drawing off-screen sprites

        self.surface.blit(self.current_size_image, (draw_pos_x, draw_pos_y))

    def resize(self, new_size):
        # resize the sprite to the correct new pixel size
        # # calculate the multiplier needed to get from full size to new_size
        # ratio_x = new_size[0] / self.full_size[0]
        # ratio_y = new_size[1] / self.full_size[1]

        # self.current_size_image = pygame.transform.scale(self.full_size_image, (ratio_x, ratio_y))

        self.current_size_image = pygame.transform.scale(self.full_size_image, new_size)
        self.current_size = new_size

    def load_image(self, sprite_id):
        load_path = "mineindustry_sprites/{}/{}.png".format(self.load_folder, self.sprite_id_path.get(sprite_id))
        full_size_image = pygame.image.load(load_path)
        full_size = full_size_image.get_size()

        return full_size_image, full_size


class BackgroundTileSprite(TileSprite):
    load_folder = "background"
    sprite_id_path = sprite_id_path_bg

    def __init__(self, surface, board_pos, sprite_id):
        super().__init__(surface, board_pos, sprite_id)

        # randomly flip/rotate background tiles
        rot_truth = np.random.choice(a=[False, True], size=(2,))
        self.full_size_image = pygame.transform.flip(self.full_size_image, rot_truth[0], rot_truth[1])
        self.current_size_image = pygame.transform.flip(self.current_size_image, rot_truth[0], rot_truth[1])


class ForegroundTileSprite(TileSprite):
    load_folder = "foreground"
    sprite_id_path = sprite_id_path_fg

    def __init__(self, surface, board_pos, sprite_id):
        super().__init__(surface, board_pos, sprite_id)


class SelectionTileShape(object):
    def __init__(self, surface, board_pos):
        self.current_size = (50, 50)
        self.board_pos = board_pos
        self.surface = surface

        self.colour = (100, 100, 100)
        self.width = 3

        self.min_width = 1
        self.width_ratio = 13

    def draw(self, h_offset, v_offset):
        # draws the rect on the given surface, with pixel offset values in the horizontal and vertical position

        draw_pos_x = self.board_pos[0] * self.current_size[0] + h_offset
        draw_pos_y = self.board_pos[1] * self.current_size[1] + v_offset
        # can add out of bound checking to avoid drawing off-screen sprites

        # new rect is created every turn
        pygame.draw.rect(self.surface, self.colour, (draw_pos_x, draw_pos_y, self.current_size[0], self.current_size[1]), self.width)

    def resize(self, new_size):
        # set new size
        self.current_size = new_size
        # also adjust width of line
        self.width = max(new_size[0] // self.width_ratio, self.min_width)