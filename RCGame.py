import numpy as np

from RCMachineTypes import *
from RCMachines import *
from RCResourceTypes import *
from RCResources import *
from RCMapTypes import RandomMap, RCMapBase


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
        # # selection_start is a tuple (x, y) of where the top left corner of the selection is
        # # selection_end is a tuple (x, y) of where the bottom right corner of the selection is
        # # mostly a modified version of is_collision() below
        #
        # # to avoid concurrent modification problems, create new list of objects to keep
        # new_placed_objects = []
        #
        # machine_min_x = selection_start[0]
        # machine_max_x = selection_end[0]
        # machine_min_y = selection_start[1]
        # machine_max_y = selection_end[1]
        #
        # for placed_object in self.placed_objects:
        #     placed_min_x = placed_object.position[0]
        #     placed_max_x = placed_object.position[0] + placed_object.size[0] - 1
        #     placed_min_y = placed_object.position[1]
        #     placed_max_y = placed_object.position[1] + placed_object.size[1] - 1
        #
        #     if not ((placed_max_x >= machine_min_x or placed_min_x <= machine_max_x) and
        #             (placed_max_y >= machine_min_y or placed_min_y <= machine_max_y)):
        #         new_placed_objects.append(placed_object)  # no collision, so append
        # self.placed_objects = new_placed_objects

        # identify the starting and ending corners
        start_x = min(selection["down"][1][0], selection["cur"][1][0])
        start_y = min(selection["down"][1][1], selection["cur"][1][1])
        end_x = max(selection["down"][1][0], selection["cur"][1][0])
        end_y = max(selection["down"][1][1], selection["cur"][1][1])

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

        for machine in self.placed_objects:
            if isinstance(machine, ProcessingMachine):
                machine.output_item()  # machine automatically select machine to output to if able
        for machine in self.placed_objects:
            if isinstance(machine, ProcessingMachine):
                machine.machine_process()  # machines do work

        self.tick += 1

    def get_serialisable_inventory(self):
        # converts the inventory into a serialisable dict
        inv = {}
        for key, item in self.inventory.items():
            inv[key.id] = item
        return inv
