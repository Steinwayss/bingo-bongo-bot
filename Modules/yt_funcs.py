from Modules.yt_dlp_source import YTQueueElement


class YTQueue:
    def __init__(self):
        self.songs: list[YTQueueElement] = []

    def add_song(self, song: YTQueueElement):
        self.songs.append(song)

    def pop(self) -> YTQueueElement | None:
        if len(self.songs) > 0:
            return self.songs.pop(0)
        return None

    def length(self):
        return len(self.songs)

    def is_empty(self) -> bool:
        return len(self.songs) < 1

    def get_titles(self):
        return "\n".join(f"{i} - " + self.songs[i].title for i in range(len(self.songs)))

    def get_title(self, index: int):
        return str(self.songs[index].title)

    def remove_song_index(self, index: int):
        self.songs.pop(index)

    def remove_song_keyword(self, keyword: list[str]):
        # TODO
        pass
