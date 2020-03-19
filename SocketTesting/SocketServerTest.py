import asyncio
import time

tick = 0


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(str(tick).encode())
    await writer.drain()

    print("Close the connection")
    writer.close()


async def loop():
    global tick
    while True:
        await asyncio.sleep(1)
        tick += 1
        print(tick)


async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)

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

