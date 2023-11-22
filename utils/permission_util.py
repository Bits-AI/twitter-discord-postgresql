"""This module is for handling permission checks."""

from discord.ext import commands
import discord.utils

def check_is_owner(message):
    """Returns the Discord ID for the Bot owner."""

    return message.author_id == 00000000

def is_owner():
    """Function to check if the sender is the owner."""

    return commands.check(lambda ctx: check_is_owner(ctx.message))
