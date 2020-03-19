from random import random

import numpy as np

from RCMachineTypes import *


class ResourceConsumerGame(object):
    def __init__(self, size):
        self.size = size

        # maps
        self.background_map = np.ones(size, dtype=int)  # map for the background tiles
        self.background_addition_map = np.random.randint(0, 1, size=size, dtype=int)  # map for background extras (ores)

        self.placed_objects = []  # list of all the RCMachines

        self.inventory = {}  # dict of RCResources and number

        self.tick = 0

    def dismantle_selection(self, selection_start, selection_end):
        # selection_start is a tuple (x, y) of where the top left corner of the selection is
        # selection_end is a tuple (x, y) of where the bottom right corner of the selection is
        # mostly a copy of tiles_occupied() in GenericMachine and is_collision()
        # TODO replace with boundary checking

        selection_tiles = []
        for x in range(selection_start[0], selection_end[0]):
            for y in range(selection_start[1], selection_end[1]):
                selection_tiles.append((x, y))

        for placed_object_index, placed_object in enumerate(self.placed_objects):
            for selection_tile in selection_tiles:
                if selection_tile in placed_object.tiles_occupied():
                    self.placed_objects.pop(placed_object_index)  # remove if there is an intersection

    def build_tile(self, machine):
        # takes a prototype machine object - already initialised with position, and checks requirements
        # if all requirements are satisfied, append to placed_objects and return true, otherwise false
        assert isinstance(machine, GenericMachine)

        # check if inventory has enough materials to build machine and that there are no collisions
        if machine.build_cost_satisfied(self.inventory) and not self.is_collision(machine):
            # update the output list of all the touching machines and add this machine to output list - if applicable
            # when machine is a conveyor, get_tiles_outputted_to() is overwritten to only check the faced block
            outputting_to = machine.get_tiles_outputted_to()
            for update_machine in self.placed_objects:
                if any([update_machine.is_touching(tile) for tile in outputting_to]):  # touching
                    if update_machine.check_accept_resource(machine.resource_out):  # can accept resource
                        machine.output_machines.append(update_machine)  # machine outputs to update_machine
                    if machine.check_accept_resource(update_machine.resource_out): # can accept resource
                        # first, check if update_machine is a conveyor, and handle it's directional output
                        if isinstance(update_machine, ConveyorMachine):
                            if any([machine.is_touching(tile) for tile in update_machine.get_tiles_outputted_to()]):
                                update_machine.output_machines.append(machine)  # conveyor outputs to machine
                        else:
                            update_machine.output_machines.append(machine)  # update_machine outputs to machine
            self.placed_objects.append(machine)  # add machine to placed_object list
            return True
        else:
            return False

    def is_collision(self, machine):
        # checks if the given machine collides with any of the placed placed_objects
        # TODO replace with boundary checking
        machine_tiles = machine.tiles_occupied()

        for placed_object in self.placed_objects:
            for machine_tile in machine_tiles:
                if machine_tile in placed_object.tiles_occupied():
                    return True
        else:
            return False

    def tick_game(self):
        # called every game tick, ticks all the machines and increments the tick

        for machine in self.placed_objects:
            machine.output_item()  # machine automatically select machine to output to if able
        for machine in self.placed_objects:
            machine.machine_process()  # machines do work

        self.tick += 1


