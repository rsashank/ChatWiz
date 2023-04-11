import json
import re
import random
import discord
import lavalink
import asyncio
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')

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

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.lavalink = lavalink.Client(self.bot.user.id)
        self.bot.lavalink.add_node("localhost", 2333, "youshallnotpass", region = "us")
        self.name = "Music commands"

    @commands.Cog.listener()
    async def on_socket_raw_receive(self, data):
        d = json.loads(data)
        await self.bot.lavalink.voice_update_handler(d)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def ensure_voice(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id)
        should_connect = ctx.command.name in ('play', "connect",)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError('Join a voicechannel first.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected. Please use `!connect` to connect.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        ch = after.channel
        if not ch:
            return
        if self.bot.user in ch.members:
            if len(ch.members) < 2:
                player = self.bot.lavalink.player_manager.get(member.guild.id)
                channel = self.bot.get_channel(player.fetch('channel'))
                if not player.paused:
                    await player.set_pause(True)
                    await channel.send("Paused the music as I was left alone.")

    @commands.command()
    async def connect(self, ctx):
        await ctx.message.reply("Connected!")

    @commands.command(name = "play")
    async def _play(self, ctx, *, query: str):
        """ Searches and plays a song from a given query. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        embed = discord.Embed(color=random.choice(ListColours))

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track Enqueued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()
            
    @commands.command(aliases=['dc', 'leave'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.message.reply('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.message.reply('You\'re not in my voicechannel!')

        player.queue.clear()
        await player.stop()
        await player.set_pause(False)
        await player.set_volume(100)
        player.set_loop(0)
        await ctx.guild.change_voice_state(channel=None)
        await ctx.message.reply('Disconnected.')


    @commands.command(aliases = ['np'])
    async def nowplaying(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.message.reply('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.message.reply('You\'re not in my voicechannel!')

        embed = discord.Embed(title = 'Now Playing', colour = random.choice(ListColours))
        embed.add_field(name = f"{player.current.title}", value = f"Requested by: {ctx.guild.get_member(player.current.requester).name}", inline = False)

        await ctx.send(embed = embed)

    @commands.command()
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.message.reply('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.message.reply('You\'re not in my voicechannel!')

        await player.set_pause(True)
        await ctx.message.reply("Paused!")

    @commands.command()
    async def resume(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.message.reply('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.message.reply('You\'re not in my voicechannel!')

        await player.set_pause(False)
        await ctx.message.reply("Resumed!")

    @commands.group(invoke_without_command = True, aliases = ["q"])
    async def queue(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.message.reply('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.message.reply('You\'re not in my voicechannel!')

        q = player.queue
        embed = discord.Embed(title = 'Tracks', colour = random.choice(ListColours))
        embed.add_field(name = f"Current - {player.current.title}", value = f"Requested by: {ctx.guild.get_member(player.current.requester).name}", inline = False)
        i = 1
        if q:
            for track in q:
                embed.add_field(name = str(i) + ".) " + str(track.title), value = f"Requested by: {ctx.guild.get_member(track.requester).name}", inline = False)
                i += 1

        await ctx.send(embed = embed)


    @commands.command()
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.message.reply('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.message.reply('You\'re not in my voicechannel!')

        await player.skip()
        await ctx.message.reply("Skipped the song!")


async def setup(bot):
    await bot.add_cog(Music(bot))