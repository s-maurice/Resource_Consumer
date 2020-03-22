import numpy as np
import json

from RCMachineTypes import *
from RCMachines import *
from RCResourceTypes import *
from RCResources import *


class ResourceConsumerGame(object):
    def __init__(self, size, server_mode):
        self.size = size
        self.server_mode = server_mode

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

    def can_build_machine(self, machine):
        # takes a prototype machine object - already initialised with position, and checks requirements
        # returns true or false depending on if the machine can be built
        assert isinstance(machine, GenericMachine)

        # check if inventory has enough materials to build machine and that there are no collisions
        if machine.build_cost_satisfied(self.inventory) and not self.is_collision(machine):
            return True
        else:
            return False

    def build_tile(self, machine):
        # takes a prototype machine object - already initialised with position, and checks requirements
        # if all requirements are satisfied, append to placed_objects and return true, otherwise false
        assert isinstance(machine, GenericMachine)

        if self.can_build_machine(machine):
            # update the output list of all the touching machines and add this machine to output list - if applicable
            # when machine is a conveyor, get_tiles_outputted_to() is overwritten to only check the faced block
            outputting_to = machine.get_tiles_outputted_to()
            for update_machine in self.placed_objects:
                if any([update_machine.is_touching(tile) for tile in outputting_to]):  # machines are touching

                    # the update_machine accepts the machine's output
                    if update_machine.check_accept_resource(machine.resource_out):
                        machine.output_machines.append(update_machine)

                    # the machine accepts the update_machine's output
                    if machine.check_accept_resource(update_machine.resource_out):
                        # check if update_machine is a conveyor, and handle it's directional output
                        if isinstance(update_machine, ConveyorMachine):
                            # update_machine is a conveyor, check if it's facing the right way
                            if any([machine.is_touching(tile) for tile in update_machine.get_tiles_outputted_to()]):
                                update_machine.output_machines.append(machine)
                        else:
                            update_machine.output_machines.append(machine)  # update machine is not a conveyor

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

    def add_machine_from_json(self, machine_dict):
        # takes the output (already de-serialised) from a machines .to_json() function and builds equivalent machine
        # then appends the machine to the game's machine list - with checking if server

        machine_id = machine_dict.get("id", None)
        assert machine_id is not None

        machine = machine_id_lookup.get(machine_id)  # get correct machine type
        machine = machine((machine_dict.get("pos")))  # call constructor
        # place in other attributes
        machine.time = machine_dict.get("time")
        machine.rotation = machine_dict.get("rot")

        # handle inventory
        for key, item in machine_dict.get("inv"):
            res = resource_id_lookup.get(key)
            machine.inventory[res] = item

        # machine.output_machines = machine_dict.get("outmachines")  # client and server build upon adding

        # check if this received machine satisfies the build requirements and build
        if self.build_tile(machine):
            # build is successful - return the serialisable machine (with server's output_machine for sending to client
            return self.placed_objects[-1]
        else:
            return False  # build failure - client sending un-buildable machines to server or client desync





