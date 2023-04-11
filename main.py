import discord
import asyncio
from discord.ext import commands
import json

def read_bot_token():
    with open("secrets.json") as f:
        data = json.load(f)
        print(f"data from json: {data}")
        return data["DISCORD_TOKEN"]

bot=commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all(),
    help_command=None
)

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user}')

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="Help", description="List of Commands:", color=0x7289da)
    embed.add_field(name="!ping", value="Returns Pong!", inline=False)
    embed.add_field(name="!say", value="Echoes your message", inline=False)
    embed.add_field(name="!help", value="Help Menu", inline=False)
    embed.add_field(name="!remindme", value="Reminds you after a given time", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    embed=discord.Embed(title="Ping Command", description=f"Pong! {round(bot.latency * 1000)}ms", color=0x7289da)
    await ctx.reply(embed=embed)

@bot.command()
async def say(ctx, *, message):
    embed=discord.Embed(title="Say Command", description=message, color=0x7289da)
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
    embed=discord.Embed(title="Remindme Command", description=f"Okay, I will remind you about \"{message}\" in {counter}.", color=0x7289da)
    await ctx.reply(embed=embed)
    await asyncio.sleep(seconds)
    embed=discord.Embed(description=f"You asked me to remind you about \"{message}\", {counter} ago. ", color=0x7289da)
    await ctx.send(f"Hey {ctx.author.mention},", embed=embed)

token = read_bot_token()
bot.run(token)