from os.path import join as pjoin
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from youtubesearchpython import Video, VideosSearch
import os
import time
import discord

class MusicPlay:
    
    def __init__(self, id, secret):
        self.title = None
        self.link = None
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
        keys = {}
        with open("ClientKey.txt") as f:
            for line in f:
                key, val = line.strip().split()
                keys[key] = val
        spotify_credentials = SpotifyClientCredentials(
            client_id=id,
            client_secret=secret
        )
        self.sp = Spotify(auth_manager=spotify_credentials)

    def download_and_play_next(self, voice):
        if not self.song_queue:
            self.title = None
            self.link = None
            return
        self.link, self.title = self.song_queue.pop(0)
        self.download_song()
        if voice.is_playing():
            voice.stop()
            time.sleep(1)   # file is still being used by voice
        self.replace_song()
        self.play(voice)

    def download_song(self):
        self.delete_old_file()
        with YoutubeDL(self.ydl_opts) as ydl:
            print("Downloading", self.title)
            ydl.download([self.link])
        
    def replace_song(self):
        self.delete_curr_file()
        os.rename(pjoin("folders", "send", "ytdl.mp3"), pjoin("folders", "send", "song.mp3"))

    def parse_search(self, text):
        if text.split()[-1][:4] == 'vol=':
            num = text.split()[-1][4:]
            if num.isnumeric() and 0 <= int(num) <= 100:
                self.volume = int(num)
            text = text[:-1]
        orig_queue_len = len(self.song_queue)
        if 'https://www.youtube.com/' in text:
            link = text
            title = Video.get(text)['title']
            self.song_queue.append((link, title))
        elif 'https://open.spotify.com/playlist/' in text:
            self.add_songs_from_playlist(text)
        elif 'https://open.spotify.com/track/' in text:
            song = self.sp.track(text)
            artist = song['artists'][0]['name']
            title = song['name']
            self.search_song(artist + " " + title)
        else:
            self.search_song(text)
        
        new_queue_len = len(self.song_queue) - orig_queue_len
        if new_queue_len == 1:
            return [self.song_queue[-1], ]
        if new_queue_len > 1:
            return self.song_queue[1:]
        return []
    
    def add_songs_from_playlist(self, link):
        result = self.sp.playlist_items(link, additional_types=['track'])
        tracks = result['items']
        while result['next']:
            result = self.sp.next(result)
            tracks.extend(result['items'])
        tracks.reverse()
        print(f"Adding {len(tracks)} tracks to queue")
        for item in tracks:
            artist = item['track']['artists'][0]['name']
            title = item['track']['name']
            self.search_song(artist + " " + title)

    def search_song(self, search):
        custom_search = VideosSearch(search, limit=1)
        result = custom_search.result()['result'][0]
        self.song_queue.append((result['link'], result['title']))

    def delete_old_file(self):
        if os.path.isfile(pjoin("folders", "send", "ytdl.mp3")):
            os.remove(pjoin("folders", "send", "ytdl.mp3"))

    def delete_curr_file(self):
        if os.path.isfile(pjoin("folders", "send", "song.mp3")):
            os.remove(pjoin("folders", "send", "song.mp3"))
    
    def next_song(self):
        if len(self.song_queue):
            return self.song_queue[0]
        return None
    
    def show_queue(self):
        if not self.song_queue and not self.title:
            return "The queue is empty"
        songs = [
            f'**Currently playing:** {self.title}',
            *[
                f"**{i+1}.** {song[1]}"
                for i, song in enumerate(self.song_queue[:10])
            ],
        ]

        if len(self.song_queue) > 10:
            songs.append(f"**.. and {len(self.song_queue)-10} other songs**")
        return '\n'.join(songs)
    
    def clear_queue(self):
        self.song_queue = []
        
    def play(self, voice):
        voice.play(discord.FFmpegPCMAudio(pjoin("folders", "send", "song.mp3")), after=lambda e: self.download_and_play_next(voice))
        voice.source = discord.PCMVolumeTransformer(voice.source, volume=float(self.volume) / 100)
