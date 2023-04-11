import discord
import asyncio
from discord.ext import commands
import json
import asyncio
import random

ListColours = [
    0xbed5e7, 
    0xb0cce1, 
    0x9ec4db, 
    0xffd1dc, 
    0xffb6c1, 
    0xf46fa8,
    0x9dc6ca,
    0xffea95,
    0xffa88c
]

def read_bot_token():
    with open("secrets.json") as f:
        data = json.load(f)
        return data["DISCORD_TOKEN"]

bot=commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all(),
    help_command=None,
    enable_debug_events = True
) 

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user}')
    await bot.load_extension("music")

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="Help", description="List of Commands:", color=random.choice(ListColours))
    embed.add_field(name="!ping", value="Returns Pong!", inline=False)
    embed.add_field(name="!say", value="Echoes your message", inline=False)
    embed.add_field(name="!help", value="Help Menu", inline=False)
    embed.add_field(name="!remindme", value="Reminds you after a given time", inline=False)
    embed.add_field(name="!play", value="Plays a song", inline=False)
    embed.add_field(name="!skip", value="Skips the current song", inline=False)
    embed.add_field(name="!pause", value="Pauses the current song", inline=False)
    embed.add_field(name="!resume", value="Resumes the current song", inline=False)
    embed.add_field(name="!queue", value="Shows the queue", inline=False)
    embed.add_field(name="!stop", value="Stops the music", inline=False)
    embed.add_field(name="!nowplaying", value="Shows the current song", inline=False)
    embed.add_field(name="!disconnect", value="Disconnects the bot", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    embed=discord.Embed(title="Ping Command", description=f"🏓 Pong! {round(bot.latency * 1000)}ms", color=random.choice(ListColours))
    await ctx.reply(embed=embed)

@bot.command()
async def say(ctx, *, message):
    embed=discord.Embed(title="Say Command", description=message, color=random.choice(ListColours))
    await ctx.reply(embed=embed)

@bot.command()
async def remindme(ctx, time, *, message: str):
    seconds=0
    if time.lower().endswith("d"):
        seconds += int(time[:-1]) * 60 * 60 * 24
        counter = f"{seconds // 60 // 60 // 24} days"
    if time.lower().endswith("h"):
        seconds += int(time[:-1]) * 60 * 60
        counter = f"{seconds // 60 // 60} hours"
    elif time.lower().endswith("m"):
        seconds += int(time[:-1]) * 60
        counter = f"{seconds // 60} minutes"
    elif time.lower().endswith("s"):
        seconds += int(time[:-1])
        counter = f"{seconds} seconds"
    embed=discord.Embed(title="Remindme Command", description=f"Okay, I will remind you about \"{message}\" in {counter}.", color=random.choice(ListColours))
    await ctx.reply(embed=embed)
    await asyncio.sleep(seconds)
    embed=discord.Embed(description=f"You asked me to remind you about \"{message}\", {counter} ago. ", color=random.choice(ListColours))
    await ctx.send(f"Hey {ctx.author.mention},", embed=embed)

token = read_bot_token()
bot.run(token)