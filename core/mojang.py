from typing import Tuple

import aiohttp

from core.errors import MojangError


class MojangApi:
    def __init__(self):
        self.url = "https://api.mojang.com/users/profiles/minecraft/{}"

    async def get_player_info(self, name: str) -> Tuple[str, str]:
        """
        returns (name, uuid)
        """
        url = self.url.format(name)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    raise MojangError

                result = await r.json()
                return tuple(result.values())
