import numpy as np

from DrawHandlers import BackgroundDrawHandler


class RCMap(object):
    id = 0

    size = (0, 0)
    background_map = np.array([])
    background_addition_map = np.array([])

    placed_objects = []

    def __init__(self):
        self.draw_handler = BackgroundDrawHandler(self.size, self.background_map, self.background_addition_map)

    def to_json_serialisable(self):
        # returns a serialisable version of itself that can be rebuilt
        # some maps will have placed_objects inside, but the server sends those separately every time

        details = {
            "id": self.id,
            "bg": self.background_map.tolist(),
            "bga": self.background_addition_map.tolist()
        }

        return details


class RandomMap(RCMap):
    def __init__(self):
        super().__init__()

        self.size = (20, 20)
        self.background_map = np.ones(self.size, dtype=int)  # bg tiles
        self.background_addition_map = np.random.randint(0, 2, size=self.size, dtype=int)  # bg extras (ores)

