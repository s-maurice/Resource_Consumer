from asyncio import StreamReader, StreamWriter, Protocol

# possibly extend asyncio.Protocol instead
# sending eof auto closes the streams - so that won't wonk


async def protocol_read(reader: StreamReader):
    # reads using the protocol (first two bytes is the message length)
    read_len_bytes = await reader.read(2)
    read_len = int.from_bytes(read_len_bytes, byteorder="big", signed=False)

    message = await reader.read(read_len)
    return message.decode()


async def protocol_write(writer: StreamWriter, message: str):
    # writes using the protocol (first two bytes is the message length)
    message = message.encode()
    write_len_bytes = int.to_bytes(len(message), 2, byteorder="big", signed=False)

    writer.write(write_len_bytes + message)
    await writer.drain()
