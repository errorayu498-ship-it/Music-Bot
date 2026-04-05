import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from music import MusicPlayer

load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)
music_player = MusicPlayer(bot)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="!play to play music"))

# Music commands
@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    """Play a song from YouTube"""
    await music_player.play_song(ctx, query)

@bot.command(name='skip')
async def skip(ctx):
    """Skip the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped the current song!")
    else:
        await ctx.send("Nothing is playing right now!")

@bot.command(name='stop')
async def stop(ctx):
    """Stop playback and clear queue"""
    if ctx.voice_client:
        queue = music_player.get_queue(ctx.guild.id)
        queue.clear()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 Stopped playback and cleared queue!")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command(name='pause')
async def pause(ctx):
    """Pause the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused the music!")
    else:
        await ctx.send("Nothing is playing!")

@bot.command(name='resume')
async def resume(ctx):
    """Resume the paused song"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed the music!")
    else:
        await ctx.send("The music is not paused!")

@bot.command(name='queue', aliases=['q'])
async def show_queue(ctx):
    """Show the current music queue"""
    queue = music_player.get_queue(ctx.guild.id)
    if queue:
        queue_list = []
        for i, (_, title, _) in enumerate(queue[:10], 1):
            queue_list.append(f"{i}. {title}")
        
        embed = discord.Embed(
            title="📋 Music Queue",
            description="\n".join(queue_list),
            color=discord.Color.blue()
        )
        if len(queue) > 10:
            embed.set_footer(text=f"And {len(queue) - 10} more...")
        await ctx.send(embed=embed)
    else:
        await ctx.send("The queue is empty!")

@bot.command(name='now', aliases=['np'])
async def now_playing(ctx):
    """Show the currently playing song"""
    # This is simplified - you might want to store current song info
    await ctx.send("Use !queue to see current songs")

@bot.command(name='leave')
async def leave(ctx):
    """Make the bot leave the voice channel"""
    if ctx.voice_client:
        queue = music_player.get_queue(ctx.guild.id)
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel!")
    else:
        await ctx.send("I'm not in a voice channel!")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found! Use !help for available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: {error.param.name}")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in .env file")
        exit(1)
    bot.run(token)
