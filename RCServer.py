import asyncio
import json
import hashlib

from RCGame import ResourceConsumerGame
from RCMapTypes import RandomMap
from SocketProtocol import protocol_read, protocol_write


class ResourceConsumerServer(object):

    def __init__(self):
        game_map = RandomMap()
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
        print("FROM {} got pw attempt {}".format(address, password_attempt))

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
            initial_json = json.dumps(initial_dict)
            await protocol_write(writer, initial_json)

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

        # on task begin, create a queue for the data to be sent out to this client
        self.client_outgoing_queue[writer.get_extra_info('peername')] = []

        while True:
            message = await protocol_read(reader)

            address = writer.get_extra_info('peername')
            print("Received {} from {}".format(message, address))

            print("Sending tick: ", self.rcg.tick)
            await protocol_write(writer, str(self.rcg.tick))

            await asyncio.sleep(2)

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
        while True:
            self.rcg.tick_game()
            print(self.rcg.tick)
            await asyncio.sleep(2)

    async def main(self):
        # creates and runs the tasks
        game_task = asyncio.create_task(self.game_loop())
        networking_task = asyncio.create_task(self.start_networking())

        await game_task
        await networking_task


if __name__ == "__main__":
    rcs = ResourceConsumerServer()
    rcs.set_hashed_password("yeet")
    asyncio.run(rcs.main())
