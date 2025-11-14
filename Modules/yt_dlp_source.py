import asyncio
from typing import Any, Dict, Optional

import discord
import yt_dlp

FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


class YTQueueElement:
    def __init__(self, query: str, data: dict):
        self.query = query
        self.title = data.get("title", "Unknown title")
        self.webpage_url = data.get("webpage_url", query)

    @classmethod
    async def from_query(cls, query: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        if "entries" in data:  # type: ignore
            data = data["entries"][0]  # type: ignore

        return cls(query, data)  # type: ignore

    async def create_player(self, loop: Optional[asyncio.AbstractEventLoop] = None, stream=True):
        return await YTDLSource.from_url(self.query, loop=loop, stream=stream)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(
        self,
        source: discord.AudioSource,
        *,
        data: Dict[str, Any],
        volume: float = 0.5,
    ):
        super().__init__(source, volume)
        self.data = data
        self.title: str = data.get("title", "Unknown title")
        self.url: str = data.get("url", "")

    @classmethod
    async def from_url(cls, url: str, *, loop: Optional[asyncio.AbstractEventLoop] = None, stream: bool = True):
        """
        Downloads or streams audio from a YouTube URL or search term.
        """
        loop = loop or asyncio.get_event_loop()

        # Extract info without blocking the event loop
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        # If it's a playlist/search, take the first result
        if isinstance(data, dict) and "entries" in data:
            data = data["entries"][0]

        # Pick stream URL or downloaded file path
        filename = data["url"] if stream else ytdl.prepare_filename(data)  # type: ignore

        # Pylance might complain here — we don't care
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)  # type: ignore
