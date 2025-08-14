import asyncio
import discord
import yt_dlp
from typing import Any, Dict, Optional

FFMPEG_OPTIONS = {"options": "-vn"}
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


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
    async def from_url(
        cls,
        url: str,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        stream: bool = True,
    ):
        """
        Downloads or streams audio from a YouTube URL or search term.
        """
        loop = loop or asyncio.get_event_loop()

        # Extract info without blocking the event loop
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        data2 = ytdl.sanitize_info(data)

        # If it's a playlist/search, take the first result
        if isinstance(data, dict) and "entries" in data:
            data = data["entries"][0]

        # Pick stream URL or downloaded file path
        filename = data["url"] if stream else ytdl.prepare_filename(data)  # type: ignore

        # Pylance might complain here — we don't care
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)  # type: ignore
