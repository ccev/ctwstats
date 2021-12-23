from core.bot import bot
from core.commands import StatsCommand, AchievementsCommand, BotStatsCommand, InfoCommand, FavoriteCommand,\
    FavoriteAddCommand
from core.leaderboard import LeaderboardCommand
from core.errors import BotError
import tokens
import discord
import traceback


async def command_error(self, interaction: discord.Interaction, error: Exception) -> None:
    if isinstance(error, BotError):
        message = error.msg
    else:
        message = "Sorry, there was an unknown error"
        print("Unknown error", error)
        print(traceback.format_exc())

    error_embed = discord.Embed(description="❌ " + message, color=16073282)
    await interaction.response.send_message(embed=error_embed)

for command in [StatsCommand, AchievementsCommand, BotStatsCommand, LeaderboardCommand, InfoCommand,
                FavoriteCommand, FavoriteAddCommand]:
    command.command_error = command_error
    bot.add_application_command(command, guild_id=497894919864713226)

bot.run(tokens.DISCORD)
