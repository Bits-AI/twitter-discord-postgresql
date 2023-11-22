"""The startup cog for Discord Bot."""

import discord
from discord.ext import commands, tasks
import os
from utils import status_util
from utils.logging import logger

class Startup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.status = status_util.StatusUtil()

    @commands.Cog.listener()
    async def on_ready(self):
        """Function to run when the bot is connected to Discord server."""

        self.presence_handler.start()
        logger.info("Discord Bot is online.")

    @tasks.loop(seconds=30)
    async def presence_handler(self):
        """Function for handling the loops of the status."""

        status = self.status.get()
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=status))

def setup(bot):
    bot.add_cog(Startup(bot))
    