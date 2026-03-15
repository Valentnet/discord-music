import discord
import os
import yt_dlp
import asyncio
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

queue = []

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": False,
    "extract_flat": False,
    "cookiefile": None,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "source_address": "0.0.0.0"
}

FFMPEG_OPTIONS = {
    "options": "-vn"
}


@bot.event
async def on_ready():
    print(f"Bot online sebagai {bot.user}")


# JOIN
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send(f"Masuk ke voice channel {channel.name}")
        else:
            await ctx.voice_client.move_to(channel)

    else:
        await ctx.send("Masuk voice channel dulu.")


# LEAVE
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Keluar dari voice channel.")


# PLAY
@bot.command()
async def play(ctx, url):

    if not ctx.author.voice:
        await ctx.send("Masuk voice channel dulu.")
        return

    vc = ctx.voice_client

    if vc is None:
        vc = await ctx.author.voice.channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

        if "entries" in info:
            for entry in info["entries"]:
                queue.append(entry["url"])
        else:
            queue.append(info["url"])

    await ctx.send("Ditambahkan ke queue.")

    if not vc.is_playing():
        await play_next(vc)


async def play_next(vc):
    if len(queue) == 0:
        return

    url = queue.pop(0)

    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

    vc.play(
        source,
        after=lambda e: asyncio.run_coroutine_threadsafe(
            play_next(vc), bot.loop
        )
    )


bot.run(TOKEN)
