import asyncio
import time

tick = 0
read_write = []


async def establish_connection(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print(f"Received {message!r} from {addr!r}")

    in_message = "you're in"
    print(f"Send: {in_message!r}")
    writer.write(str(in_message).encode())
    await writer.drain()

    read_write.append((reader, writer))


async def handle_connections():
    while True:
        for reader, writer in read_write:
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
        print("tick:", tick, len(read_write))


async def main():
    server = await asyncio.start_server(establish_connection, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


async def bigmain():
    task1 = asyncio.create_task(loop())
    task2 = asyncio.create_task(main())
    task3 = asyncio.create_task(handle_connections())

    await task1
    await task2
    await task3

asyncio.run(bigmain())

