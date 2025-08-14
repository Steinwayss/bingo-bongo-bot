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
        #TODO: handle different expected functionality of !play in different contexts.
        # Refer to the documentation image
        if not await self.join_authors_channel(ctx):
            return

        if (vc := self.get_voice_client(ctx)) is not None:
            async with ctx.typing():
                player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
                vc.play(player, after=lambda e: print(f"Player error: {e}") if e else print("After!"))
            await ctx.send(f"Now playing: {player.title}")

    @command(
        name="queue",
        help="Puts a song into the queue. Can use URL or search words. Without arguments prints the current queue",
    )
    async def queue(self, ctx: Context, *, query: str):
        async with ctx.typing():
            player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
            self.bot.queue.add_song(player)
        await ctx.send(f"Added {player.title} to the queue.")

    @command(name="skip", help="Immediately start playback of the next item in the queue")
    async def skip(self, ctx: Context):
        if (voice_client := self.get_voice_client(ctx)) is not None:
            voice_client.stop()
            if not self.bot.queue.is_empty():
                await self.start_player(ctx, self.bot.queue.pop())
            else:
                await ctx.send("Skipped current song, but the queue is empty.")

    @command(
        name="remove",
        help="Removes a song from the queue. Use index or keyword(s).",
    )
    async def remove(self, ctx: Context, *, query: str):
        if self.bot.queue.is_empty():
            await ctx.send("Your queue is **empty**!")
            return
        args = query.split(" ")
        if len(args) < 2 and args[0].isdigit():
            index = int(args[0])
            if index > -1 and index < self.bot.queue.length():
                self.bot.queue.remove_song_index(index)
                await self.print_queue(ctx)
        else:
            self.bot.queue.remove_song_keyword(args)
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
        if (vc := self.get_voice_client(ctx)) is not None:
            await vc.disconnect()
            
    async def start_player(self, ctx: Context, player: YTDLSource, afterfunc=None):
        """Starts playing the provided player in the current voice channel.
        If the current voice channel is None, do nothing."""
        if (vc := self.get_voice_client(ctx)) is not None:
            async with ctx.typing():
                vc.play(player, after=lambda e: print(f"Player error: {e}") if e else afterfunc)
            await ctx.send(f"**Now playing:** {player.title}")

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
        if (
            isinstance(author := ctx.message.author, discord.Member)
            and author.voice is not None
            and (author_voice_channel := author.voice.channel) is not None
        ):
            bot_voice_client = self.get_voice_client(ctx)
            bot_voice_channel = None if bot_voice_client is None else bot_voice_client.channel
            if author_voice_channel is not bot_voice_channel:
                if bot_voice_client is None:
                    await author_voice_channel.connect()
                else:
                    # idk why, but using move_to throws a small error (but works).
                    # If there are no practical differences,
                    # I'll use disconnect() and connect() to avoid error messages
                    # await bot_voice_client.move_to(author_voice_channel)
                    await bot_voice_client.disconnect()
                    await author_voice_channel.connect()
            return True
        else:
            # Author is User and not Member, meaning the message was not received on a server. OR
            # Author has no voice information available, so the bot cannot join the channel
            await ctx.send("Plase join a voice channel")
            return False
