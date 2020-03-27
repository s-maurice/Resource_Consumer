from DrawHandlers import MachineDrawHandler, ConveyorDrawHandler
from RCResourceTypes import IngotResource
from RCResources import EmptyIngotResource


class GenericMachine(object):
    # generic class for all machines
    id = 0
    image_name = "none"

    size = (1, 1)
    speed = 0
    build_cost = {}  # dict with resourceconsumeritem and number needed

    # these not always used
    resource_in = {}  # dict with resourceconsumeritem and number needed
    resource_out = None  # resourceconsumeritem
    max_capacity = {}  # dict with resourceconsumeritem and max capacity, include resource_out

    def __init__(self, position, rotation):
        self.inventory = {}
        self.timer = 0

        assert 0 <= rotation <= 3
        self.rotation = rotation
        self.position = position

        self.output_machines = []  # list of the machines that this machine outputs to
        self.output_machine_tiles = self.get_tiles_outputted_to()  # list of the tiles that this machine outputs to

        self.output_callback = None  # callback func to RCGame, used when outputting

        self.draw_handler = MachineDrawHandler(self.image_name, position, rotation)

    def get_tiles_occupied(self):
        # returns a list of the tiles (x, y) occupied by this machine
        tiles = []
        for x in range(self.position[0], self.position[0] + self.size[0]):
            for y in range(self.position[1], self.position[1] + self.size[1]):
                tiles.append((x, y))
        return tuple(tiles)

    def get_bounds(self):
        # returns a tuple of tuples with the corners of the machine ((x_left, y_top), (x_right, y_bottom))
        return self.position, (self.position[0] + self.size[0] - 1, self.position[1] + self.size[1] - 1)

    def get_tiles_outputted_to(self):
        # returns a list of tiles touching the machine, will return out of bounds of board - need to check outside
        possible_tiles = []
        for x in range(self.position[0], self.position[0] + self.size[0] - 1):
            possible_tiles.append((x, self.position[1] - 1))  # all above
            possible_tiles.append((x, self.position[1] + self.size[1] - 1))  # all below

        for y in range(self.position[1], self.position[1] + self.size[1] - 1):
            possible_tiles.append((y, self.position[0] - 1))  # all left
            possible_tiles.append((y, self.position[0] + self.size[0] - 1))  # all right

        return possible_tiles

    def get_touching_tiles(self):
        # returns a list of tiles touching the machine
        # same as in get_tiles_outputted_to, but not overridden in conveyors
        possible_tiles = []
        for x in range(self.position[0], self.position[0] + self.size[0] - 1):
            possible_tiles.append((x, self.position[1] - 1))  # all above
            possible_tiles.append((x, self.position[1] + self.size[1] - 1))  # all below

        for y in range(self.position[1], self.position[1] + self.size[1] - 1):
            possible_tiles.append((y, self.position[0] - 1))  # all left
            possible_tiles.append((y, self.position[0] + self.size[0] - 1))  # all right

        return possible_tiles

    def shift_output_machines(self):
        # rolls the output machine list - so a new machine is outputted to
        self.output_machines = self.output_machines[1:] + self.output_machines[:1]
        self.output_machine_tiles = self.output_machine_tiles[1:] + self.output_machine_tiles[:1]

    def check_accept_resource(self, resource):
        # checks if the machine could accept a certain resource
        # doesn't actually add it and ignores inventory size check
        if self.resource_in.get(resource, 0) > 0:
            return True
        else:
            return False

    def is_touching(self, position):
        # takes (x, y) tuple and sees if machine is overlapping the point
        if (self.position[0] <= position[0] >= self.position[0] + self.size[0] - 1 and
                self.position[1] <= position[1] >= self.position[1] + self.size[1] - 1):
            return True
        else:
            return False

    def get_serialisable_inventory(self):
        # converts the inventory into a serialisable dict
        inv = {}
        for key, item in self.inventory.items():
            inv[key.id] = item
        return inv

    def to_json_serialisable(self):
        # returns a serialisable version of itself that can be rebuilt

        # create a dict with the needed attributes for json encoding
        details = {
            "id": self.id,
            "pos": self.position,
            "time": self.timer,
            "rot": self.rotation,
            "inv": self.get_serialisable_inventory(),
            # "outmachines": self.output_machines  # client and server build upon adding
        }

        return details

    def rotate(self, new_rotation):
        # sets the rotation to the new rotation, calls the rotate func in the draw handler
        # WHEN CALLING ROTATE, NEED TO REBUILD OUTPUT_MACHINES
        self.rotation = new_rotation
        self.draw_handler.rotate(new_rotation)

        self.output_machine_tiles = self.get_tiles_outputted_to()  # reset the tiles outputted to


class ProcessingMachine(GenericMachine):
    # class for machines with input and output

    resource_in = {}  # dict with resourceconsumeritem and number needed
    resource_out = None  # resourceconsumeritem
    max_capacity = {}  # dict with resourceconsumeritem and max capacity, include resource_out

    def __init__(self, position, rotation):
        super().__init__(position, rotation)

        self.inventory = dict(zip(self.max_capacity.keys(), [0 for _ in range(len(self.max_capacity))]))  # all empty

    def input_item(self, item):
        # called when item is inputted to machine, returns true if able to accept, false if not

        # check that there is capacity in the inventory
        item_inventory = self.inventory.get(item, 0)
        item_inventory_max = self.max_capacity.get(item, -1)
        if item_inventory <= item_inventory_max:
            # accept item, increment and return True
            self.inventory[item] += 1
            return True
        else:
            return False  # do not accept item if the inventory does not accept the item or inventory if full of item

    def machine_process(self):
        # machine attempts to process items in its inventory

        # check according to speed, and if the inventory capacity for the output is not full
        if self.timer % self.speed == 0 and self.inventory[self.resource_out] < self.max_capacity[self.resource_out]:
            # check inventory to see if enough materials are available to produce output
            for key, item in self.inventory.items():
                if not item == self.resource_out:
                    if item <= self.resource_in.get(key, 0):
                        # item failed check
                        break
            else:
                # all requirements satisfied, subtract inputs from inventory
                for key, item in self.inventory.items():
                    if not item == self.resource_out:
                        self.inventory[key] -= self.resource_in.get(key, 0)
                self.inventory[self.resource_out] += 1  # place resource into inventory for output

        # at the end, increment the timer
        self.timer += 1

    def output_item(self):
        # attempts to output item from inventory to the first machine in the output_machines

        if self.output_callback is not None:  # check that callback it set
            if self.inventory[self.resource_out] > 0:  # check that inventory contains resource
                for output_tile in self.output_machine_tiles:  # try tiles in secession until success
                    if self.output_callback(self.resource_out, output_tile):
                        break
        else:
            print("OUTPUT CALLBACK NOT SET")
        self.shift_output_machines()


class ExtractingMachine(ProcessingMachine):
    # subclass for machines that do not take input

    def input_item(self, item):
        # override, always return false, never accept input
        return False

    def machine_process(self):
        # override, don't need to check requirements, only check for capacity for the output item
        if self.timer % self.speed == 0 and self.inventory[self.resource_out] < self.max_capacity[self.resource_out]:
            self.inventory[self.resource_out] += 1  # place resource into inventory for output

        # at the end, increment the timer
        self.timer += 1


class ConveyorMachine(GenericMachine):
    # for conveyors, custom inventory, rendering
    size = (1, 1)
    max_capacity = 10
    speed = 10
    # for rendering, use stages and increment every tick - need to keep order of inventory - queue?

    def __init__(self, position, rotation):
        super().__init__(position, rotation)
        self.rotation = rotation  # range(0, 4) - from 0 to 3 - with 0 pointing up

        self.inventory = []  # inventory created in super().__init__() already, but here needs to be list
        [self.inventory.append(EmptyIngotResource) for _ in range(self.max_capacity)]  # pre-populate with empty
        self.cur_tick_inputted = False

        self.draw_handler = ConveyorDrawHandler(self.image_name, self.position, rotation)

    def get_tiles_outputted_to(self):
        # gets the coordinates of the block that this conveyor outputs to - override for list of single position

        # convert the rotation value from range(0, 4) to correct offsets
        if self.rotation == 0:
            facing = (0, -1)
        elif self.rotation == 1:
            facing = (1, 0)
        elif self.rotation == 2:
            facing = (0, -1)
        elif self.rotation == 3:
            facing = (-1, 0)
        else:
            print("Rotation out of legal range")
            facing = (0, 0)

        x_output = self.position[0] + self.size[0] - 1 + facing[0]
        y_output = self.position[1] + self.size[1] - 1 + facing[1]

        return [(x_output, y_output)]

    def input_item(self, item):
        # accept input to the conveyor, add to queue, set flag that there has been an input this tick
        if len(self.inventory) < 10:
            self.inventory.append(item)
            self.cur_tick_inputted = True  # set flag so tick function knows not to add empty item
            return True
        else:
            return False

    def output_item(self):
        # output the oldest item to the output machine if not an EmptyIngotResource
        if not isinstance(self.inventory[0], EmptyIngotResource):  # check not empty
            if self.output_callback is not None:  # check callback is set
                for output_tile in self.output_machine_tiles:  # check output tiles in secession (only 1)
                    if self.output_callback(self.inventory[0], output_tile):
                        self.inventory.pop(0)
                        break
        self.shift_output_machines()

    def machine_process(self):
        # shifts items on conveyor forwards if there are EmptyIngotResources at the front
        if isinstance(self.inventory[0], EmptyIngotResource):
            self.inventory.pop(0)
            self.inventory.append(EmptyIngotResource)

        # at the end, increment the timer
        self.timer += 1

    def check_accept_resource(self, resource):
        # override, always accept ingot resources
        if isinstance(resource, IngotResource):
            return True
        else:
            return False

    def get_serialisable_inventory(self):
        # override, since the inventory is a list in this case
        return [i.id for i in self.inventory]
