import numpy as np

from DrawHandlers import BackgroundTileDrawHandler


class RCMap(object):
    id = 0

    size = (0, 0)
    background_map = None
    background_addition_map = None

    placed_objects = []

    def __init__(self):
        self.bg_draw_handlers = []
        self.bg_add_draw_handlers = []

        for x in range(self.size[0]):
            for y in range(self.size[1]):
                # TODO move all image locations to the draw handlers - here and in the machines
                tile_id = self.background_map[x, y]
                image_location = "mineindustry_sprites/background/{}.png".format(tile_id)
                bg_renderer = BackgroundTileDrawHandler(image_location, (x, y))
                self.bg_draw_handlers.append(bg_renderer)

                tile_id_addition = self.background_addition_map[x, y]
                image_location_addition = "mineindustry_sprites/background_additions/{}.png".format(tile_id)
                bg_addition_renderer = BackgroundTileDrawHandler(image_location, (x, y))
                self.bg_add_draw_handlers.append(bg_addition_renderer)

    def to_json_serialisable(self):
        # returns a serialisable version of itself that can be rebuilt
        # some maps will have placed_objects inside, but the server sends those separately every time

        details = {
            "id": self.id,
            "bg": self.background_map.tolist(),
            "bga": self.background_addition_map.tolist()
        }

        return details

    def draw_background(self, surface, offsets, size):
        # iterates through the draw handlers for each tile and renders them
        for draw_handler in self.bg_draw_handlers:
            draw_handler.draw(surface, offsets, size)
        for draw_handler in self.bg_add_draw_handlers:
            draw_handler.draw(surface, offsets, size)


class RandomMap(RCMap):
    def __init__(self):
        super().__init__()

        self.size = (20, 20)
        self.background_map = np.ones(self.size, dtype=int)  # bg tiles
        self.background_addition_map = np.random.randint(0, 2, size=self.size, dtype=int)  # bg extras (ores)

