import numpy as np

from RCMachineTypes import GenericMachine, ProcessingMachine
from RCMapTypes import RCMapBase


class ResourceConsumerGame(object):
    def __init__(self, game_map):
        assert isinstance(game_map, RCMapBase)
        self.game_map = game_map  # game_map object

        self.placed_objects = game_map.placed_objects  # list of all the RCMachines, initially inherit from the map

        self.placed_object_map = self.game_map.get_empty_placed_object_map()

        # fill the placed object map with references to all the placed objects
        for placed_object in self.placed_objects:
            for tile_occupied in placed_object.get_tiles_occupied():
                self.placed_object_map[tile_occupied[1]][tile_occupied[0]] = placed_object

        self.inventory = {}  # dict of RCResources and number

        self.tick = 0

    def dismantle_selection(self, selection):
        # dismantles all machines in area given by selection
        # selection is a dict with "start" and "end" keys, with both items being tuples of (x, y) tile positions

        # identify the starting and ending corners
        start_x = min(selection["start"][0], selection["end"][0])
        start_y = min(selection["start"][1], selection["end"][1])
        end_x = max(selection["start"][0], selection["end"][0])
        end_y = max(selection["start"][1], selection["end"][1])

        # iterate through the placed_object_map
        for y_idx, row in enumerate(self.placed_object_map[start_y:end_y+1]):
            for x_idx, value in enumerate(row[start_x:end_x+1]):
                if isinstance(value, GenericMachine):
                    # need to check if list.remove() works
                    if value in self.placed_objects:
                        self.placed_objects.remove(value)
                        for tile_occupied in value.get_tiles_occupied():
                            self.placed_object_map[tile_occupied[1]][tile_occupied[0]] = 0

    def can_build_machine(self, machine):
        # takes a prototype machine object - already initialised with position, and checks requirements
        # returns true or false depending on if the machine can be built
        assert isinstance(machine, GenericMachine)
        # check if inventory has enough materials to build machine and that there are no collisions
        for key, value in machine.build_cost.items():
            if self.inventory.get(key, 0) < value:
                # print("FAIL INV")
                break
        else:
            if not self.is_collision(machine):
                return True
            else:
                pass
        return False

    def build_machine(self, machine, ignore_check=False, ignore_build_cost=False):
        # takes a prototype machine object - already initialised with position, and checks requirements
        # if all requirements are satisfied, append to placed_objects and return true, otherwise false
        assert isinstance(machine, GenericMachine)

        if ignore_check or self.can_build_machine(machine):
            # machine build routine

            # handle build cost
            if not ignore_build_cost:
                for key, item in machine.build_cost.items():
                    self.inventory[key] -= item

            # set the callback for the machine
            machine.output_callback = self.machine_output_callback

            # add machine to placed_object list
            self.placed_objects.append(machine)

            # add machine to placed_object_map
            for tile_occupied in machine.get_tiles_occupied():
                self.placed_object_map[tile_occupied[1]][tile_occupied[0]] = self.placed_objects[-1]

            return True
        else:
            return False

    def machine_output_callback(self, resource, tile_tuple):
        # used by the machines to callback to - takes resource and tuple of a single tile to try
        # returns true if successfully inputted, otherwise false
        machine_input_check = self.placed_object_map[tile_tuple[1]][tile_tuple[0]]
        if machine_input_check != 0 and machine_input_check.input_item(resource):
            return True
        else:
            return False

    def is_collision(self, machine):
        # checks if the given machine collides with any of the placed placed_objects or the map edge,
        # using the placed_object_map
        for tile_occupied in machine.get_tiles_occupied():
            if (not (0 <= tile_occupied[0] < self.game_map.size[0] and
                     0 <= tile_occupied[1] < self.game_map.size[1]) or
                    self.placed_object_map[tile_occupied[1]][tile_occupied[0]] != 0):
                return True
        else:
            return False

    def tick_game(self):
        # called every game tick, ticks all the machines and increments the tick

        # try to output to valid machines
        for machine in self.placed_objects:
            machine.output_item()

        # process machines
        for machine in self.placed_objects:
            machine.machine_process()

        self.tick += 1

    def get_serialisable_inventory(self):
        # converts the inventory into a serialisable dict
        inv = {}
        for key, item in self.inventory.items():
            inv[key.id] = item
        return inv
