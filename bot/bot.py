from discord.ext import commands
from media import AudioContextManager
from mediadownload import YTManager
import discord
import logging

logger = logging.getLogger("bot")
DELETE_TIME = 30 # number of seconds to delete a message after sending

class MusicCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self._audio_manager: AudioContextManager = AudioContextManager()

    async def join_user_channel(self, ctx: commands.Context):
        vc = ctx.author.voice.channel
        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)
        if vc:
            await audio_ctx.join_channel(vc)
        else:
            await ctx.send("User not in voice channel!", delete_after=DELETE_TIME)

    @commands.command(aliases=["j"])
    async def join(self, ctx: commands.Context):
        await self.join_user_channel(ctx)

    @commands.command(aliases=["dc"])
    async def disconnect(self, ctx: commands.Context):
        await self._audio_manager.get_audio_ctx(ctx.guild.id).disconnect_channel()

    @commands.command()
    async def pause(self, ctx: commands.Context):
        self._audio_manager.get_audio_ctx(ctx.guild.id).pause()

    @commands.command(aliases=["r"])
    async def resume(self, ctx: commands.Context):
        self._audio_manager.get_audio_ctx(ctx.guild.id).resume()

    @commands.command()
    async def stop(self, ctx: commands.Context):
        self._audio_manager.get_audio_ctx(ctx.guild.id).stop()

    @commands.command(aliases=["q"])
    async def queue(self, ctx: commands.Context):
        queue = self._audio_manager.get_audio_ctx(ctx.guild.id).get_queue()
        output = ""
        for i in range(0, len(queue)):
            output += f"{i+1}. {queue[i].name} [{queue[i].duration}]\n"

        if len(queue) == 0:
            await ctx.send("Queue empty", delete_after=DELETE_TIME)
        else:
            await ctx.send(output, delete_after=DELETE_TIME)

    @commands.command(aliases=["np"])
    async def now_playing(self, ctx: commands.Context):
        np = self._audio_manager.get_audio_ctx(ctx.guild.id).get_now_playing()
        
        if np:
            await ctx.send(f"{np.name} [{np.duration}]", delete_after=DELETE_TIME)
        else:
            await ctx.send("Nothing playing right now", delete_after=DELETE_TIME)

    @commands.command(aliases=["s"])
    async def skip(self, ctx: commands.Context):
        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)

        np = audio_ctx.get_now_playing()
        audio_ctx.skip()
        
        if np:
            await ctx.send(f"Skipped {np.name}", delete_after=DELETE_TIME)


    @commands.command()
    async def status(self, ctx: commands.Context):
        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)
        await ctx.send(f"Is Playing: {audio_ctx._vc.is_playing()}. Is Paused: {audio_ctx._vc.is_paused()}", delete_after=DELETE_TIME)

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *args: (str)):
        await self.join_user_channel(ctx)
        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)
        np = audio_ctx.get_now_playing()
        media_name: str

        if len(args) == 1 and args[0].startswith("https://www.youtube.com/watch"):
            # stream this direct link
            data = await YTManager.from_url(args[0], loop=self.bot.loop)
            audio_ctx.queue_song(data[0], data[1], data[2])
            media_name = data[1]
        else:
            # search the video on YouTube first
            pass

        if not np:
            await ctx.send(f"Playing {media_name}", delete_after=DELETE_TIME)
        else:
            await ctx.send(f"Queued {media_name}", delete_after=DELETE_TIME)

        audio_ctx.play_from_queue()

    @commands.command(aliases=["v"])
    async def volume(self, ctx: commands.Context, num: str):
        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)
        if audio_ctx.get_now_playing():
            try:
                n = float(num)
                if n >= 0 and n <= 2:
                    audio_ctx.get_now_playing().source.volume = n
                    await ctx.send(f"Succesfully set volume to {n}", delete_after=DELETE_TIME)
                else:
                    await ctx.send(f"{n} is not within the range of [0.0-2.0]", delete_after=DELETE_TIME)
            except:
                await ctx.send("Not a valid number", delete_after=DELETE_TIME)
        else:
            await ctx.send("Nothing currently playing", delete_after=DELETE_TIME)