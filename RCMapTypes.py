import numpy as np

from DrawHandlers import BackgroundDrawHandler, BackgroundDrawHandler2


class RCMapBase(object):
    id = 0

    size = (0, 0)
    background_map = np.array([])
    background_addition_map = np.array([])

    placed_objects = []

    def __init__(self, size, background_map, background_addition_map):
        # this init is usually only called for custom maps - so custom init params
        self.size = size
        self.background_map = background_map
        self.background_addition_map = background_addition_map

        if self.size[0] > 0 and self.size[1] > 0:
            # only want to create draw handlers if map exists
            # self.draw_handler = BackgroundDrawHandler(self.size, self.background_map, self.background_addition_map)
            self.draw_handler = BackgroundDrawHandler2(self.size, self.background_map, self.background_addition_map)

    def to_json_serialisable(self):
        # returns a serialisable version of itself that can be rebuilt
        # some maps will have placed_objects inside, but the server sends those separately every time

        details = {
            "id": self.id,
            "size": self.size,
            "bg": self.background_map.tolist(),
            "bga": self.background_addition_map.tolist()
        }

        return details

    def get_empty_placed_object_map(self):
        # gets an empty 2d list of lists of all zeros the size of this map - ignores any placed objects on the map
        return [[0 for _ in range(self.size[0])] for _ in range(self.size[1])]


class StoredMap(RCMapBase):
    def __init__(self):
        # this class is always extended with the details - just pass through to constructor
        super().__init__(self.size, self.background_map, self.background_addition_map)


class SentMap(RCMapBase):
    # class for when the map is sent to the client and the client needs to build the map
    def __init__(self, size, background_map, background_addition_map):
        # constructor allows to pass through
        super().__init__(size, background_map, background_addition_map)


class RandomMap(RCMapBase):
    def __init__(self):
        size = (20, 20)
        background_map = np.random.randint(1, 4, size=size, dtype=int)  # bg tiles
        background_addition_map = np.random.randint(0, 4, size=size, dtype=int)  # bg extras (ores)

        super().__init__(size, background_map, background_addition_map)


