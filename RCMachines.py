from RCMachineTypes import ProcessingMachine, ExtractingMachine, GenericMachine
from RCResources import Sand, Lead, Glass, Titanium


class Machine1(ProcessingMachine):
    image_name = "machine1"

    size = (2, 2)
    resource_in = {Sand: 1}  # dict with RCResource and number needed
    resource_out = Glass  # RCResource
    max_capacity = {Sand: 10, Glass: 10}  # dict with RCResource and max capacity, include resource_out
    speed = 10

    build_cost = {Lead: 20, Titanium: 1}  # dict with RCResource and number needed


class Extractor1(ExtractingMachine):
    image_name = "extractor1"

    size = (2, 2)
    resource_in = {}  # empty dict
    resource_out = Sand  # RCResource
    max_capacity = {Sand: 10}  # only resource out and capacity
    speed = 10

    build_cost = {Lead: 20}  # dict with RCResource and number needed


class Rock1(GenericMachine):
    image_name = "rock"

    size = (1, 1)
    speed = 0
    build_cost = {}
