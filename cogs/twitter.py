"""The Twitter cog module for Discord Bot."""

import discord
from discord.ext import commands, tasks
import tweepy
import asyncio
from utils import twitter_util, config_util, permission_util, db_pool
from utils.logging import logger

class Twitter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        #Complete the authentication process during initialization
        #Tweepy requires 2 OAuth keys and 2 Tokens
        OAuth1, OAuth2, Token1, Token2 = twitter_util.get_twitter_credentials()

        #Setup the authentication object with the access token
        auth = tweepy.OAuthHandler(OAuth1, OAuth2)
        auth.set_access_token(Token1, Token2)

        #Set the api variable
        self.api = tweepy.API(auth)

        self.db_params = config_util.get_db_params()

        self.twitter_url = twitter_util.get_twitter_target()

        self.twitter_id = twitter_util.get_twitter_id()

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        """Event listener when the bot is ready."""

        #Start all workers
        self.worker_name.start()

    @commands.command()
    @permission_util.is_owner()
    async def stop_worker(self, ctx, worker: str = None):
        if worker is None:
            return await ctx.send("Please specify the name of the running worker!")

        try:
            logger.info(f"Attempting to stop the worker for {worker}.")
            if worker == "worker_name":
                self.worker_name.stop()
            else:
                return await ctx.send("No matching worker for the specified name.")
        except Exception as error:
            return await ctx.send(f"Error: {type(error).__name__}: {error}")
        finally:
            return await ctx.send(f"Successfully stopped worker {worker}.")

    @tasks.loop(seconds=60)
    async def worker_name(self):
        """Scheduled worker for monitoring tweets."""

        logger.info("Started scheduled worker for Twitter monitoring.")
        try:
            conn, pool = await db_pool.create_pool()

            msg = await twitter_util._tweet_handler(
                conn, self.twitter_id, self.api, self.twitter_url
            )

            if msg == "Failed":
                logger.info("Failed to retrieve Twitter data for the specified account.")
            
            elif msg is None:
                logger.info("The account has not posted any new tweet.")

            else:
                channel = discord.utils.get(self.bot.get_all_channels(), name="channel-name")
                await channel.send(msg)
                logger.info(msg)

        except Exception as error:
            logger.error(f"Error: {type(error).__name__}: {error}")

        finally:
            await pool.release(conn)
            await pool.close()

def setup(bot):
    bot.add_cog(Twitter(bot))
