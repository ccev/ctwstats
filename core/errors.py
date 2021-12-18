class BotError(Exception):
    msg = "Sorry, there was an error"


class HypixelError(BotError):
    msg = "There was an error contacting Hypixel, please try again later"


class MojangError(BotError):
    msg = "Sorry, either this player name doesn't exist or Mojang has issues right now."
