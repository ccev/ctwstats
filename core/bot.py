import discord
import aiohttp

from typing import Dict, Set

from core.queries import Queries
from core.hypixel import HypixelApi
from core.mojang import MojangApi


class CTWStats(discord.Client):
    def __init__(self):
        self._startup = True
        super().__init__(update_application_commands_at_startup=True)
        self.queries: Queries = Queries(self.loop)

        self.player_cache: Dict[str, str] = {}
        self.favorite_players: Dict[int, Set[str]] = dict()
        self.hypixel_api = HypixelApi()
        self.mojang_api = MojangApi(self)

    async def on_ready(self):
        if not self._startup:
            self._startup = False
            return

        await self.hypixel_api.prepare_achievements()

        players = await self.queries.execute("select uuid, name from players order by caps desc")
        for player in players:
            self.player_cache[player["uuid"]] = player["name"].replace("\\", "")

        favorites = await self.queries.execute("select user_id, uuid from favorites", as_dict=False)
        for user_id, uuid in favorites:
            favorite = self.favorite_players.get(user_id)
            if not favorite:
                self.favorite_players[user_id] = {uuid}
            else:
                favorite.add(uuid)

        print("ready")

    @staticmethod
    async def httpget(url: str, as_json: bool = False):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()


bot = CTWStats()
