import asyncio
from aioconsole import ainput

async def user_input():
    while True:
        raw = await ainput(">")
        raw = raw.split(" ", 2)
        server = raw[0]
        channel = raw[1]
        message = raw[2]
        print(f"{server}, {channel}, {message}")


async def print_something():
    while True:
        await asyncio.sleep(30)
        print('something')


async def main():
    tasks = [user_input(), print_something()]
    await asyncio.gather(*tasks)


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()