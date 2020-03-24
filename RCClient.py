import asyncio
import hashlib
import json

from RCScreen import RCScreen
from RCGame import ResourceConsumerGame
from RCMachines import machine_id_lookup
from RCMaps import *
from RCResources import resource_id_lookup
from SocketProtocol import protocol_read, protocol_write


class ResourceConsumerClient(object):

    def __init__(self):
        self.reader = None
        self.writer = None

        self.TEMP_PW = "yeet"
        self.sending_message = "hi"

        self.rcg = None
        self.rcs = None

    async def connect_to_server(self):
        # searches for and establishes initial connection with the server, returning the reader and writer for later use
        while True:
            reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

            # hash password to compare
            password_attempt = self.TEMP_PW
            password_hashed = hashlib.sha224(password_attempt.encode()).hexdigest()

            print("Send pw", password_hashed)
            await protocol_write(writer, password_hashed)

            data = await protocol_read(reader)
            print("Receive", data)

            initial_dict = json.loads(data)
            # check if password is accepted
            if initial_dict["pw_auth"]:

                # once the dict with initial details has been received, init RCGame and put in the details
                self.rcg = ResourceConsumerGame()

                # TODO re-builder funcs for all the things that need rebuilding

                # handle map
                game_map_dict = initial_dict.get("game_map", None)
                if game_map_dict is not None:
                    map_id = game_map_dict.get("id", -1)
                    print(map_id)
                    if map_id == 0:
                        # custom map, need to build
                        map_obj = RCMap()
                        map_obj.background_map = np.array(game_map_dict["bg"])
                        map_obj.background_addition_map = np.array(game_map_dict["bga"])
                        # placed objects handled later
                        self.rcg.game_map = map_obj
                    elif map_id > 0:
                        # defined map in the RCMaps
                        self.rcg.game_map = map_id_lookup.get(map_id)
                    else:
                        # no map sent, error
                        pass

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

                    # since initial build - ignore resource checks
                    # this way the output_machines for the machines are built by the client's game
                    self.rcg.build_tile(machine, ignore_check=True)

                # handle game inventory
                for key, item in initial_dict.get("inv"):
                    res = resource_id_lookup.get(key)
                    self.rcg.inventory[res] = item

                # handle tick
                self.rcg.tick = initial_dict.get("tick")

                return reader, writer
            elif not initial_dict["pw_auth"]:
                # password not authenticated - wait and then loop back around
                print("pw rejected")
                await asyncio.sleep(3)

    async def handle_connection(self):
        # infinitely loops, handling the main connection with the server
        while True:
            print("Send", self.sending_message)
            await protocol_write(self.writer, self.sending_message)

            data = await protocol_read(self.reader)
            print("Receive", data)

            await asyncio.sleep(2)

    async def game_loop(self):
        # main loop for the game, controlling the game's tick speed
        while True:
            self.rcg.tick_game()
            print("client tick")
            await asyncio.sleep(2)

    async def game_render_loop(self):
        self.rcs = RCScreen(self.rcg)
        await self.rcs.main()

    async def main(self):
        # establish communication
        networking_task = asyncio.create_task(self.connect_to_server())
        self.reader, self.writer = await networking_task

        # once connection has been established

        # create and run the main game loop task and renderer task
        game_task = asyncio.create_task(self.game_loop())
        render_task = asyncio.create_task(self.game_render_loop())

        # create and run the communication task
        communication_task = asyncio.create_task(self.handle_connection())

        await game_task
        await render_task
        await communication_task


rcc = ResourceConsumerClient()
asyncio.run(rcc.main())
