from __future__ import annotations

import discord

from core.player import Player
from core.bot import bot


class CategorySelect(discord.ui.Select):
    def __init__(self, default: int):
        super().__init__(placeholder="Choose a page", options=[])
        self.current_page = default

        for i, label in enumerate(["Stats", "Achievements", "Bot Stats"]):
            self.add_option(label=label, value=str(i), default=default == i)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.author:
            return
        self.current_page = int(self.values[0])
        for i, option in enumerate(self.options):
            option.default = i == self.current_page
        await self.view.make_embed()
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)


class PlayerView(discord.ui.View):
    embed: discord.Embed

    def __init__(self, interaction: discord.Interaction, player: Player, page: int = 0):
        super().__init__(timeout=3*60)
        self.interaction = interaction
        self.player = player
        self.author = interaction.user.id
        self.select = CategorySelect(page)
        self.add_item(self.select)

    async def make_embed(self):
        if self.select.current_page == 0:
            self.make_stat_embed()
        elif self.select.current_page == 1:
            self.make_achievement_embed()
        elif self.select.current_page == 2:
            await self.make_botstats_embed()

    def make_stat_embed(self):
        self.embed = discord.Embed(
            title=f"{discord.utils.escape_markdown(self.player.name)}'s Stats",
            description=(
                f"Captures: **{self.player.caps:,}**\n"
                f"Kills+Assists: **{self.player.kills:,}**\n"
                f"Achievements: **{len(self.player.achievements)}/{len(bot.hypixel_api.achievements)}**"
            )
        )
        self.embed.set_thumbnail(url=self.player.bust)

    def make_achievement_embed(self):
        self.embed = discord.Embed(
            title=f"{self.player.name}'s Achievements"
        )
        self.embed.set_thumbnail(url=self.player.bust)
        for ach in bot.hypixel_api.achievements:
            if ach in self.player.achievements:
                emote = "✅ "
            else:
                emote = "❌ "
            self.embed.add_field(
                name=emote + ach.name.replace("Capture the Wool: ", ""),
                value=ach.desc,
                inline=False
            )

    async def make_botstats_embed(self):
        # possible TODO: save botstats in self.player object
        stats = await bot.queries.execute(
            (
                "select count(distinct(s.user_id)) as stats, count(distinct(a.user_id)) as achievements "
                "from players "
                "left join stats_queried s on players.uuid = s.uuid "
                "left join achievements_queried a on players.uuid = a.uuid "
                f"where players.uuid = %s"
            ),
            args=self.player.uuid
        )
        stats = stats[0]

        lb = await bot.queries.execute(
            (
                "select "
                "(select count(*) from players where caps > (select caps from players where uuid = %s)) as caps, "
                "(select count(*) from players where kills > (select kills from players where uuid = %s)) as kills "
            ),
            args=(self.player.uuid, self.player.uuid)
        )
        lb = lb[0]

        self.embed = discord.Embed(
            title=f"{discord.utils.escape_markdown(self.player.name)}'s Bot Stats",
        )
        self.embed.set_thumbnail(url=self.player.bust)
        self.embed.add_field(
            name="Leaderboard positions",
            value=f"Wool Captures: **#{lb['caps'] + 1}**\nKills+Assists: **#{lb['kills'] + 1}**",
            inline=False
        )
        self.embed.add_field(
            name="Unique lookups",
            value=f"/stats: **{stats['stats']}**\n/achievements: **{stats['achievements']}**",
            inline=False
        )

        if max(lb["caps"], lb["kills"]) > 30:
            self.embed.set_footer(text="Note that leaderboard positions are likely to be incorrect. /info")

    async def on_timeout(self):
        followup = self.interaction.followup
        message = await self.interaction.original_message()
        for item in self.children:
            item.disabled = True
        await followup.edit_message(message.id, view=self)
