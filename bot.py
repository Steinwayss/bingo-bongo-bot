import json
import yt_dlp
import discord
from discord.ext import commands

from yt_funcs import YTQueue


class BingoBongoBot(commands.Bot):
    def __init__(self, config_path="Data/config.json", token_path="Data/token.json"):
        self.config = json.load(open(config_path, "r"))
        self.token = json.load(open(token_path, "r"))["token"]
        super().__init__(command_prefix=self.config["prefix"], intents=discord.Intents.all())
        
        self.queue = YTQueue()
        self.downloader = yt_dlp.YoutubeDL(self.config["yt_dlp_format_options"])
        
    async def setup_hook(self):
        from custom_commands import MusicCommands
        await self.add_cog(MusicCommands(self))
        from status_changer import StatusCog
        await self.add_cog(StatusCog(self))
        
    async def on_ready(self):
        print(f"Bot logged in as {self.user}")

    def start_bongos(self):
        self.run(self.token)

if __name__ == "__main__":
    bot = BingoBongoBot()
    bot.start_bongos()