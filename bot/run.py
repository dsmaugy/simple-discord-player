from bot import bot
import os
from dotenv import load_dotenv
import logging

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.WARN)
    bot.run(os.environ['DISCORD_TOKEN'])