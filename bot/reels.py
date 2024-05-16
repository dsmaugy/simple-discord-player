
from typing import TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from threading import Timer

from discord.mentions import AllowedMentions

import asyncio
import random
import logging

logger = logging.getLogger("reels")


if TYPE_CHECKING:
    from discord.abc import MessageableChannel
    from typing import Dict

MEAN_LOW = 3600 * 24 * 1 # daily limit
MEAN_HIGH = 3600 * 24 * 7 # weekly high limit
DEFAULT_MEAN = 3600 * 24 * 5
DEFAULT_STD = 3600 * 24 # one day standard deviation

class ReelsManager:
    
    def __init__(self):
        self.reels_list: Dict[str, Reels] = {}

    def add_channel(self, reels_id: str, channel: 'MessageableChannel') -> bool:
        if reels_id not in self.reels_list:
            entry = Reels(channel)
            self.reels_list[reels_id] = entry
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
    
    def set_reel_timeout_mean(self, reels_id: str, new_mean: int) -> bool:
        if new_mean >= MEAN_LOW and new_mean <= MEAN_HIGH:
            self.reels_list[reels_id].timeout_mean = new_mean
            return True
        return False
    
    def set_reel_timeout_std(self, reels_id: str, new_std: int) -> bool:
        self.reels_list[reels_id].timeout_std = new_std
        return True
    
    def send_reel(self, reels_id: str, loop):
        reel: Reels = self.reels_list[reels_id]
        mention_all = AllowedMentions.all()
        
        logger.info("Sending reel update")
        asyncio.run_coroutine_threadsafe(reel.channel.send("@everyone REEL UPDATES", allowed_mentions=mention_all), loop)
        self._trigger_send_timer(reels_id, loop)

    def _trigger_send_timer(self, reels_id: str, loop=None):
        reel: Reels = self.reels_list[reels_id]
        new_timeout = random.gauss(reel.timeout_mean, reel.timeout_std)

        reel.last_reel = datetime.now()
        logger.info(f"Next reel for {reels_id} is at {reel.last_reel + timedelta(seconds=new_timeout)}")
        loop = asyncio.get_event_loop() if loop is None else loop
        Timer(new_timeout, self.send_reel, kwargs={'reels_id': reels_id, 'loop': loop}).start()

        

@dataclass
class Reels:
    channel: 'MessageableChannel'
    timeout_mean: int = DEFAULT_MEAN
    timeout_std: int = DEFAULT_STD
    last_reel: datetime = None