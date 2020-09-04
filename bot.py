import discord
import requests
import json

from discord.ext import commands
from datetime import datetime

with open("tokens.json", "r") as f:
    tokens = json.load(f)

DISCORD_TOKEN = tokens["discord_token"]
HYPIXEL_TOKEN = tokens["hypixel_token"]

bot = commands.Bot(command_prefix="/", case_insensitive=1)
ach_api = requests.get(f"https://api.hypixel.net/resources/achievements?key={HYPIXEL_TOKEN}&uuid=229f1765-0ca1-4d67-9a41-e7cb198e4832").json()["achievements"]["arcade"]["one_time"]

class Error(Exception):
    pass

async def send_error(ctx, error):
    embed = discord.Embed(description=f"❌ {error}", color=16073282)
    await ctx.send(embed=embed)

async def send_loading(ctx):
    embed = discord.Embed()
    embed.set_footer(text="Loading...", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    m = await ctx.send(embed=embed)
    return m

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
    return name, kills, caps, achievements, possible_achs, f"https://visage.surgeplay.com/bust/512/{uuid}"

@bot.command()
async def stats(ctx, playername):
    m = await send_loading(ctx)
    try:
        name, kills, caps, achievements, possible_achs, url = get_stats(playername)
    except Error as e:
        await send_error(ctx, e)
        return

    embed = discord.Embed(
        title=f"{name}'s Stats",
        description=f"Captures: **{caps:,}**\nKills/Assists: **{kills:,}**\nAchievements: **{len(achievements)}/{len(possible_achs)}**"
    )
    embed.set_thumbnail(url=url)
    await m.edit(embed=embed)

@bot.command(aliases=["a", "ach"])
async def achievements(ctx, playername):
    m = await send_loading(ctx)
    try:
        name, kills, caps, achievements, possible_achs, url = get_stats(playername)
    except Error as e:
        await send_error(ctx, e)
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
    await m.edit(embed=embed)

"""@bot.event
async def on_message(message):
    if message.content.lower() == "dab":
        await message.channel.send("<:dab:750795517893541919>")"""

@bot.event
async def on_ready():
    print("Connected to Discord")

bot.run(DISCORD_TOKEN)