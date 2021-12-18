from __future__ import annotations
import asyncio
from enum import Enum

import discord
from discord.application_commands import ApplicationCommand, option, ApplicationCommandMeta
from thefuzz import process

from core.bot import bot
from core.player_view import PlayerView


class FavoriteLevel(Enum):
    EXCLUDE = 0
    BOTH = 1
    ONLY_FAVORITES = 2


def autocomplete(interaction: discord.Interaction, favorite_level: FavoriteLevel = FavoriteLevel.BOTH) -> list:
    if not interaction.value or favorite_level == FavoriteLevel.ONLY_FAVORITES:
        if favorite_level.value > 0:
            favorites = bot.favorite_players.get(interaction.user.id)
            if favorites:
                return [bot.player_cache.get(uuid, "") for uuid in favorites]

        if favorite_level == FavoriteLevel.ONLY_FAVORITES:
            return ["You don't have any favorites"]

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
        # TODO botstats
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


class BotStatsCommand(ApplicationCommand, name="botstats",
                      description="View a player's leaderboard position and command lookups"):
    _page: int = 2
    player = option(description="The player's name", required=True)

    @player.autocomplete
    async def player_autocomplete(self, interaction: discord.Interaction):
        for r in autocomplete(interaction):
            yield r

    async def callback(self, interaction: discord.Interaction):
        callback = Callback(self._page, self.player, interaction)
        await callback.callback()


class InfoCommand(ApplicationCommand, name="info", description="General information about the bot"):
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed()
        embed.add_field(name="Hypixel limits", inline=False, value=(
            "Unfortunately, Hypixel doesn't like Capture The Wool very much, so the data we're able to get "
            "is super limited. There's not a lot I can show you. Sorry!"
        ))
        embed.add_field(name="Leaderboards", inline=False, value=(
            "The leaderboard is solely based on past lookups of players, so it can get very inaccurate on lower "
            "ranks. That's also why `/leaderboard` will only show you the top 100 players. When you see inaccurate "
            "names or stats, you can update them using a `/stats` lookup."
        ))
        embed.add_field(name="Credits", inline=False, value=(
            "I was made by @Malte#1748 and @qej#8895. Special thanks to Iets and Inventums!\n\n"
            "[Invite](https://discord.gg)    |    [GitHub](https://github.com/ccev/ctwstats)"
        ))
        await interaction.response.send_message(embed=embed)


class FavoriteCommand(ApplicationCommand, name="favorite", description="Manage your favorite players"):
    pass


class FavoriteAddCommand(ApplicationCommand, name="add", parent=FavoriteCommand,
                         description="Add a favorite player to show up first in command autocomplete"):
    player = option(description="The player's name", required=True)

    @player.autocomplete
    async def player_autocomplete(self, interaction: discord.Interaction):
        for r in autocomplete(interaction, favorite_level=FavoriteLevel.EXCLUDE):
            yield r

    async def callback(self, interaction: discord.Interaction) -> None:
        favorites = bot.favorite_players.get(interaction.user.id)
        name, uuid = await bot.mojang_api.get_player_info(self.player)

        keyvals = {
            "user_id": interaction.user.id,
            "uuid": uuid
        }
        # TODO limit favorites
        if favorites is None:
            favorites = bot.favorite_players[interaction.user.id] = {uuid}
            await bot.queries.insert("favorites", keyvals)
        elif uuid in favorites:
            await interaction.response.send_message(f"{name} is already in your favorites")
            return
        else:
            favorites.add(uuid)
            await bot.queries.insert("favorites", keyvals)

        await interaction.response.send_message(f"Added {name} to your favorites")

    async def command_error(self, interaction: discord.Interaction, error: Exception) -> None:
        # TODO: error handling
        await interaction.response.send_message(error.msg)


class FavoriteRemoveCommand(ApplicationCommand, name="remove", parent=FavoriteCommand,
                            description="Remove a player from your favorite list"):
    player = option(description="The player's name", required=True)

    @player.autocomplete
    async def player_autocomplete(self, interaction: discord.Interaction):
        for r in autocomplete(interaction, favorite_level=FavoriteLevel.ONLY_FAVORITES):
            yield r

    async def callback(self, interaction: discord.Interaction) -> None:
        favorites = bot.favorite_players.get(interaction.user.id)
        if not favorites:
            await interaction.response.send_message("You don't have any favorites")
            return
        name, uuid = await bot.mojang_api.get_player_info(self.player)

        if favorites is None or uuid not in favorites:
            await interaction.response.send_message(f"{name} is not in your favorites")
        else:
            favorites.remove(uuid)
            await interaction.response.send_message(f"Removed {name} from your favorites")
        # TODO responses, db
