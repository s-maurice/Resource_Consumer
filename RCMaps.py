import numpy as np

from RCMapTypes import RCMap


class IceMap(RCMap):
    id = 1

    background_map = np.array([])
    background_addition_map = np.array([])

    placed_objects = []


map_id_lookup = {IceMap.id: IceMap}
