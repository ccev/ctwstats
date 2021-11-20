from __future__ import annotations
import aiohttp
import tokens

from typing import List

from core.errors import HypixelError
from core.player import Player
from core.player import CTWAchievement


class HypixelApi:
    achievements: List[CTWAchievement] = []

    def __init__(self):
        self.url = "https://api.hypixel.net/{}?key={}&uuid={}"

    async def prepare_achievements(self):
        result = await self.request(uuid="229f1765-0ca1-4d67-9a41-e7cb198e4832", route="resources/achievements")
        one_times: dict = result["achievements"]["arcade"]["one_time"]
        for name, data in one_times.items():
            if name.startswith("CTW_"):
                self.achievements.append(CTWAchievement(name, data))

    async def request(self, uuid, route: str) -> dict:
        url = self.url.format(route, tokens.HYPIXEL, uuid)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    raise HypixelError

                result = await r.json()
                if not result.get("success", False):
                    raise HypixelError

                return result

    async def get_player(self, uuid) -> Player:
        data = await self.request(uuid, "player")
        player = Player(data)
        player.achievements = []
        for ach in self.achievements:
            if ach.id in player._completed_achs:
                player.achievements.append(ach)

        return player
