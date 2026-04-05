import yt_dlp as youtube_dl
import discord
from discord.ext import commands
import asyncio

# FFmpeg options for voice
ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

# yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
    
    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]
    
    async def play_song(self, ctx, song_url):
        voice_client = ctx.voice_client
        
        if not voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                voice_client = ctx.voice_client
            else:
                await ctx.send("You need to be in a voice channel!")
                return False
        
        # Extract song info
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_url, download=False)
                song_url = info['url']
                title = info.get('title', 'Unknown')
                
                source = await discord.FFmpegOpusAudio.from_probe(
                    song_url, **ffmpeg_options
                )
                
                def after_playing(error):
                    if error:
                        print(f"Error: {error}")
                    asyncio.run_coroutine_threadsafe(
                        self.play_next(ctx), self.bot.loop
                    )
                
                if voice_client.is_playing():
                    queue = self.get_queue(ctx.guild.id)
                    queue.append((source, title, song_url))
                    await ctx.send(f"Added to queue: **{title}**")
                else:
                    voice_client.play(source, after=after_playing)
                    await ctx.send(f"Now playing: **{title}**")
                return True
                
        except Exception as e:
            await ctx.send(f"Error playing song: {str(e)}")
            return False
    
    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if queue:
            source, title, url = queue.pop(0)
            voice_client = ctx.voice_client
            
            def after_playing(error):
                if error:
                    print(f"Error: {error}")
                asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx), self.bot.loop
                )
            
            voice_client.play(source, after=after_playing)
            await ctx.send(f"Now playing: **{title}**")
