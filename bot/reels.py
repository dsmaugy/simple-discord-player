
from typing import TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Timer

from discord.mentions import AllowedMentions

import asyncio
import random
import logging

logger = logging.getLogger("reels")


if TYPE_CHECKING:
    from discord.abc import MessageableChannel
    from typing import Dict

MEAN_LOW = 1 # daily limit
MEAN_HIGH = 7 # weekly high limit
DEFAULT_MEAN = 5
DEFAULT_STD = 1 # one day standard deviation

HOUR_MEAN = 17 # 5pm mu
HOUR_STD = 2 # 2 hour standard deviation

EASTERN_TIME = timezone(timedelta(hours=-4))

class ReelsManager:
    
    def __init__(self):
        self.reels_list: Dict[str, Reels] = {}

    def add_channel(self, reels_id: str, channel: 'MessageableChannel') -> bool:
        if reels_id not in self.reels_list:
            entry = Reels(channel)
            self.reels_list[reels_id] = entry
            logger.info(f"Registering {reels_id} to reels manager")
            self._trigger_send_timer(reels_id)
            return True
        return False

    def remove_channel(self, reels_id: str) -> bool:
        if reels_id in self.reels_list:
            self.reels_list.pop(reels_id)    
            return True
        return False
    
    def reels_is_enabled(self, reels_id: str) -> bool:
        return reels_id in self.reels_list
    
    def get_status_str(self, reels_id: str) -> str:
        if reels_id in self.reels_list:
            return (
                f"Status: {'enabled' if self.reels_is_enabled(reels_id) else 'disabled'}, timeout mean={self.reels_list[reels_id].timeout_mean}, "
                f"timeout std={self.reels_list[reels_id].timeout_std}, "
                f"last reel={self.reels_list[reels_id].last_reel}"   
            )
        else:
            return "Channel reels not configured"
    
    def set_reel_timeout_mean(self, reels_id: str, new_mean: float) -> bool:
        if new_mean >= MEAN_LOW and new_mean <= MEAN_HIGH:
            self.reels_list[reels_id].timeout_mean = new_mean
            return True
        return False
    
    def set_reel_timeout_std(self, reels_id: str, new_std: float) -> bool:
        self.reels_list[reels_id].timeout_std = new_std
        return True
    
    def send_reel(self, reels_id: str, loop):
        reel: Reels = self.reels_list[reels_id]
        mention_all = AllowedMentions.all()

        logger.info("Sending reel update")
        asyncio.run_coroutine_threadsafe(reel.channel.send(f":warning:{reel.channel.name} time:warning:\nSend a pic and/or message of what you're up to!!!\n@everyone", allowed_mentions=mention_all), loop)
        self._trigger_send_timer(reels_id, loop)

    def force_send(self, reels_id: str):
        self._trigger_send_timer(reels_id, now=True)

    def _trigger_send_timer(self, reels_id: str, loop=None, now=False):
        reel: Reels = self.reels_list[reels_id]
        current_dt = datetime.now(EASTERN_TIME)
        if now:
            new_timeout = 0
        else:
            next_day = random.gauss(reel.timeout_mean, reel.timeout_std)
            hour = int(random.gauss(HOUR_MEAN, HOUR_STD))
            minute = random.randint(0, 59)
            trigger_date = (current_dt + timedelta(days=next_day)).replace(hour=hour, minute=minute)
            new_timeout = (trigger_date - current_dt).total_seconds()

        reel.last_reel = current_dt
        logger.info(f"Next reel for {reels_id} is at {reel.last_reel + timedelta(seconds=new_timeout)}")
        loop = asyncio.get_event_loop() if loop is None else loop
        t = Timer(new_timeout, self.send_reel, kwargs={'reels_id': reels_id, 'loop': loop})
        t.setDaemon(True)
        t.start()

        

@dataclass
class Reels:
    channel: 'MessageableChannel'
    timeout_mean: int = DEFAULT_MEAN
    timeout_std: int = DEFAULT_STD
    last_reel: datetime = None