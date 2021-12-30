from pyyoutube import Api as YTApi
import youtube_dl
import asyncio
import os
import logging

logger = logging.getLogger("mediadownload")

ytdl = youtube_dl.YoutubeDL(params={
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
})

ytapi = YTApi(api_key=os.environ["YOUTUBE_API"])

class YTManager():

    @classmethod
    async def from_url(cls, url, loop=None) -> tuple:
        '''
        Given a URL to a YouTube video, returns a URL to the mp3, the title, and the duration of a video in a tuple. 
        '''

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        
        mins = data['duration'] // 60
        sec = data['duration'] % 60
        return (data['url'], data['title'], f"{mins}:{sec:02d}")

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
