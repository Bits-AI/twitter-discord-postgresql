import discord
from discord.ext import commands
import signal
from utils import config_util
from utils.logging import logger
import os

#Get all prefix defined in default and cogs
def get_prefixes(bot, message):
    cog_prefixes = (cog.prefix for cog in bot.cogs.values() if hasattr(cog, 'prefix'))
    prefix_list = config_util.get_prefix(*cog_prefixes)
    return prefix_list

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = get_prefixes, intents = intents)

initial_extensions = [
    'cogs.startup',
    'cogs.twitter',
]

#This class is made for heroku force shut down
class GracefulExit:

    def __init__(self, bot):
        self.bot = bot
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signu, frame):
        print("Exiting...")
        exit(0)

if __name__ == "__main__":
    try:
        grace = GracefulExit(bot)

        token = config_util.get_config()

        for extension in initial_extensions:
            try:
                bot.load_extension(extension)

            except Exception as error:
                logger.error(f"Failed to load extension {extension}\n{type(error).__name__}: {error}")

        bot.run(token)

    except KeyboardInterrupt as error:
        logger.error("Keyboard Interruption detected!")
        try:
            exit(1)

        except SystemExit:
            os._exit(0)
