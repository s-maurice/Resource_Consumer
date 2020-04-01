from RCMachineTypes import ProcessingMachine, ExtractingMachine, GenericMachine, DecorationMachine, ConveyorMachine
from RCResources import *


class Processor1(ProcessingMachine):
    id = 1
    image_name = "processor1"

    size = (2, 2)
    resource_in = {Sand: 1}  # dict with RCResource and number needed
    resource_out = Glass  # RCResource
    max_capacity = {Sand: 10, Glass: 10}  # dict with RCResource and max capacity, include resource_out
    speed = 10

    build_cost = {Copper: 20, Titanium: 1}  # dict with RCResource and number needed


class Processor2(ProcessingMachine):
    id = 2
    image_name = "processor2"

    size = (1, 1)
    resource_in = {Sand: 1}  # dict with RCResource and number needed
    resource_out = Glass  # RCResource
    max_capacity = {Sand: 10, Glass: 10}  # dict with RCResource and max capacity, include resource_out
    speed = 10

    build_cost = {Copper: 20, Titanium: 1}  # dict with RCResource and number needed


class Extractor1(ExtractingMachine):
    id = 3
    image_name = "extractor1"

    size = (2, 2)
    resource_in = {}  # empty dict
    resource_out = Sand  # RCResource
    max_capacity = {Sand: 10}  # only resource out and capacity
    speed = 10

    build_cost = {Copper: 20}  # dict with RCResource and number needed


class Extractor2(ExtractingMachine):
    id = 4
    image_name = "extractor2"

    size = (2, 2)
    resource_in = {}  # empty dict
    resource_out = Sand  # RCResource
    max_capacity = {Sand: 10}  # only resource out and capacity
    speed = 10

    build_cost = {Copper: 20}  # dict with RCResource and number needed


class Extractor3(ExtractingMachine):
    id = 5
    image_name = "extractor3"

    size = (1, 1)
    resource_in = {}  # empty dict
    resource_out = Sand  # RCResource
    max_capacity = {Sand: 10}  # only resource out and capacity
    speed = 10

    build_cost = {Copper: 20}  # dict with RCResource and number needed


class Rock1(DecorationMachine):
    id = 6
    image_name = "rock"

    size = (1, 1)
    speed = 0
    build_cost = {}


class Conveyor1(ConveyorMachine):
    id = 7
    image_name = "conveyor1"

    size = (1, 1)
    max_capacity = 10
    speed = 10


machine_id_lookup = {Processor1.id: Processor1,
                     Processor2.id: Processor2,
                     Extractor1.id: Extractor1,
                     Extractor2.id: Extractor2,
                     Extractor3.id: Extractor3,
                     Rock1.id: Rock1,
                     Conveyor1.id: Conveyor1
                     }


def machine_from_json(machine_dict):
    machine = machine_id_lookup.get(int(machine_dict.get("id")))  # get correct machine type
    machine = machine((machine_dict.get("pos")), machine_dict.get("rot"))  # call constructor
    # place in other attributes
    machine.time = machine_dict.get("time")

    # handle machine's inventory
    for key, item in machine_dict.get("inv").items():
        res = resource_id_lookup.get(int(key))
        machine.inventory[res] = item

    return machine
