import asyncio
from ragtools import stream_query

async def main():
    i = 0
    async for chunk in stream_query("hello world"):
        print("CHUNK:", chunk)
        i += 1
        if i > 5:
            break

if __name__ == '__main__':
    asyncio.run(main())
