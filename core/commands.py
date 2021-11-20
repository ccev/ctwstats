from __future__ import annotations
import asyncio

import discord
from discord.application_commands import ApplicationCommand, option, ApplicationCommandMeta
from thefuzz import process

from core.bot import bot
from core.player_view import PlayerView


def autocomplete(interaction: discord.Interaction):
    if not interaction.value:
        return list(bot.player_cache.values())[:5]

    result: str = process.extractOne(interaction.value, bot.player_cache.values())[0]

    if result.casefold() == interaction.value.casefold():
        return [result]
    else:
        return [interaction.value, result]


class Callback:
    def __init__(self, page: int, name, interaction: discord.Interaction):
        self.page = page
        self.name = name
        self.interaction = interaction

        self.responded = False
        self.followup_message = None

    async def loading_message(self):
        await asyncio.sleep(2.5)
        if self.responded:
            return
        self.responded = True
        await self.interaction.response.send_message("Give me another second...")
        self.followup_message = await self.interaction.original_message()

    async def callback(self):
        bot.loop.create_task(self.loading_message())
        if self.name in bot.player_cache.values():
            uuid = list(bot.player_cache.keys())[list(bot.player_cache.values()).index(self.name)]
        else:
            name, uuid = await bot.mojang_api.get_player_info(self.name)
            bot.player_cache[uuid] = name

        player = await bot.hypixel_api.get_player(uuid)
        bot.player_cache[uuid] = player.name

        view = PlayerView(self.interaction, player, self.page)

        if self.responded:
            while not self.followup_message:
                await asyncio.sleep(0.1)

            await self.interaction.followup.edit_message(self.followup_message.id,
                                                         content="", embed=view.embed, view=view)
        else:
            self.responded = True
            await self.interaction.response.send_message(embed=view.embed, view=view)


class StatsCommand(ApplicationCommand, name="stats", description="Query a player's stats"):
    _page: int = 0
    player = option(description="The player's name", required=True)

    @player.autocomplete
    async def player_autocomplete(self, interaction: discord.Interaction):
        for r in autocomplete(interaction):
            yield r

    async def callback(self, interaction: discord.Interaction):
        callback = Callback(self._page, self.player, interaction)
        await callback.callback()


class AchievementsCommand(ApplicationCommand, name="achievements", description="Query a player's achievements"):
    _page: int = 1
    player = option(description="The player's name", required=True)

    @player.autocomplete
    async def player_autocomplete(self, interaction: discord.Interaction):
        for r in autocomplete(interaction):
            yield r

    async def callback(self, interaction: discord.Interaction):
        callback = Callback(self._page, self.player, interaction)
        await callback.callback()
