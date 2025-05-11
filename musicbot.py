import discord
from discord.ext import commands, tasks
import yt_dlp

import asyncio
import json
from random import choice
from yt_funcs import yt_queue, yt_search, dm_texts

# ******************* yt_dlp setup ********************
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop  or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
# ******************* youtube_dl setup ********************


config = json.load(open("Data/config.json", "r"))
bot_intents = discord.Intents.all() # This gives the bot permission to (at least read messages and join voice) everything.
client = commands.Bot(command_prefix=config["prefix"], intents=bot_intents)

status = ["Macht was immer ein Bingo Bongo Bot so macht!", "Reinigt den Maschinenraum", "Spielt den selben Song nochmal", "Ist der König der Bongos",
          "Spielt Bingo", "Hier könnte Ihre Werbung stehen"]
queue = yt_queue()

async def play_from_queue(ctx):
    # plays the first item in the queue.
    # check for empty queue BEFORE calling!
    global queue
    voice_channel = ctx.message.guild.voice_client

    song = queue.pop()

    # start the yt player
    async with ctx.typing():
        player = await YTDLSource.from_url(song["url"], loop=client.loop, stream=True)  # STREAM SET TRUE
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send(f'**Now playing:** {player.title}')

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')


@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):  # context
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)} ms')


@client.command(name='play', help='This command plays music')
async def play(ctx, *args):  # context
    if not await control_authorized(ctx):
        return

    global queue
    # if no url or searchterm is specified, use the first item in the queue instead
    if len(args) > 0:
        queue.add_search(args)
    elif queue.length() < 0:
        # -play was called but queue is empty. Message and abort.
        await ctx.send('No song specified and the queue is empty, please gimme more information!')
        return
    
    # if all went well, start playback
    await play_from_queue(ctx)



@client.command(name='pause', help='Pauses the playback. Can be resumed with "-resume"')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()


@client.command(name='resume', help='Resumes the playback after "-pause" has been called.')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()


@client.command(name='stop', help='Stops the playback. Not resumable with "-resume"')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

@client.command(name='skip', help='Skips currently playing song and plays next song in queue.')
async def skip(ctx):
    if not await control_authorized(ctx):
        return
    # stop playing
    ctx.message.guild.voice_client.stop()

    if queue.length() < 0:
        await ctx.send('Your queue is **empty**, stopping.')
    else:

        await play_from_queue(ctx)

# @client.command(name='queue', help='use -queue [song] to queue up a song; use -queue to print the queue.')
# async def queue_(ctx, url=''):
#     global queue

#     if url == '':
#         await view(ctx)
#         return

#     # queue.add_url(url)
#     queue.add_search(url)
#     await ctx.send(f'`{queue.get_titles(all=False, index=-1)}` added to queue!')
    
@client.command(name='queue', help='use -queue [song] to queue up a song; use -queue to print the queue.')
async def queue_(ctx, *args):
    global queue

    if len(args) <= 0:
        await view(ctx)
        return

    # queue.add_url(url)
    queue.add_search(args)
    await ctx.send(f'`{queue.get_titles(all=False, index=-1)}` added to queue!')


# @client.command(name='view', help='Displays the current queue. Alternative to using -queue')
async def view(ctx):
    global queue

    if queue.length() == 0:
        await ctx.send('Your queue is currently **empty!**')
    else:
        await ctx.send(f'Your queue is now:\n```{queue.get_titles(all=True)}```')


@client.command(name='remove', help='Removes the specified song from the queue. For example, "-remove 0" removes the first element in the queue.')
async def remove(ctx, index):
    index = int(index)
    global queue

    if queue.length() < 0:
        await ctx.send('Your queue is **empty**!')
        return
    elif queue.length() < index:
        await ctx.send('The index you specified is **out of range**')
        return

    queue.remove_song(index)
    await view(ctx)


@client.command(name='leave', help='This command stops the music and makes the bot leave the channel')
async def leave(ctx):  # context
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@client.command(name='dm', help='surprise :)')
async def dm(ctx):
    await ctx.author.send(choice(dm_texts))


@tasks.loop(seconds=60)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

async def control_authorized(ctx):
    # join voice channel if possible
    # if bot is not in voice but author is: join that channel
    if not ctx.me.voice and ctx.message.author.voice:
        await ctx.message.author.voice.channel.connect()
        # bot allowed to continue
        return True
    # if author is not in voice: refuse to do anything
    elif not ctx.message.author.voice:
        await ctx.send('You are not connected to a voice channel')
        # bot not allowed to continue
        return False
    # bot allowed to continue
    return True

client.run(config["token"])
