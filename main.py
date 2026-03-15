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

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

queue = []

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True
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
        else:
            await ctx.voice_client.move_to(channel)
    else:
        await ctx.send("Masuk voice channel dulu.")


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
        try:
            info = ydl.extract_info(url, download=False)
        except Exception:
            await ctx.send("Gagal mengambil audio dari YouTube.")
            return

    if "entries" in info:
        info = info["entries"][0]

    audio_url = info["url"]

    source = await discord.FFmpegOpusAudio.from_probe(
        audio_url,
        **FFMPEG_OPTIONS
    )

    vc.play(source)

    await ctx.send(f"Memutar: {info['title']}")


# LEAVE
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


bot.run(TOKEN)
