import asyncio
import Messages.NewUser as newUser
from Controller import ClientController as cc
from Controller import InputController as Ic


async def main():
    task = asyncio.create_task(cc.Client().handle())
    await task


def exceptionHandler(loop: asyncio.AbstractEventLoop, dic: dict):
    pass


if __name__ == '__main__':
    try:
        inp = Ic.CMDInput()
        inp.init_input_ui()
        inp.operations_ui()
    except KeyboardInterrupt as e:
        print("Forced Closed")
