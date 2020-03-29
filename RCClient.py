import asyncio
import hashlib
import json

from RCScreen import RCScreen
from RCGame import ResourceConsumerGame
from RCMachines import machine_id_lookup, machine_from_json
from RCMaps import *
from RCMapTypes import SentMap
from RCResources import resource_id_lookup, inventory_from_json
from RateHandlers import GameRateHandler, NetworkRateHandler
from SocketProtocol import protocol_read, protocol_write


class ResourceConsumerClient(object):

    def __init__(self):
        self.reader = None
        self.writer = None

        self.TEMP_PW = "yeet"

        self.rcg = None
        self.rcs = None

        # self.outgoing_queue = {"tick": 0, "placements": [], "removal_sel": []}  # tick too, but added on send
        self.outgoing_queue = {"placements": [], "removal_sel": []}  # dict for data to be sent to server

    async def connect_to_server(self):
        # searches for and establishes initial connection with the server, returning the reader and writer for later use
        while True:
            # reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
            reader, writer = await asyncio.open_connection("", 8888)

            # hash password to compare
            password_attempt = self.TEMP_PW
            password_hashed = hashlib.sha224(password_attempt.encode()).hexdigest()

            print("INITIAL: Send pw", password_hashed)
            await protocol_write(writer, password_hashed)

            data = await protocol_read(reader)
            print("INITIAL: Receive", data)

            initial_dict = json.loads(data)
            # check if password is accepted
            if initial_dict["pw_auth"]:
                # once the dict with initial details has been received, init RCGame and put in the details

                # TODO re-builder funcs for all the things that need rebuilding

                # handle map
                game_map_dict = initial_dict.get("game_map", None)
                if game_map_dict is not None:
                    map_id = game_map_dict.get("id", -1)
                    print(map_id)
                    if map_id == 0:
                        # custom map, need to build
                        size = game_map_dict["size"]
                        background_map = np.array(game_map_dict["bg"])
                        background_addition_map = np.array(game_map_dict["bga"])
                        map_obj = SentMap(size, background_map, background_addition_map)
                        # placed objects are handled later
                        # once map is ready, can init the game with the map
                        self.rcg = ResourceConsumerGame(map_obj)
                    elif map_id > 0:
                        # defined map in the RCMaps
                        map_obj = map_id_lookup.get(map_id)
                        # once map is ready, can init the game with the map
                        self.rcg = ResourceConsumerGame(map_obj)
                    else:
                        # no map sent, error
                        pass

                # handle placed objects
                for machine_dict in initial_dict.get("placed_obj"):
                    machine = machine_from_json(machine_dict)

                    # since initial build - ignore resource checks
                    # this way the output_machines for the machines are built by the client's game
                    self.rcg.build_machine(machine, ignore_check=True, ignore_build_cost=True)

                # handle game inventory
                self.rcg.inventory = inventory_from_json(initial_dict.get("inv"))

                # handle tick
                self.rcg.tick = initial_dict.get("tick")

                return reader, writer
            elif not initial_dict["pw_auth"]:
                # password not authenticated - wait and then loop back around
                print("pw rejected")
                await asyncio.sleep(3)

    async def handle_connection(self):
        # infinitely loops, handling the main connection with the server
        network_rate_handler = NetworkRateHandler(1)
        while True:
            network_rate_handler.period_start()

            # go through the outgoing_queue and find if the fields are populated, and create a minimised version
            outgoing_queue = {"tick": self.rcg.tick}
            for key, item in self.outgoing_queue.items():
                if len(item) > 0:
                    outgoing_queue[key] = item

            print("Send:", outgoing_queue)
            await protocol_write(self.writer, json.dumps(outgoing_queue))
            self.clear_outgoing_queue()

            # get data incoming from server
            server_data = await protocol_read(self.reader)
            server_data = json.loads(server_data)
            print("Receive:", server_data)

            # handle incoming
            tick = server_data.get("tick", None)
            if tick is not None:
                # tick should never be none
                if tick != self.rcg.tick:
                    print("DESYNC: server tick {}, client tick {}".format(tick, self.rcg.tick))

            placements = server_data.get("placements", None)
            if placements is not None:
                for machine in placements:
                    # handle machine placement here

                    machine = machine_from_json(machine)
                    if not self.rcg.build_machine(machine):
                        print("DESYNC: server could build machine but client could not")

            removal_sel = server_data.get("removal_sel", None)
            if removal_sel is not None:
                for removal in removal_sel:
                    # handle selection removal here

                    pass

            inv_dict = server_data.get("inventory", None)
            if inv_dict is not None:
                # handle inventory synchronisation here
                self.rcg.inventory = inventory_from_json(inv_dict[0])

                # for debug, iterate through and print differences
                # for key, item in inv_dict.items():
                #     res = resource_id_lookup.get(int(key))
                #     if self.rcg.inventory[res] != item:
                #         print("DESYNC: inv resource {} not matching. Server: {}, Client: {}".format(res, item, self.rcg.inventory[res]))
                #     self.rcg.inventory[res] = item

            await network_rate_handler.period_end()

    def add_to_outgoing_queue(self, key, item_to_append):
        # takes a key and item to append to one of the lists in the outgoing queue
        # used by the screen to callback player inputs to be sent to the server
        # ensure that the item_to_append is json.dumps() able
        self.outgoing_queue[key].append(item_to_append)

    def clear_outgoing_queue(self):
        self.outgoing_queue = {"placements": [], "removal_sel": []}

    async def game_loop(self):
        # main loop for the game, controlling the game's tick speed
        game_rate_handler = GameRateHandler(1)
        while True:
            game_rate_handler.period_start()

            self.rcg.tick_game()
            print("Client Tick: ", self.rcg.tick)

            await game_rate_handler.period_end()

    async def game_render_loop(self):
        self.rcs = RCScreen(self.rcg, self.add_to_outgoing_queue)
        await self.rcs.main()

    async def main(self):
        # establish communication
        networking_task = asyncio.create_task(self.connect_to_server())
        self.reader, self.writer = await networking_task

        # once connection has been established
        # await asyncio.sleep(1)  # wait so client isn't ahead of server

        # create and run the main game loop task and renderer task
        game_task = asyncio.create_task(self.game_loop())
        render_task = asyncio.create_task(self.game_render_loop())

        # create and run the communication task
        communication_task = asyncio.create_task(self.handle_connection())

        await game_task
        await render_task
        await communication_task


if __name__ == "__main__":
    rcc = ResourceConsumerClient()
    asyncio.run(rcc.main(), debug=False)
