import asyncio

from RCGame import ResourceConsumerGame


class ResourceConsumerServer(object):

    def __init__(self):
        self.rcg = ResourceConsumerGame((20, 20))

    async def establish_connection(self, reader, writer):
        # always runs, looking for new clients to connect
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print(f"Received {message!r} from {addr!r}")

        in_message = "you're in"
        print(f"Send: {in_message!r}")
        writer.write(str(in_message).encode())
        await writer.drain()

        # create and run task for the freshly connected
        # this allows for clients to disconnect without crashing server
        # wrap in try except to handle the task exception when the connections are closed
        connection_task = asyncio.create_task(self.handle_existing_connection(reader, writer))
        await connection_task

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
asyncio.run(rcs.main())
