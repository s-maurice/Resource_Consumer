import asyncio
import json
import hashlib

from RCGame import ResourceConsumerGame


class ResourceConsumerServer(object):

    def __init__(self):
        self.rcg = ResourceConsumerGame()
        self.hashed_password = None

    def set_hashed_password(self, password):
        # takes password string and stores as class attribute
        self.hashed_password = hashlib.sha224(password.encode()).hexdigest()
        print("HASHED PW", self.hashed_password)

    async def establish_connection(self, reader, writer):
        # always runs, looking for new clients to connect
        data = await reader.read(100)
        password_attempt = data.decode()
        addr = writer.get_extra_info('peername')
        print("FROM {} got pw attempt {}".format(addr, password_attempt))

        # password checking
        if self.hashed_password == password_attempt:
            # on password success
            print("{} PW PASS".format(addr))

            # build the details to send on connection
            # game_map is only sent when it is a custom game_map, otherwise the map can be loaded client-side
            if self.rcg.game_map.id != 0:
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

            writer.write(initial_json.encode())
            await writer.drain()

            # create and run task for the freshly connected
            # this allows for clients to disconnect without crashing server
            # wrap in try except to handle the task exception when the connections are closed
            connection_task = asyncio.create_task(self.handle_existing_connection(reader, writer))
            await connection_task
        else:
            # on password fail
            print("{} PW FAIL".format(addr))

            initial_dict = {"pw_auth": False}
            initial_json = json.dumps(initial_dict)

            writer.write(initial_json.encode())
            await writer.drain()

    async def handle_existing_connection(self, reader, writer):
        # one of these exists for each of the connected clients
        # infinitely loops, handling the main connection with the clients
        while True:
            data = await reader.read(100)
            message = data.decode()
            address = writer.get_extra_info('peername')
            print("Received {} from {}".format(message, address))

            print("Sending tick: ", self.rcg.tick)
            writer.write(str(self.rcg.tick).encode())
            await writer.drain()

            await asyncio.sleep(2)

    async def start_networking(self):
        # called to start the networking - constantly runs establish connection to try to establish new connections
        server = await asyncio.start_server(self.establish_connection, '127.0.0.1', 8888)

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


rcs = ResourceConsumerServer()
rcs.set_hashed_password("yeet")
asyncio.run(rcs.main())
