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

    # once connection has been established, create and run the communication task
    communication_task = asyncio.create_task(get_tick())
    await communication_task


async def get_tick():
    message = "hi"
    while True:
        if reader is not None and writer is not None:
            print(f'Send: {message!r}')
            writer.write(message.encode())

            data = await reader.read(100)
            print(f'Received: {data.decode()!r}')

        await asyncio.sleep(2)


async def main():
    networking_task = asyncio.create_task(connect_to_server('im 1 connect'))
    await networking_task

asyncio.run(main())
