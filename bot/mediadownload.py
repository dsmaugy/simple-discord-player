import youtube_dl
import asyncio

class YTManager():
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

    '''
    Returns a URL to the mp3, the title, and the duration of a video in a tuple. 
    '''
    @classmethod
    async def from_url(cls, url, loop=None) -> tuple:
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: YTManager.ytdl.extract_info(url, download=False))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        
        mins = data['duration'] // 60
        sec = data['duration'] % 60
        return (data['url'], data['title'], f"{mins}:{sec:02d}")


