from core.bot import bot
from core.commands import StatsCommand, AchievementsCommand, BotStatsCommand, InfoCommand, FavoriteCommand,\
    FavoriteAddCommand
from core.leaderboard import LeaderboardCommand
import tokens

bot.add_application_commands(StatsCommand, AchievementsCommand, BotStatsCommand, LeaderboardCommand, InfoCommand,
                             FavoriteCommand, FavoriteAddCommand,
                             guild_id=911719424455766016)
bot.run(tokens.DISCORD)
