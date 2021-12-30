import discord
from discord.ext import commands
from media import AudioContextManager
import logging

logger = logging.getLogger("bot")
bot = commands.Bot(command_prefix='>')
audio_manager = AudioContextManager()

async def join_user_channel(ctx: commands.Context):
    vc = ctx.author.voice.channel
    audio_ctx = audio_manager.get_audio_ctx(ctx.guild.id)
    if vc:
        await audio_ctx.join_channel(vc)
    else:
        await ctx.send("User not in voice channel!")

@bot.command(aliases=["j"])
async def join(ctx: commands.Context):
    await join_user_channel(ctx)

@bot.command(aliases=["dc"])
async def disconnect(ctx: commands.Context):
    await audio_manager.get_audio_ctx(ctx.guild.id).disconnect_channel()

@bot.command()
async def test(ctx: commands.Context):
    await join_user_channel(ctx)
    audio = discord.FFmpegPCMAudio("/home/darwin/Music/Life Is Strange Complete Soundtrack/142 - The Choice.mp3")
    audio_ctx = audio_manager.get_audio_ctx(ctx.guild.id)
    logger.warn(f"Guild ID: {ctx.guild.id} Audio Context: {audio_ctx}")
    audio_ctx.queue_song(audio, "Life is Strange - Pause Menu 1")
    audio_ctx.play_from_queue()

    await ctx.send("bingus")

@bot.command(aliases=["stop"])
async def pause(ctx: commands.Context):
    audio_manager.get_audio_ctx(ctx.guild.id).pause()

@bot.command(aliases=["r"])
async def resume(ctx: commands.Context):
    audio_manager.get_audio_ctx(ctx.guild.id).resume()


@bot.command(aliases=["q"])
async def queue(ctx: commands.Context):
    queue = audio_manager.get_audio_ctx(ctx.guild.id).get_queue()
    output = ""
    logger.warn(queue.__str__())
    for i in range(0, len(queue)):
        output += f"{i+1}. {queue[i].name}\n"

    if len(queue) == 0:
        await ctx.send("Queue empty")
    else:
        await ctx.send(output)

@bot.command(aliases=["np"])
async def now_playing(ctx: commands.Context):
    queue = audio_manager.get_audio_ctx(ctx.guild.id).get_queue()
    if len(queue) > 0:
        await ctx.send(queue[0].name)

@bot.command(aliases=["s"])
async def skip(ctx: commands.Context):
    audio_ctx = audio_manager.get_audio_ctx(ctx.guild.id)

    if len(audio_ctx.get_queue()) > 0:
        np = audio_ctx.get_queue()[0]
        audio_ctx.skip()

        await ctx.send(f"Skipped {np.name}")
    else:
        await ctx.send("No songs in queue")