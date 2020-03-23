import numpy as np


class RCMap(object):
    id = 0

    background_map = None
    background_addition_map = None

    placed_objects = []

    def __init__(self):
        self.draw_handler = None

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
        self.background_addition_map = np.random.randint(0, 1, size=self.size, dtype=int)  # bg extras (ores)
