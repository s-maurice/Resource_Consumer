import asyncio

writer = None
reader = None


async def connect_to_server(message):
    global writer, reader
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    await asyncio.sleep(2)


async def get_tick(message):
    while True:
        if reader is not None and writer is not None:
            print(f'Send: {message!r}')
            writer.write(message.encode())

            data = await reader.read(100)
            print(f'Received: {data.decode()!r}')

        await asyncio.sleep(2)


async def main():
    # task = asyncio.create_task(connect_to_server('im 1 connect'))
    await connect_to_server("im 2 connect")
    task2 = asyncio.create_task(get_tick('im 2'))
    # await task
    await task2


asyncio.run(main())
