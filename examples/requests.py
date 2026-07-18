# type: ignore
# ruff: noqa
import asyncio
from http import HTTPMethod

import tasto

from .mapper import SerializeToUser

request = tasto.Request(method=HTTPMethod.POST, url="https://example.com/api/users")
authorized_rquest = request.with_(Header("Authorization", "Bearer ..."))
authorized_request_with_user = request.with_(Query({"id": "123"}))


async def get_user(user_id: UserId) -> User:
    response: tasto.Response = await tasto.send(authorized_request_with_user)
    return SerializeToUser(response)


async def main() -> None:
    print(await get_user(UserId(123)))


if __name__ == "__main__":
    asyncio.run(main())
