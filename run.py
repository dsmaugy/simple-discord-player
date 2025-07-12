import asyncio
import logging
import os
from enum import auto

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

from bot.bot import AdminCommands, MusicCog
from bot.mediadownload import SCManager, YTManager
from bot.reels import ReelsManager

REQUIRED_ENV_VARS = ["DISCORD_TOKEN", "YOUTUBE_API"]


async def start():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s-[%(levelname)s]-%(name)s: %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    load_dotenv()
    for required_var in REQUIRED_ENV_VARS:
        if required_var not in os.environ:
            raise RuntimeError(f"Missing required var: {required_var}")

    intent = Intents.default()
    intent.message_content = True

    bot = commands.Bot(command_prefix="-", intents=intent)
    await bot.login(os.getenv("DISCORD_TOKEN"))

    yt_manager = YTManager(os.getenv("YOUTUBE_API"))
    sc_manager = SCManager()

    # set up initial reel
    reels = ReelsManager()
    initial_reels_channel = os.getenv("INITIAL_REELS")
    if initial_reels_channel:
        channel = await bot.fetch_channel(int(initial_reels_channel))
        reels.add_channel(initial_reels_channel, channel)

    await bot.add_cog(MusicCog(bot, yt_manager, sc_manager))
    await bot.add_cog(AdminCommands(bot, reels))

    await bot.connect()


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("Exited bot")
