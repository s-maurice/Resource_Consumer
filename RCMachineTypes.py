from queue import Queue


class GenericMachine(object):
    # generic class for all machines
    image_name = "none"

    size = (1, 1)
    speed = 0
    build_cost = {}  # dict with resourceconsumeritem and number needed

    # these not always used
    resource_in = {}  # dict with resourceconsumeritem and number needed
    resource_out = None  # resourceconsumeritem
    max_capacity = {}  # dict with resourceconsumeritem and max capacity, include resource_out

    def __init__(self, position):
        self.image_location = "mineindustry_sprites/foreground/{}.png".format(self.image_name)

        self.timer = 0
        self.rotation = 0
        self.position = position

        self.output_machines = []  # list of the machines that this machine outputs to

    def build_cost_satisfied(self, inventory_dict):
        # takes a dict of the materials the player has, and compares it to the required materials in the build_cost
        for key, value in self.build_cost:
            if inventory_dict.get(key, 0) < value:
                return False
        else:
            return True

    def tiles_occupied(self):
        # returns a list of the tiles (x, y) occupied by this machine
        tiles = []
        for x in range(self.position[0], self.position[0] + self.size[0]):
            for y in range(self.position[1], self.position[1] + self.size[1]):
                tiles.append((x, y))
        return tiles

    def get_bounds(self):
        # returns a tuple of tuples with the corners of the machine ((x_left, y_top), (x_right, y_bottom))
        return self.position, (self.position[0] + self.size[0] - 1, self.position[1] + self.size[1] - 1)

    def get_touching_tiles(self):
        # returns a list of tiles touching the machine, will return out of bounds of board - need to check outside
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

    def check_accept_resource(self, resource):
        # checks if the machine could accept a certain resource
        # doesn't actually add it and ignores inventory size check
        if self.resource_in.get(resource, 0) > 0:
            return True
        else:
            return False

        
class ProcessingMachine(GenericMachine):
    # class for machines with input and output

    resource_in = {}  # dict with resourceconsumeritem and number needed
    resource_out = None  # resourceconsumeritem
    max_capacity = {}  # dict with resourceconsumeritem and max capacity, include resource_out

    def __init__(self, position):
        super().__init__(position)

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
            for key, item in self.inventory:
                if not item == self.resource_out:
                    if item <= self.resource_in.get(key, 0):
                        # item failed check
                        break
            else:
                # all requirements satisfied, subtract inputs from inventory
                for key, item in self.inventory:
                    if not item == self.resource_out:
                        self.inventory[key] -= self.resource_in.get(key, 0)
                self.inventory[self.resource_out] += 1  # place resource into inventory for output

    def output_item(self):
        # attempts to output item from inventory, returning item
        # TODO above this class need a func to place item into correct tile
        out_resource_count = self.inventory[self.resource_out]
        if out_resource_count > 0:
            self.inventory[self.resource_out] -= 1
            return self.resource_out
        else:
            return False

    def is_output_ready(self):
        # checks if machine has the output item in the inventory
        if self.inventory[self.resource_out] > 0:
            return True
        else:
            return False


class ExtractingMachine(ProcessingMachine):
    # subclass for machines that do not take input

    def input_item(self, item):
        # override, always return false, never accept input
        return False

    def machine_process(self):
        # override, don't need to check requirements, only check for capacity for the output item
        if self.timer % self.speed == 0 and self.inventory[self.resource_out] < self.max_capacity[self.resource_out]:
            self.inventory[self.resource_out] += 1  # place resource into inventory for output

    def is_output_ready(self):
        # checks if machine has the output item in the inventory
        if self.inventory[self.resource_out] > 0:
            return True
        else:
            return False


class ConveyorMachine(GenericMachine):
    # for conveyors, custom inventory, rendering
    size = (1, 1)
    max_capacity = 10
    speed = 10
    # for rendering, use stages and increment every tick - need to keep order of inventory - queue?

    def __init__(self, position, facing):
        super().__init__(position)
        self.facing = facing  # (x, y) tuple of offset

        self.inventory = Queue(maxsize=self.max_capacity)
        [self.inventory.put(None) for _ in range(self.max_capacity)]  # pre-populate with empty
        self.cur_tick_inputted = False

    def get_touching_tiles(self):
        # gets the coordinates of the block that this conveyor outputs to - override for list of len = 1 in conveyors
        x_output = self.position[0] + self.size[0] - 1 + self.facing[0]
        y_output = self.position[1] + self.size[1] - 1 + self.facing[1]

        return [x_output, y_output]

    def input_item(self, item):
        # accept input to the conveyor, add to queue, set flag that there has been an input this tick
        if not self.inventory.full():
            self.inventory.put(item, block=False)  # do not block program
            self.cur_tick_inputted = True  # set flag so tick function knows not to add empty item
            return True
        else:
            return False

    def output_item(self):
        # return the oldest item, or false if there is an empty conveyor slot
        output_item = self.inventory.get(block=False)  # do not block program - automatically pops the first item
        if output_item is not None:
            return output_item
        else:
            return False

    def machine_process(self):
        # as output_item automatically pops the last item, simply fill conveyor back up to full if not full
        if not self.inventory.full():
            self.inventory.put(None)

