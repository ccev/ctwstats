from typing import Tuple, Union, Dict, List

import discord

from discord.application_commands import ApplicationCommand

from core.bot import bot


class BackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:up_:921863761852244068>", disabled=True)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.interaction.user.id:
            return
        self.view.page -= 1
        await self.view.update(interaction)


class ForwardButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:down:921863761780949142>", disabled=False)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.interaction.user.id:
            return
        self.view.page += 1
        await self.view.update(interaction)


class LBView(discord.ui.View):
    MAX_PAGE = 10

    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=3*60)
        self.interaction = interaction
        self.page: int = 0

        self.back_button = BackButton()
        self.forward_button = ForwardButton()
        self.add_item(self.back_button)
        self.add_item(self.forward_button)

    def _get_limits(self) -> Tuple[int, int]:
        return self.page * 10, 10

    async def get_stats(self) -> Tuple[List[Dict[str, Union[str, int]]], List[Dict[str, Union[str, int]]]]:
        caps = await bot.queries.execute(
            "select name, caps from players order by caps desc limit {}, {}".format(*self._get_limits()))

        kills = await bot.queries.execute(
            "select name, kills from players order by kills desc limit {}, {}".format(*self._get_limits()))

        return caps, kills

    @staticmethod
    def _get_text_part(payload: dict, i: int, stat: int) -> str:
        name = discord.utils.escape_markdown(payload['name'].replace("\\", ""))
        return f"{i}. **{name}** ({stat:,})\n"

    async def get_embed(self):
        cap_lb, kill_lb = await self.get_stats()

        embed = discord.Embed(title="Leaderboard")
        cap_text = ""
        for i, caps in enumerate(cap_lb, start=self.page * 10 + 1):
            cap_text += self._get_text_part(caps, i, caps["caps"])

        kill_text = ""
        for i, kills in enumerate(kill_lb, start=self.page * 10 + 1):
            kill_text += self._get_text_part(kills, i, kills["kills"])

        embed.add_field(name="Wool Captures", value=cap_text)
        embed.add_field(name="Kills+Assists", value=kill_text)
        embed.set_footer(text="Note that leaderboard positions are likely to be incorrect. /info")

        return embed

    async def update(self, interaction: discord.Interaction):
        self.back_button.disabled = self.page <= 0
        self.forward_button.disabled = self.page >= self.MAX_PAGE - 1
        embed = await self.get_embed()

        await interaction.response.edit_message(embed=embed, view=self)


class LeaderboardCommand(ApplicationCommand, name="leaderboard", description="See who has the most caps and kills"):
    async def callback(self, interaction: discord.Interaction) -> None:
        view = LBView(interaction)
        embed = await view.get_embed()
        await interaction.response.send_message(embed=embed, view=view)
