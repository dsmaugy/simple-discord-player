from discord.ext import commands
from media import AudioContextManager
from mediadownload import YTManager
from mediadownload import SCManager
from reels import ReelsManager
import logging
import re

logger = logging.getLogger("bot")
DELETE_TIME = 30 # number of seconds to delete a message after sending

global_blacklist = {}
reels = ReelsManager()

class AdminCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot    

    # only I can access these commands ;)
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id == 122886595077472257

    @commands.command(aliases=["b"])
    async def ban(self, ctx: commands.Context, user: str):
        id = int(re.search(r"[0-9]+", user)[0])
        global_blacklist[id] = True
        await ctx.send(f"Adding user ID {id} to blacklist", delete_after=DELETE_TIME)

    @commands.command(aliases=["ub"])
    async def unban(self, ctx: commands.Context, user: str):
        id = int(re.search(r"[0-9]+", user)[0])
        if id in global_blacklist:
            global_blacklist[id] = False
            await ctx.send(f"Removing user ID {id} from blacklist", delete_after=DELETE_TIME)

    @commands.command()
    async def reel(self, ctx: commands.Context, cmd: str = ""):
        reel_id = str(ctx.channel.guild.id) + "-" + str(ctx.channel.id)
        logger.info(f"CMD: {cmd}, on reel ID: {reel_id}")
        
        if cmd == "status":
            await ctx.send(reels.get_status_str(reel_id), delete_after=DELETE_TIME)
        elif cmd == "on":
            if reels.add_channel(reel_id, ctx.channel):
                await ctx.send(f"Adding channel {reel_id} to reels list", delete_after=DELETE_TIME)
        elif cmd == "off":
            if reels.remove_channel(reel_id):
                await ctx.send(f"Removing channel {reel_id} from reels", delete_after=DELETE_TIME)

        # mention_all = AllowedMentions.all()
        # await ctx.send(f"Edgewood ID: {ctx.guild}, @", allowed_mentions=mention_all, delete_after=5)

class MusicCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self._audio_manager: AudioContextManager = AudioContextManager()

    def cog_check(self, ctx: commands.Context):
        if ctx.author.id in global_blacklist:
            return not global_blacklist[ctx.author.id]
        return True

    async def join_user_channel(self, ctx: commands.Context):
        try:
            vc = ctx.author.voice.channel
        except:
            await ctx.send("User not in voice channel!", delete_after=DELETE_TIME)
            return

        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)
        logger.warn(f"channel: {vc}")
        await audio_ctx.join_channel(vc)

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
        await ctx.send(f"Is Playing: {audio_ctx._vc.is_playing()}. Is Paused: {audio_ctx._vc.is_paused()}. Is Repeat: {audio_ctx._repeat_flag}", delete_after=DELETE_TIME)

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *, args: str):
        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)
        
        # join the user channel if not currently in one:
        if not audio_ctx._vc:
            await self.join_user_channel(ctx)

        data_url = args

        # order of checking:
        # 1. Direct soundcloud link
        # 2. Direct YouTube link
        # 3. Indirect Youtube search
        if args.startswith("https://soundcloud.com"):
            data = await SCManager.from_url(data_url, loop=self.bot.loop)
        elif args.startswith("https://www.youtube.com/watch"):
            data = await YTManager.from_url(data_url, loop=self.bot.loop)
        else:
            # NOT a direct URL (search for the vid on YouTube)
            data_url = YTManager.search_youtube(args)
            if not data_url:
                await ctx.send("Invalid query", delete_after=DELETE_TIME)
                return

            data = await YTManager.from_url(data_url, loop=self.bot.loop)

        audio_ctx.queue_song(data[0], data[1], data[2])

        await ctx.send(f"Queued {data[1]}", delete_after=DELETE_TIME)

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

    # loops current track, skip command will override this
    @commands.command(aliases=["rep"])
    async def repeat(self, ctx: commands.Context):
        audio_ctx = self._audio_manager.get_audio_ctx(ctx.guild.id)
        audio_ctx.repeat_toggle()
        await ctx.send(f"Setting repeat to {audio_ctx._repeat_flag}", delete_after=DELETE_TIME)

