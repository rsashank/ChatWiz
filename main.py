import discord
import asyncio
from discord.ext import commands
import json
import random
import openai

ListColours = [
    0xbed5e7, 
    0xb0cce1, 
    0x9ec4db, 
    0xffd1dc, 
    0xffb6c1, 
    0xf46fa8,
    0x9dc6ca,
    0xffea95,
    0xffa88c,
    0x77DD77,
    0x836953,
    0x89cff0,
    0x99c5c4,
    0x9adedb,
    0xaa9499,
    0xaaf0d1
]

def read_bot_token():
    with open("secrets.json") as f:
        data = json.load(f)
        return data["DISCORD_TOKEN"]

def read_openai_token():
    with open("secrets.json") as f:
        data = json.load(f)
        return data["OPENAI_TOKEN"]

openai.api_key= read_openai_token()

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
    servers = len(bot.guilds)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"in {servers} servers!"))

@bot.command()
async def help(ctx):
    embed1 = discord.Embed(title="Help", description="**General Commands (Page 1):**\n Press ▶️ to go to Music Commands.", color=random.choice(ListColours))
    embed1.add_field(name="!ping", value="```Returns Pong!```", inline=False)
    embed1.add_field(name="!say", value="```Echoes your message```", inline=False)
    embed1.add_field(name="!help", value="```Help Menu```", inline=False)
    embed1.add_field(name="!remindme", value="```Reminds you after a given time```", inline=False)
    embed1.add_field(name="!gptchannel", value="```Sets the GPT-3 chat channel```", inline=False)


    embed2 = discord.Embed(title="Help", description="**Music Commands (Page 2):**\n Press ◀️ to go to General Commands.", color=random.choice(ListColours))
    embed2.add_field(name="!play", value="```Plays a song```", inline=False)
    embed2.add_field(name="!skip", value="```Skips the current song```", inline=False)
    embed2.add_field(name="!pause", value="```Pauses the current song```", inline=False)
    embed2.add_field(name="!resume", value="```Resumes the current song```", inline=False)
    embed2.add_field(name="!queue", value="```Shows the queue```", inline=False)
    embed2.add_field(name="!stop", value="```Stops the music```", inline=False)
    embed2.add_field(name="!nowplaying", value="```Shows the current song```", inline=False)
    embed2.add_field(name="!disconnect", value="```Disconnects the bot```", inline=False)

    pages = [embed1, embed2]
    page_number = 0

    message = await ctx.send(embed=pages[page_number])

    await message.add_reaction('◀️')
    await message.add_reaction('▶️')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['◀️', '▶️']

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            break

        if str(reaction.emoji) == '▶️' and page_number != len(pages) - 1:
            page_number += 1
            await message.edit(embed=pages[page_number])
            await message.remove_reaction(reaction, user)

        elif str(reaction.emoji) == '◀️' and page_number > 0:
            page_number -= 1
            await message.edit(embed=pages[page_number])
            await message.remove_reaction(reaction, user)

        else:
            await message.remove_reaction(reaction, user)

@bot.command()
async def ping(ctx):
    embed=discord.Embed(title="Ping", description=f"🏓 Pong! {round(bot.latency * 1000)}ms", color=random.choice(ListColours))
    await ctx.reply(embed=embed)

@bot.command()
async def say(ctx, *, message=None):
    if not message:
        embed=discord.Embed(title="Say", description="Please provide a message after the command. \n**Usage:** ```!say [message]```", color=random.choice(ListColours))
        await ctx.reply(embed=embed)
        return

    embed=discord.Embed(title="Say", description=message, color=random.choice(ListColours))
    await ctx.reply(embed=embed)


@bot.command()
async def remindme(ctx, time=None, *, message=None):
    if not time or not message:
        embed=discord.Embed(title="Say", description="You must provide a time and a message. \n**Example:** ```!remindme 1d do laundry```", color=random.choice(ListColours))
        await ctx.reply(embed=embed)
        return
    seconds = 0
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
    embed=discord.Embed(title="Remind Me", description=f"Okay, I will remind you about **\"{message}\" in {counter}**.", color=random.choice(ListColours))
    await ctx.reply(embed=embed)
    await asyncio.sleep(seconds)
    embed=discord.Embed(title="Reminder", description=f"You asked me to remind you about **\"{message}\", {counter} ago**. ", color=random.choice(ListColours))
    await ctx.send(f"Hey {ctx.author.mention},", embed=embed)

gpt3_channel_id = None

@bot.command()
async def gptchannel(ctx, channel: discord.TextChannel):
    global gpt3_channel_id
    gpt3_channel_id = channel.id
    await ctx.reply(f"GPT-3 chat channel set to <#{channel.id}>.")

@bot.event
async def on_message(message):
    global gpt3_channel_id
    if gpt3_channel_id:
        if message.channel.id == int(gpt3_channel_id) and message.author != bot.user:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=message.content,
                temperature=0.33,
                max_tokens=50,
                presence_penalty=0,
                frequency_penalty=0,
                best_of=1,
            )

            bot_response = response.choices[0].text.strip()
            embed=discord.Embed(title="GPT-3 Chat (text-davinci-003 model)", description=bot_response, color=random.choice(ListColours))
            await message.channel.send(embed=embed)

    await bot.process_commands(message)
    

token = read_bot_token()
bot.run(token)