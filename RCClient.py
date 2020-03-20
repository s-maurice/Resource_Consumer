import asyncio


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
            # self.rcg.tick_game()
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
