import asyncio
import Messages.NewUser as newUser
from Controller import ClientController as cc


async def main():
    task = asyncio.create_task(cc.Client().handle())
    await task


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Forced Closed")
