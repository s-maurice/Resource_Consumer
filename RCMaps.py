import numpy as np

from RCMapTypes import StoredMap


class IceMap(StoredMap):
    id = 1

    size = (0, 0)
    background_map = np.array([])
    background_addition_map = np.array([])

    placed_objects = []


map_id_lookup = {IceMap.id: IceMap}
