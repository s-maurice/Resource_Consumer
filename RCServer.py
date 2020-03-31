import asyncio
import json
import hashlib

from RCGame import ResourceConsumerGame
from RCMachines import machine_from_json
from RCMapTypes import RandomMap
from RCResources import Lead, Titanium, Sand, Glass
from RateHandlers import NetworkRateHandler, GameRateHandler
from SocketProtocol import protocol_read, protocol_write


class ResourceConsumerServer(object):

    def __init__(self, game_map):
        self.rcg = ResourceConsumerGame(game_map)
        self.hashed_password = None

        self.client_outgoing_queue = {}  # not real queue, just a list for each client of details to be sent

    def set_hashed_password(self, password):
        # takes password string and stores as class attribute
        self.hashed_password = hashlib.sha224(password.encode()).hexdigest()
        print("HASHED PW", self.hashed_password)

    async def establish_connection(self, reader, writer):
        # always runs, looking for new clients to connect
        password_attempt = await protocol_read(reader)  # need timeout, can be hijacked so no new clients can connect

        address = writer.get_extra_info('peername')
        print("INITIAL: from {} got pw attempt {}".format(address, password_attempt))

        # password checking
        if self.hashed_password == password_attempt:
            # on password success
            print("{} PW PASS".format(address))

            # build the details to send on connection
            # game_map is only sent when it is a custom game_map, otherwise the map can be loaded client-side
            if self.rcg.game_map.id == 0:
                initial_map = self.rcg.game_map.to_json_serialisable()
            else:
                initial_map = {"id": self.rcg.game_map.id}

            initial_dict = {
                "pw_auth": True,
                "game_map": initial_map,
                "placed_obj": [o.to_json_serialisable() for o in self.rcg.placed_objects],
                "inv": self.rcg.get_serialisable_inventory(),
                "tick": self.rcg.tick
            }

            # encode and send out
            print("INITIAL: Send {} to {}".format(initial_dict, address))
            await protocol_write(writer, json.dumps(initial_dict))

            # create and run task for the freshly connected
            # this allows for clients to disconnect without crashing server
            # wrap in try except to handle the task exception when the connections are closed
            connection_task = asyncio.create_task(self.handle_existing_connection(reader, writer))
            await connection_task
        else:
            # on password fail
            print("{} PW FAIL".format(address))

            initial_dict = {"pw_auth": False}
            initial_json = json.dumps(initial_dict)

            await protocol_write(writer, initial_json)

    async def handle_existing_connection(self, reader, writer):
        # one of these exists for each of the connected clients
        # infinitely loops, handling the main connection with the clients

        address = writer.get_extra_info('peername')

        # on task begin, create a queue for the data to be sent out to this client
        # tick too, but added just before send
        # self.client_outgoing_queue[address] = {"tick": 0, "placements": [], "removal_sel": [], "inventory": []}
        self.client_outgoing_queue[address] = {"placements": [], "removal_sel": [], "inventory": []}

        network_rate_handler = NetworkRateHandler(1)
        while True:
            network_rate_handler.period_start()

            # get incoming from client
            client_data = await protocol_read(reader)
            client_data = json.loads(client_data)
            print("Received {} from {}".format(client_data, address))

            # handle incoming
            # handle tick
            tick = client_data.get("tick", None)
            if tick is not None:
                if tick != self.rcg.tick:
                    print("DESYNC: client {} tick {}, server tick {}".format(address, tick, self.rcg.tick))

            # handle machine placement
            placements = client_data.get("placements", None)
            if placements is not None:
                for machine in placements:
                    machine = machine_from_json(machine)
                    if self.rcg.build_machine(machine):
                        # machine is built and added to out_queue for all clients
                        self.add_to_out_queue("placements", machine.to_json_serialisable())
                    # sync inventories with all clients, even on failure - as it means desync
                    self.add_to_out_queue("inventory", self.rcg.get_serialisable_inventory())

            # handle selection removal
            removal_sel = client_data.get("removal_sel", None)
            if removal_sel is not None:
                for removal in removal_sel:
                    self.rcg.dismantle_selection(removal)
                    # add to queue for all clients
                    self.add_to_out_queue("removal_sel", removal)
                    # resync all objects - but can be more selective in the future
                    [self.add_to_out_queue("resync_machines", o.to_json_serialisable()) for o in self.rcg.placed_objects]

            # handle outgoing
            # go through the outgoing_queue and find if the fields are populated, and create a minimised version
            outgoing_queue = {"tick": self.rcg.tick}
            for key, item in self.client_outgoing_queue[address].items():
                if len(item) > 0:
                    outgoing_queue[key] = item

            print("Sending {} to {}".format(outgoing_queue, address))
            await protocol_write(writer, json.dumps(outgoing_queue))
            self.clear_outgoing_queue(address)  # clear the outgoing queue for this client

            await network_rate_handler.period_end()

    def add_to_out_queue(self, key, item_to_append):
        # adds the given item_to_append to the queues of every client at the given key
        for client_dict in self.client_outgoing_queue.values():
            client_dict[key].append(item_to_append)

    def clear_outgoing_queue(self, client):
        # clears the outgoing queue for a single client
        self.client_outgoing_queue[client] = {"placements": [],
                                              "removal_sel": [],
                                              "inventory": [],
                                              "resync_machines": []}

    async def start_networking(self):
        # called to start the networking - constantly runs establish connection to try to establish new connections
        # server = await asyncio.start_server(self.establish_connection, '127.0.0.1', 8888)
        server = await asyncio.start_server(self.establish_connection, "", 8888)

        address = server.sockets[0].getsockname()
        print("Server started with address: ", address)

        async with server:
            await server.serve_forever()

    async def game_loop(self):
        # main loop for the game, controlling the game's tick speed
        game_rate_handler = GameRateHandler(1)

        while True:
            game_rate_handler.period_start()

            self.rcg.tick_game()
            print("Game Tick: ", self.rcg.tick)

            await game_rate_handler.period_end()

    async def main(self):
        # creates and runs the tasks
        game_task = asyncio.create_task(self.game_loop())
        networking_task = asyncio.create_task(self.start_networking())

        await game_task
        await networking_task


if __name__ == "__main__":
    random_game_map = RandomMap()
    rcs = ResourceConsumerServer(random_game_map)

    # for debug give resources
    rcs.rcg.inventory[Lead] = 1000
    rcs.rcg.inventory[Titanium] = 1000
    rcs.rcg.inventory[Sand] = 1000
    rcs.rcg.inventory[Glass] = 1000

    rcs.set_hashed_password("yeet")
    asyncio.run(rcs.main())
