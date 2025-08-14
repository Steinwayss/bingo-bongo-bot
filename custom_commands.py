import discord
from discord.ext import commands
from discord.ext.commands import command
from discord.ext.commands.context import Context
from bot import BingoBongoBot
from yt_dlp_source import YTDLSource


class MusicCommands(commands.Cog):
    def __init__(self, bot: BingoBongoBot):
        self.bot = bot

    @command(name="ping", help="Returns latency")
    async def ping(self, ctx: Context):
        await ctx.send(f"**Pong!** Latency: {round(self.bot.latency * 1000)} ms")

    @command(name="play", help="Plays music from the queue, URL or search terms")
    async def play(self, ctx: Context, *, query: str):
        if not await self.join_authors_channel(ctx):
            return
        
        if (vc := self.get_voice_client(ctx)) is not None:
        
            async with ctx.typing():
                player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
                vc.play(player, after=lambda e: print(f"Player error: {e}") if e else None)
            await ctx.send(f"Now playing: {player.title}")
        
        

    @command(
        name="queue",
        help="Puts a song into the queue. Can use URL or search words. Without arguments prints the current queue",
    )
    async def queue(self, ctx: Context):
        #TODO
        pass

    @command(name="skip", help="Immediately start playback of the next item in the queue")
    async def skip(self, ctx: Context):
        #TODO
        pass

    @command(
        name="remove",
        help="Removes the n-th entry from the queue, 0 being the first. Without arguments, remove the first entry",
    )
    async def remove(self, ctx: Context, index):
        index = int(index)
        if self.bot.queue.length() < 1:
            await ctx.send("Your queue is **empty**!")
            return
        elif self.bot.queue.length() < index:
            await ctx.send(
                f"The queue is {self.bot.queue.length()} entries long, but you want to remove number {index}. Remember that 0 is the first."
            )
            return

        self.bot.queue.remove_song(index)
        await self.print_queue(ctx)

    @command(name="pause", help="Pauses music playbay. Can be resumed with the resume command")
    async def pause(self, ctx: Context):
        if (vc := self.get_voice_client(ctx)) is not None:
            vc.pause()

    @command(name="resume", help="Resumes playback of music paused by the pause command")
    async def resume(self, ctx: Context):
        if (vc := self.get_voice_client(ctx)) is not None:
            vc.resume()

    @command(name="stop", help="Stops music. Cannot be resumed")
    async def stop(self, ctx: Context):
        if (vc := self.get_voice_client(ctx)) is not None:
            vc.stop()

    @command(name="join", help="Joins your voice channel")
    async def join(self, ctx: Context):
        await self.join_authors_channel(ctx)

    @command(name="leave", help="leaves the current voice channel")
    async def leave(self, ctx: Context):
        if ctx.guild is not None and isinstance(voice_client := ctx.guild.voice_client, discord.VoiceClient):
            await voice_client.disconnect()

    def get_voice_client(self, ctx: Context) -> discord.VoiceClient | None:
        if ctx.guild is not None and isinstance(voice_client := ctx.guild.voice_client, discord.VoiceClient):
            return voice_client
        else:
            return None

    async def print_queue(self, ctx: Context):
        if self.bot.queue.length() < 1:
            await ctx.send("Your queue is currently **empty**!")
        else:
            await ctx.send(f"Your queue is now:\n```{self.bot.queue.get_titles(all=True)}```")

    async def join_authors_channel(self, ctx: Context) -> bool:
        if isinstance(author := ctx.message.author, discord.Member) and author.voice is not None:
            if author.voice.channel is not None:
                await author.voice.channel.connect()
                return True
            else:
                await ctx.send("Plase join a voice channel")
                return False
        else:
            # Author is User and not Member, meaning the message was not received on a server. Ignore. OR
            # Author has no voice information available, so the bot cannot join the channel
            return False
