import asyncio
from typing import Any

import discord
import yt_dlp
from yt_dlp.YoutubeDL import YoutubeDL

FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
}

ytdl: YoutubeDL = yt_dlp.YoutubeDL(YTDL_OPTIONS)  # pyright: ignore[reportArgumentType]


class YTQueueElement:
    def __init__(self, query: str, data: dict[str, Any]):
        self.query: str = query
        self.title: str = data.get("title", "Unknown title")
        self.webpage_url: str = data.get("webpage_url", query)

    @classmethod
    async def from_query(cls, query: str, loop: asyncio.AbstractEventLoop | None = None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        if "entries" in data:
            data = data["entries"][0]

        return cls(query, data)  # pyright: ignore[reportArgumentType]

    async def create_player(self, loop: asyncio.AbstractEventLoop | None = None, stream: bool = True):
        return await YTDLSource.from_url(self.query, loop=loop, stream=stream)


class YTDLSource(discord.PCMVolumeTransformer[discord.AudioSource]):
    def __init__(
        self,
        source: discord.AudioSource,
        *,
        data: dict[str, Any],
        volume: float = 0.5,
    ):
        super().__init__(source, volume)
        self.data: dict[str, Any] = data
        self.title: str = data.get("title", "Unknown title")
        self.url: str = data.get("url", "")

    @classmethod
    async def from_url(cls, url: str, *, loop: asyncio.AbstractEventLoop | None = None, stream: bool = True):
        """
        Downloads or streams audio from a YouTube URL or search term.
        """
        loop = loop or asyncio.get_event_loop()

        # Extract info without blocking the event loop
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        # If it's a playlist/search, take the first result
        if "entries" in data.keys():
            data = data["entries"][0]

        # Pick stream URL or downloaded file path
        filename = data["url"] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)
