class BotError(Exception):
    msg = "Sorry, there was an error"


class HypixelError(BotError):
    msg = "There was an error contacting Hypixel, please try again later"


class MojangError(BotError):
    msg = "There was an error contacting Mojang, please try again later"
