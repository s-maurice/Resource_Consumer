import asyncio
import time

tick = 0
read_write_tasks = []


async def establish_connection(reader, writer):
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
    # wrap in try to handle the task exception when the connections are closed
    communication_task = asyncio.create_task(handle_connection(reader, writer))
    await communication_task


async def handle_connection(reader, writer):
    while True:
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {tick!r}")
        writer.write(str(tick).encode())
        await writer.drain()
        await asyncio.sleep(2)


async def loop():
    global tick
    while True:
        await asyncio.sleep(2)
        tick += 1
        print("tick:", tick)


async def main():
    server = await asyncio.start_server(establish_connection, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


async def bigmain():
    task1 = asyncio.create_task(loop())
    task2 = asyncio.create_task(main())

    await task1
    await task2

asyncio.run(bigmain())

