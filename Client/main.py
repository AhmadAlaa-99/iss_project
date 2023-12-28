import asyncio
import Messages.NewUser as newUser


async def main():
    user_ms = newUser.NewUserMessage('AhmadAlaa', 'password')
    print(user_ms.to_json_string())
    await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
