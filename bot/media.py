import discord
import logging
import os

logger = logging.getLogger("mediactrl")


class BotAudioSource():
    def __init__(self, source_str: str, name: str, duration: str):
        self.name = name
        self.duration = duration
        self.source_str = source_str
        self.source: discord.PCMVolumeTransformer = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source_str))

    def __repr__(self) -> str:
        return self.name

class AudioContext():
    def __init__(self, voice_client: discord.VoiceClient=None):
        self._queue: list[BotAudioSource] = [] # list of AudioSources
        self._now_playing: BotAudioSource = None
        self._vc: discord.VoiceClient = voice_client

        self._stop_flag: bool = False
        self._repeat_flag: bool = False
        self._skip_flag: bool = False
        
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

        if self._repeat_flag and not self._stop_flag and not self._skip_flag:
            logger.info(f"Repeating {self._now_playing.name}")
            bas: BotAudioSource = BotAudioSource(self._now_playing.source_str, self._now_playing.name, self._now_playing.duration)
            self._queue.insert(0, bas)

        if self._now_playing.source_str.startswith("/tmp/"):
            os.remove(self._now_playing.source_str)

        self._now_playing = None

        if not self._stop_flag:
            self.play_from_queue()
        else:
            self._stop_flag = False
        self._skip_flag = False


    def play_from_queue(self):
        if len(self._queue) > 0 and self._vc and not self._vc.is_playing():
            self._now_playing = self._queue.pop(0)
            self._vc.play(self._now_playing.source, after=self.done_playing)

    def queue_song(self, source: str, name: str, duration: str):
        logger.info(f"Queueing {name} from {source}")
        self._queue.append(BotAudioSource(source, name, duration))

    def pause(self):
        if self._vc and self._vc.is_playing:
            self._vc.pause()

    def resume(self):
        if self._vc and self._vc.is_paused():
            self._vc.resume()
        
    def skip(self):
        self._skip_flag = True
        if self._vc.is_playing() or self._vc.is_paused():
            self._vc.stop()
        else:
            self.play_from_queue()


    def repeat_toggle(self):
        self._repeat_flag = not self._repeat_flag

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
