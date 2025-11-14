from random import choice

import discord
from discord.ext import commands, tasks


class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()  # Start the loop when the cog loads

    async def cog_unload(self):
        self.change_status.cancel()  # Make sure the loop stops when the cog unloads

    @tasks.loop(seconds=60)
    async def change_status(self):
        await self.bot.change_presence(activity=discord.Game(choice(self.bot.config["status_list"])))

    @change_status.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()
