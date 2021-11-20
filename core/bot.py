import discord
import aiohttp

from typing import Dict

from core.queries import Queries
from core.hypixel import HypixelApi
from core.mojang import MojangApi


class CTWStats(discord.Client):
    def __init__(self):
        self._startup = True
        super().__init__(update_application_commands_at_startup=True)
        self.queries: Queries = Queries(self.loop)

        self.player_cache: Dict[str, str] = {}
        self.hypixel_api = HypixelApi()
        self.mojang_api = MojangApi()

    async def on_ready(self):
        if not self._startup:
            self._startup = False
            return

        await self.hypixel_api.prepare_achievements()

        players = await self.queries.execute("select uuid, name from players order by caps desc")
        for player in players:
            self.player_cache[player["uuid"]] = player["name"].replace("\\", "")

        print("ready")

    @staticmethod
    async def httpget(url: str, as_json: bool = False):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()


bot = CTWStats()
