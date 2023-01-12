from pyyoutube import Api as YTApi
from yt_dlp import YoutubeDL
from sclib import SoundcloudAPI
from datetime import datetime

import asyncio
import os
import logging
import requests



logger = logging.getLogger("mediadownload")

YTDL_COMMON_PARAMS = {
    'format': 'm4a/bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
}
# Use YTDLP fork of YTDL to work with age restricted videos
ytdl_extract = YoutubeDL(params=YTDL_COMMON_PARAMS)

ytapi = YTApi(api_key=os.environ["YOUTUBE_API"])
scapi = SoundcloudAPI() 

class YTManager():

    @classmethod
    async def from_url(cls, url, loop=None, download=True) -> tuple:
        '''
        Given a URL to a YouTube video, returns a URL to the mp3, the title, and the duration of a video in a tuple. 
        '''

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl_extract.extract_info(url, download=False))
        
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        
        mins = data['duration'] // 60
        sec = data['duration'] % 60

        if not download:
            audio_url = data['url']
        else:
            ytdl_download_params = YTDL_COMMON_PARAMS.copy()
            ytdl_download_params['outtmpl'] = f"/tmp/{datetime.now()}-{data['title']}"
            with YoutubeDL(ytdl_download_params) as ytdl_download:
                await loop.run_in_executor(None, lambda: ytdl_download.download(url))
                
            audio_url = ytdl_download_params['outtmpl']
 
        return (audio_url, data['title'], f"{mins}:{sec:02d}")
        

    @classmethod
    def search_youtube(cls, query) -> str:
        '''
        Searches YouTube for a video with the given query and returns the full URL of that video
        Returns None if the search finds nothing
        '''

        r = ytapi.search_by_keywords(q=query, search_type=["video"], count=1)
        if len(r.items) > 0:
            logger.info(f"Found https://www.youtube.com/watch?v={r.items[0].id.videoId}")
            return f"https://www.youtube.com/watch?v={r.items[0].id.videoId}"
        else:
            return None

class SCManager():

    @classmethod
    async def from_url(cls, url, loop=None) -> tuple:
        '''
        Given a URL to a SoundCloud song, returns a URL to the mp3, the title, and the duration of the track in a tuple. 
        '''

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: scapi.resolve(url))
        
        total_sec = data.duration / 1000

        mins = int(total_sec // 60)
        sec = int(total_sec % 60)
        return (data.get_stream_url(), f"{data.title} - {data.artist}", f"{mins}:{sec:02d}")