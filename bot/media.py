import discord
from discord.ext import commands
import logging

logger = logging.getLogger("mediactrl")

class AudioContextManager():
    def __init__(self):
        self._ctxs = {}
    
    def is_ctx_present(self, guild_id: int):
        return guild_id in self._ctxs
    
    def get_audio_ctx(self, guild_id: int):
        if self.is_ctx_present(guild_id):
            return self._ctxs[guild_id]
        
        ctx = AudioContext()
        self._ctxs[guild_id] = ctx
        return ctx

class BotAudioSource():
    def __init__(self, source: discord.AudioSource, name: str):
        self.source = source
        self.name = name

class AudioContext():
    def __init__(self, voice_client: discord.VoiceClient=None):
        self._queue = [] # list of AudioSources
        self._now_playing = None
        self._vc = voice_client
        
    async def join_channel(self, channel: discord.VoiceChannel):
        if not self._vc or not self._vc.is_connected():
            self._vc = await channel.connect()
        else:
            await self._vc.move_to(channel)

    async def disconnect_channel(self):
        if self._vc and self._vc.is_connected():
            self._vc.cleanup()
            await self._vc.disconnect()

    def done_playing(self, e):
        logger.warn(f"Done playing {self._queue[0].name}")
        self._queue.pop(0)
        if e:
            logger.error(f"Player error: {e}")

        self.play_from_queue()

    def play_from_queue(self):
        if len(self._queue) > 0 and self._vc and not self._vc.is_playing():
            self._vc.play(self._queue[0].source, after=self.done_playing)

    def queue_song(self, source: discord.AudioSource, name: str):
        self._queue.append(BotAudioSource(source, name))

    def pause(self):
        if self._vc and self._vc.is_playing:
            self._vc.pause()

    def resume(self):
        if self._vc and self._vc.is_paused():
            self._vc.resume()

    def get_queue(self):
        return self._queue
        
    def skip(self):
        self._vc.stop()
