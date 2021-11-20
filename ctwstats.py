from core.bot import bot
from core.commands import StatsCommand, AchievementsCommand
import tokens

bot.add_application_commands(StatsCommand, AchievementsCommand, guild_id=911719424455766016)
bot.run(tokens.DISCORD)
