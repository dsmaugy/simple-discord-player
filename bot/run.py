from dotenv import load_dotenv
load_dotenv() # load all environment variables first for YouTube API key

from bot import MusicCog
from bot import AdminCommands
from discord.ext import commands
import os
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s-[%(levelname)s]-%(name)s: %(message)s", datefmt="%d-%b-%y %H:%M:%S")

    bot = commands.Bot(command_prefix="-")
    bot.add_cog(MusicCog(bot))
    bot.add_cog(AdminCommands(bot))
    bot.run(os.environ['DISCORD_TOKEN'])