import discord
from discord.ext import commands
import logging

logger = logging.getLogger("mediactrl")


class BotAudioSource():
    def __init__(self, source: discord.PCMVolumeTransformer, name: str, duration: str):
        self.source = source
        self.name = name
        self.duration = duration

    def __repr__(self) -> str:
        return self.name

class AudioContext():
    def __init__(self, voice_client: discord.VoiceClient=None):
        self._queue: list[BotAudioSource] = [] # list of AudioSources
        self._now_playing: BotAudioSource = None
        self._vc: discord.VoiceClient = voice_client

        self._stop_flag: bool = False
        
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
        logger.info(f"Done playing {self._now_playing.name}")
        if e:
            logger.error(f"Player error: {e}")

        self._now_playing = None

        if not self._stop_flag:
            self.play_from_queue()
        else:
            self._stop_flag = False


    def play_from_queue(self):
        if len(self._queue) > 0 and self._vc and not self._vc.is_playing():
            self._now_playing = self._queue.pop(0)
            self._vc.play(self._now_playing.source, after=self.done_playing)

    def queue_song(self, source: str, name: str, duration: str):
        self._queue.append(BotAudioSource(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source), volume=0.5), name, duration))

    def pause(self):
        if self._vc and self._vc.is_playing:
            self._vc.pause()

    def resume(self):
        if self._vc and self._vc.is_paused():
            self._vc.resume()
        
    def skip(self):
        if self._vc.is_playing() or self._vc.is_paused():
            self._vc.stop()
        else:
            self.play_from_queue()

    def stop(self):
        self._stop_flag = True
        self._vc.stop()

    def get_queue(self) -> list:
        return self._queue

    def get_now_playing(self) -> BotAudioSource:
        return self._now_playing

class AudioContextManager():
    def __init__(self):
        self._ctxs = {}
    
    def is_ctx_present(self, guild_id: int) -> bool:
        return guild_id in self._ctxs
    
    def get_audio_ctx(self, guild_id: int) -> AudioContext:
        if self.is_ctx_present(guild_id):
            return self._ctxs[guild_id]
        
        ctx = AudioContext()
        self._ctxs[guild_id] = ctx
        return ctx
