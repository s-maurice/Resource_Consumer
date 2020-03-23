import asyncio
import json

from RCGame import ResourceConsumerGame
from RCMachines import machine_id_lookup
from RCMaps import *
from RCResources import resource_id_lookup


class ResourceConsumerClient(object):

    def __init__(self):
        self.reader = None
        self.writer = None

        self.connection_message = "connection message"
        self.sending_message = "hi"

        self.rcg = None

    async def connect_to_server(self):
        # searches for and establishes initial connection with the server, returning the reader and writer for later use
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

        print("Send", self.connection_message)
        writer.write(self.connection_message.encode())

        data = await reader.read(100)
        print("Receive", data.decode())

        initial_dict = json.loads(data)
        initial_dict = {}
        # once the dict with initial details has been received, init RCGame and put in the details
        self.rcg = ResourceConsumerGame()

        # TODO re-builder funcs for all the things that need rebuilding

        # handle map
        map_id = initial_dict.get("map", 0)
        if map_id == 0:
            # custom map, need to build
            map_obj = RCMap()
            map_obj.background_map = initial_dict["bg"]
            map_obj.background_addition_map = initial_dict["bga"]
            # placed objects handled later
            self.rcg.game_map = map_obj
        else:
            # defined map in the RCMaps
            self.rcg.game_map = map_id_lookup.get(map_id)

        # handle placed objects
        for machine_dict in initial_dict.get("placed_obj"):

            machine = machine_id_lookup.get(machine_dict.get("id"))  # get correct machine type
            machine = machine((machine_dict.get("pos")), machine_dict.get("rot"))  # call constructor
            # place in other attributes
            machine.time = machine_dict.get("time")

            # handle machine's inventory
            for key, item in machine_dict.get("inv"):
                res = resource_id_lookup.get(key)
                machine.inventory[res] = item

            # since initial build - ignore resource checks - this way the output_machines for the machines are built
            self.rcg.build_tile(machine, ignore_check=True)

        # handle game inventory
        for key, item in initial_dict.get("inv"):
            res = resource_id_lookup.get(key)
            self.rcg.inventory[res] = item

        # handle tick
        self.rcg.tick = initial_dict.get("tick")

        return reader, writer

    async def handle_connection(self):
        # infinitely loops, handling the main connection with the server
        while True:
            print("Send", self.sending_message)
            self.writer.write(self.sending_message.encode())

            data = await self.reader.read(100)
            print("Receive", data.decode())

            await asyncio.sleep(2)

    async def game_loop(self):
        # main loop for the game, controlling the game's tick speed
        while True:
            self.rcg.tick_game()
            print("client tick")
            await asyncio.sleep(2)

    async def main(self):
        # establish communication
        networking_task = asyncio.create_task(self.connect_to_server())
        self.reader, self.writer = await networking_task

        # once connection has been established
        # create and run the main game loop task
        game_task = asyncio.create_task(self.game_loop())
        # create and run the communication task
        communication_task = asyncio.create_task(self.handle_connection())

        await game_task
        await communication_task


rcc = ResourceConsumerClient()
asyncio.run(rcc.main())
