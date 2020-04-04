import numpy as np


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

    def to_json_serialisable(self):
        # returns a serialisable version of itself that can be rebuilt
        # some maps will have placed_objects inside, but the server sends those separately every time

        details = {
            "id": self.id,
            "map_size": self.size,
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
        from scipy.ndimage import zoom
        size = (20, 20)

        # handle background_map
        background_map = np.empty(shape=size, dtype=int)

        bg_zoom_ratio = 2  # ensure size is int divisible by ratio
        bg_uniform_size = (size[0]//bg_zoom_ratio, size[1]//bg_zoom_ratio)  # size before interpolation / zooming

        background_uniform = np.random.uniform(size=bg_uniform_size)
        background_uniform = zoom(background_uniform, bg_zoom_ratio)
        assert background_uniform.shape == size

        # iterate through the generated, zoomed background_uniform and apply values to background_map
        for index, value in np.ndenumerate(background_uniform):
            if value < 0.3:
                background_map[index] = 1
            elif 0.3 <= value < 0.6:
                background_map[index] = 2
            elif 0.6 <= value:
                background_map[index] = 3
            else:
                background_map[index] = 0

        # handle ores / background_addition_map
        background_addition_map = np.empty(shape=size, dtype=int)

        add_zoom_ratio = 4  # ensure size is int divisible by ratio
        add_uniform_size = (size[0] // add_zoom_ratio, size[1] // add_zoom_ratio)  # size before interpolation / zooming

        addition_uniform = np.random.uniform(size=add_uniform_size)
        addition_uniform = zoom(addition_uniform, add_zoom_ratio)
        assert addition_uniform.shape == size

        # iterate through the generated, zoomed background_uniform and apply values to background_map
        for index, value in np.ndenumerate(addition_uniform):
            if value < 0.1:
                background_addition_map[index] = 1
            elif 0.3 <= value < 0.35:  # possibly only use the top and bottom of uniform map - regenerate new uniform
                background_addition_map[index] = 2
            elif 0.9 <= value:
                background_addition_map[index] = 3
            else:
                background_addition_map[index] = 0

        super().__init__(size, background_map, background_addition_map)


