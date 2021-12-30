from bot import MusicCog
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.WARN)

    bot = commands.Bot(command_prefix="-")
    bot.add_cog(MusicCog(bot))
    bot.run(os.environ['DISCORD_TOKEN'])