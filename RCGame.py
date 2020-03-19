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
        # mostly a modified version of is_collision() below

        # to avoid concurrent modification problems, create new list of objects to keep
        new_placed_objects = []

        machine_min_x = selection_start[0]
        machine_max_x = selection_end[0]
        machine_min_y = selection_start[1]
        machine_max_y = selection_end[1]

        for placed_object in self.placed_objects:
            placed_min_x = placed_object.position[0]
            placed_max_x = placed_object.position[0] + placed_object.size[0] - 1
            placed_min_y = placed_object.position[1]
            placed_max_y = placed_object.position[1] + placed_object.size[1] - 1

            if not ((placed_max_x >= machine_min_x or placed_min_x <= machine_max_x) and
                    (placed_max_y >= machine_min_y or placed_min_y <= machine_max_y)):
                new_placed_objects.append(placed_object)  # no collision, so append
        self.placed_objects = new_placed_objects

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

        machine_min_x = machine.position[0]
        machine_max_x = machine.position[0] + machine.size[0] - 1
        machine_min_y = machine.position[1]
        machine_max_y = machine.position[1] + machine.size[1] - 1

        for placed_object in self.placed_objects:
            placed_min_x = placed_object.position[0]
            placed_max_x = placed_object.position[0] + placed_object.size[0] - 1
            placed_min_y = placed_object.position[1]
            placed_max_y = placed_object.position[1] + placed_object.size[1] - 1

            if ((placed_max_x >= machine_min_x or placed_min_x <= machine_max_x) and
                    (placed_max_y >= machine_min_y or placed_min_y <= machine_max_y)):
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


