from dotenv import load_dotenv
load_dotenv() # load all environment variables first for YouTube API key

from bot import MusicCog
from bot import AdminCommands
from discord.ext import commands
from discord import Intents
import os
import logging
import asyncio

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s-[%(levelname)s]-%(name)s: %(message)s", datefmt="%d-%b-%y %H:%M:%S")
    intent = Intents.default()
    intent.message_content = True

    bot = commands.Bot(command_prefix="-", intents=intent)
    asyncio.run(bot.add_cog(MusicCog(bot)))
    asyncio.run(bot.add_cog(AdminCommands(bot)))
    bot.run(os.environ['DISCORD_TOKEN'])