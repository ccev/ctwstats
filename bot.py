import discord
import requests
import json

from discord.ext import commands
from datetime import datetime

from botstats import Stats

with open("tokens.json", "r") as f:
    tokens = json.load(f)

DISCORD_TOKEN = tokens["discord_token"]
HYPIXEL_TOKEN = tokens["hypixel_token"]

bot = commands.Bot(command_prefix="/", case_insensitive=1)
ach_api = requests.get(f"https://api.hypixel.net/resources/achievements?key={HYPIXEL_TOKEN}&uuid=229f1765-0ca1-4d67-9a41-e7cb198e4832").json()["achievements"]["arcade"]["one_time"]

bot_stats = Stats()

class Error(Exception):
    pass

async def send_error(m, error):
    embed = discord.Embed(description=f"❌ {error}", color=16073282)
    await m.edit(embed=embed)

async def send_loading(ctx):
    embed = discord.Embed()
    embed.set_footer(text="Loading...", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    m = await ctx.send(embed=embed)
    return m

wkplayers = [
    '7155b607f80d425c85257a8fecc32d6f',
    '1d236af11269409e82ffe2debe1fccd7',
    '403d437d2ee04457a39d7b62811e6f08',
    '1fc97172c4964966872086f19da147a5',
    'c7d988d6b15c4cc3af3d13ff8ed2ba12',
    '6b8e87f8e39646beb82707b7cfaa1f6b',
    '1fc4ccd429f248a29359ac7a4a445823',
    'dd4c96b53b284e0ca700afe1ed8d81f0',
    '15280eedbbf54e50b04251f03149ca07',
    '12701cc56c7142a1ba605d92fdf1395e',
    'da328728d87a45ff9bcbbc4590e2cc40',
    '4939702ade65467a9174375945969d49',
    '6349a0a3d61c43d7abefde803b1ce07c',
    '369a7b7109ed4bcbaf32639f3899dece',
    '5dc88460a5c7422ea3a858ad9dd55ec9',
    '63682d135b3b4553b2c548372df80154',
    '89a7eee8932a453a878f110f92a8e8b0',
    'be28f569ebd0489db13096866d5f5e07',
    '1ca46ea6d06f47ab91cf772582946815',
    '7b06e93d205a450a864c2f7675603f48',
    'af1edd48aa004d20a2b943b1b8bce61d',
    '5dc88460a5c7422ea3a858ad9dd55ec9',
    'edaf1136619f4378b10f69c9c900e0f7',
    'd3bc64650edf4f688c4fdbcf30db089a',
    '846ee5ee3cf1439982af0a173e4927a2',
    '5ad2d62048374a7ab4540d8cff460219',
    'd7e136b9cf6142778fc0e53997eda12d',
    'd75b8d39bf9447b5b240371a5a59c331',
    'f06d4793937546fc8c6c8098b5fe9060',
    '229f17650ca14d679a41e7cb198e4832',
]

lplayers = [
    '6ca68e69f319438e8344a97fc1fb7914',
    '6ff2629575f544a2aa96d62446d6901d', 
    '1a9ea24412cd4b74be414e322d56243b', 
    '647871f098e643368e1cff8ffe74a5f0', 
    '486914ec9da242f5aa2c540950ddb364', 
    'e6e81f757cc1439ea17d36e6dfdf2dcf', 
    'cb92169da50b4fa7a6041e553ebab03f', 
    'f191e1d6e32f4a6cb78c4ffefb096eb6', 
    'c79d473abaa443efa17998e1a7ca8a76',
    '1d8a510189ca4d1f89859e0f15690357', 
    'c044a47a52ba41b4ac5d6a91dafa3735', 
    '67b236dc3d154ce5b48fd98b85aa650b',
    '42d6304b519f4cd197cb71d4d6523e6c',
    '022005ddb80b430a91c8b673829761f4',
    '0afd9670998e4cf29a3265c9d9ced514',
    'fc2216c14ddc4dcdb81b1858aa12fd9f',
    '5aabc3fa32274cbc87873a50abb4f2ec',
    '3eea7dafebf941918d1b272f78b6dfb2',
    'b32110a5aacf4537a5f58a0ec33357e6',
    '5dc88460a5c7422ea3a858ad9dd55ec9',
    'e1c06e1b82dc4346b8f796c236233cbb',
    '1d5cf87211244a299a8ae1819610445e',
    '6dbbd744f8bb4a59b7837d8c29ac48e6',
    '42d6c7fb0ecd4208bf7bc663254df062',
]

def get_stats(playername):
    mojang_r = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{playername}")
    if mojang_r.status_code == 200:
        mojangjson = mojang_r.json()
        name = mojangjson["name"]
        uuid = mojangjson["id"]
    else:
        raise Error("Could not find that player")

    hypixel = requests.get(f"https://api.hypixel.net/player?key={HYPIXEL_TOKEN}&uuid={uuid}").json() 
    if not hypixel["success"]:
        raise Error("Hypixel didn't give any info")
    player = hypixel["player"]

    special = ""

    for x in range(len(wkplayers)):
        if(uuid == wkplayers[x]):
            special = "☆ Well-Known Player"
    for x in range(len(lplayers)):
        if(uuid == lplayers[x]):
            special = "♔ Leaderboard Player"

    try:
        kills = player["achievements"]["arcade_ctw_slayer"]
        caps = player["achievements"]["arcade_ctw_oh_sheep"]
        #first_login = int(str(player["firstLogin"])[:-3])

        achievement_ids = player["achievementsOneTime"]
        achievements = []
        for ach in achievement_ids:
            if "arcade_ctw" in ach:
                achievements.append(
                    ach_api[ach.split("arcade_")[1].upper()]
                )
        possible_achs = []
        for ach, a in ach_api.items():
            if "CTW_" in ach:
                possible_achs.append(a)

    except:
        raise Error("Player probably didn't play since Update 1.0 came out")
    return name, kills, caps, achievements, possible_achs, special, f"https://visage.surgeplay.com/bust/512/{uuid}", uuid

@bot.command()
async def stats(ctx, playername):
    m = await send_loading(ctx)
    try:
        name, kills, caps, achievements, possible_achs, special, url, uuid = get_stats(playername)
    except Error as e:
        await send_error(m, e)
        return

    embed = discord.Embed(
        title=f"{name}'s Stats",
        description= special + f"\n\nCaptures: **{caps:,}**\nKills/Assists: **{kills:,}**\nAchievements: **{len(achievements)}/{len(possible_achs)}**"
    )
    embed.set_thumbnail(url=url)
    embed.set_footer(text="CTW Stats by ccev and qej")
    await m.edit(embed=embed)
    bot_stats.add_statsquery(uuid, ctx.author.id)

@bot.command(aliases=["a", "ach"])
async def achievements(ctx, playername):
    m = await send_loading(ctx)
    try:
        name, kills, caps, achievements, possible_achs, url, uuid = get_stats(playername)
    except Error as e:
        await send_error(m, e)
        return

    embed = discord.Embed(
        title=f"{name}'s Achievements"
    )
    embed.set_thumbnail(url=url)
    for ach in possible_achs:
        if ach["name"] in [a["name"] for a in achievements]:
            emote = "✅ "
        else:
            emote = "❌ "
        embed.add_field(
            name=emote + ach["name"].replace("Capture the Wool: ", ""),
            value=ach["description"],
            inline=False
        )
        embed.set_footer(text="CTW Stats by ccev and qej")
    await m.edit(embed=embed)
    bot_stats.add_achievementsquery(uuid, ctx.author.id)

@bot.command()
async def credits(ctx):
    embed = discord.Embed(
        title="Credits",
        description="I was developed by <@!211562278800195584> with the help of <@314924973234061313>\n\n**[Invite me](https://discord.com/oauth2/authorize?client_id=750015447788683395&scope=bot)** | **[Fork me on GitHub](https://github.com/ccev/ctwstats)**"
    )
    await ctx.send(
        embed=embed,
        allowed_mentions=discord.AllowedMentions(users=False)
    )

@bot.command()
async def botstats(ctx):
    achs = bot_stats.sort_achievements()
    stats = bot_stats.sort_stats()

    embed = discord.Embed(title="Bot Stats")
    embed.add_field(
        name="Stats Lookups",
        value=stats
    )
    embed.add_field(
        name="Achievement Lookups",
        value=achs
    )
    await ctx.send(embed=embed)

"""@bot.event
async def on_message(message):
    if message.content.lower() == "dab":
        await message.channel.send("<:dab:750795517893541919>")"""

@bot.event
async def on_ready():
    print("Connected to Discord")

bot.run(DISCORD_TOKEN)