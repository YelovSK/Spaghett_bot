import json
import os
import disnake
import time

from asyncio import run_coroutine_threadsafe as rct
from message_send import bot_send
from disnake.ext import commands
from disnake.ext.commands import Context
from disnake.ext.commands import Bot
from os.path import join as pjoin
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from youtubesearchpython import Video, VideosSearch

with open("config.json") as file:
    config = json.load(file)

class Music(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.voice = None
        self.title = None
        self.link = None
        self.ctx = None
        self.song_queue = []
        self.volume = 100
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': pjoin("folders", "send", "ytdl.mp3"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        spotify_credentials = SpotifyClientCredentials(
            client_id=config["spotify-id"],
            client_secret=config["spotify-secret"]
        )
        self.sp = Spotify(auth_manager=spotify_credentials)

    async def download_and_play_next(self):
        if not self.song_queue:
            self.title = None
            self.link = None
            return
        self.link, self.title = self.song_queue.pop(0)
        await self.download_song()
        if self.voice.is_playing():
            self.voice.stop()
            time.sleep(1)   # file is still being used by voice
        await self.replace_song()
        await self.start_playing()

    async def download_song(self):
        await self.delete_old_file()
        with YoutubeDL(self.ydl_opts) as ydl:
            await bot_send(self.ctx, f"Downloading **{self.title}**")
            ydl.download([self.link])

    async def replace_song(self):
        await self.delete_curr_file()
        os.rename(pjoin("folders", "send", "ytdl.mp3"), pjoin("folders", "send", "song.mp3"))

    async def parse_search(self, text):
        if text.split()[-1][:4] == 'vol=':
            num = text.split()[-1][4:]
            if num.isnumeric() and 0 <= int(num) <= 100:
                self.volume = int(num)
            text = text[:-1]
        orig_queue_len = len(self.song_queue)
        if 'https://www.youtube.com/' in text:
            link = text
            title = Video.get(text)['title']
            await self.song_queue.append((link, title))
        elif 'https://open.spotify.com/playlist/' in text:
            await self.add_songs_from_playlist(text)
        elif 'https://open.spotify.com/track/' in text:
            song = self.sp.track(text)
            artist = song['artists'][0]['name']
            title = song['name']
            await self.search_song(artist + " " + title)
        else:
            await self.search_song(text)
        
        new_queue_len = len(self.song_queue) - orig_queue_len
        if new_queue_len == 1:
            return [self.song_queue[-1], ]
        if new_queue_len > 1:
            return self.song_queue[1:]
        return []

    async def add_songs_from_playlist(self, link):
        result = self.sp.playlist_items(link, additional_types=['track'])
        tracks = result['items']
        while result['next']:
            result = self.sp.next(result)
            tracks.extend(result['items'])
        tracks.reverse()
        await bot_send(self.ctx, f"Adding **{len(tracks)} songs** to queue")
        for item in tracks:
            artist = item['track']['artists'][0]['name']
            title = item['track']['name']
            await self.search_song(artist + " " + title)

    async def search_song(self, search):
        custom_search = VideosSearch(search, limit=1)
        result = custom_search.result()['result'][0]
        self.song_queue.append((result['link'], result['title']))

    async def delete_old_file(self):
        if os.path.isfile(pjoin("folders", "send", "ytdl.mp3")):
            os.remove(pjoin("folders", "send", "ytdl.mp3"))

    async def delete_curr_file(self):
        if os.path.isfile(pjoin("folders", "send", "song.mp3")):
            os.remove(pjoin("folders", "send", "song.mp3"))

    async def connect_voice(self):
        if not self.voice:
            self.voice = await self.ctx.author.voice.channel.connect()

    async def start_playing(self):
        self.voice.play(disnake.FFmpegPCMAudio(pjoin("folders", "send", "song.mp3")), after=lambda e: rct(self.download_and_play_next(), self.bot.loop))
        self.voice.source = disnake.PCMVolumeTransformer(self.voice.source, volume=float(self.volume) / 100)
        send_list = [
            f"Playing **{self.title}**",
            self.link,
            'Commands: play | pause | resume | stop | skip | queue | clearqueue | volume | leave',
        ]
        await bot_send(self.ctx, "\n".join(send_list))

    @commands.command()
    async def clearqueue(self, ctx: Context):
        self.song_queue = []
        await bot_send(ctx, "Song queue cleared")

    @commands.command()
    async def play(self, ctx: Context, *, url):
        self.ctx = ctx
        await self.connect_voice()
        songs_added = await self.parse_search(url)
        if self.voice.is_playing() or self.voice.is_paused():
            if len(songs_added) == 1:
                added_title = songs_added[0][1]
            else:
                added_title = f"{len(songs_added)} songs"
            await bot_send(ctx, f"Added **{added_title}** to queue")
            return
        await self.download_and_play_next()

    @commands.command()
    async def playfile(self, ctx: Context, *, url):
        if not self.voice:
            self.voice = await ctx.author.voice.channel.connect()

        if os.path.isfile(url) and (self.voice.is_playing() or self.voice.is_paused()):
            self.voice.stop()
            time.sleep(1)

        self.voice.play(disnake.FFmpegPCMAudio(url))
        await bot_send(ctx, f"Playing {url}")

    @commands.command()
    async def join(self, ctx: Context):
        self.voice = await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self, ctx: Context):
        if self.voice and self.voice.is_connected():
            await self.voice.disconnect()
            await bot_send(ctx, "Disconnected")
        else:
            await bot_send(ctx, "I'm not connected ya dingus")

    @commands.command()
    async def pause(self, ctx: Context):
        if self.voice and self.voice.is_playing():
            self.voice.pause()
            await bot_send(ctx, f"Paused - **{self.title}**")
        else:
            await bot_send(ctx, "Not playin' anything")

    @commands.command()
    async def resume(self, ctx: Context):
        if self.voice and self.voice.is_paused():
            self.voice.resume()
            await bot_send(ctx, f"Resumed - **{self.title}**")
        else:
            await bot_send(ctx, "Shit's not paused yo")

    @commands.command()
    async def skip(self, ctx: Context, skip_num="1"):
        if not self.voice:
            await bot_send(ctx, "Not connected")
            return
        if skip_num.isnumeric() and int(skip_num) > 1:
            self.song_queue = self.song_queue[skip_num-1:]
        self.voice.stop()
        if not len(self.song_queue):
            await bot_send(ctx, "The end of queue")

    @commands.command()
    async def queue(self, ctx: Context):
        if not self.song_queue and not self.title:
            await bot_send(ctx, "The queue is empty")
        songs = [
            f'**Currently playing:** {self.title}',
            *[
                f"**{i+1}.** {song[1]}"
                for i, song in enumerate(self.song_queue[:10])
            ],
        ]
        if len(self.song_queue) > 10:
            songs.append(f"**.. and {len(self.song_queue)-10} other songs**")
        await bot_send(ctx, "\n".join(songs))

    @commands.command()
    async def stop(self, ctx: Context):
        if self.voice and self.voice.is_playing():
            self.song_queue = []
            self.voice.stop()
            await bot_send(ctx, "Stopped")
        else:
            await bot_send(ctx, "Music isn't playing")

    @commands.command()
    async def volume(self, ctx: Context, *, volume):
        if not self.voice:
            await bot_send(ctx, "Not connected")
        elif volume.isnumeric() and 0 <= int(volume) <= 100:
            self.voice.source.volume = float(volume) / 100
            await bot_send(ctx, f"Set volume to {volume}%")
        else:
            await bot_send(ctx, "Volume must be between <0, 100>")

    @commands.command()
    async def currentvolume(self, ctx: Context):
        if not self.voice:
            await bot_send(ctx, "Not connected")
        else:
            await bot_send(ctx, f"Current volume: {self.voice.source.volume * 100}%")

    @commands.command()
    async def maximumpain(self, ctx: Context):
        if not self.voice:
            await bot_send(ctx, "Not connected")
        else:
            self.voice.source.volume = float(1_000_000) / 100

def setup(bot):
    bot.add_cog(Music(bot))
