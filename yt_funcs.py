import urllib.request
import re
import validators

from yt_dlp_source import YTDLSource


class YTQueue:
    def __init__(self):
        # self.songs = []
        self.songs: list[YTDLSource] = []
        
    def add_song(self, player: YTDLSource):
        self.songs.append(player)
    
    def length(self):
        return len(self.songs)
    
    def get_titles(self, all=False, index=-1):
        if all:
            return "\n".join(f"{i} - " + self.songs[i].title for i in range(len(self.songs)))
        else:
            return str(self.songs[index].title)
        
    def remove_song_index(self, index: int):
        self.songs.pop(index)
    
    def remove_song_keyword(self, keyword: list[str]):
        pass
    
    def get_next_song(self) -> YTDLSource:
        pass
    
    def pop(self) -> YTDLSource:
        return self.songs.pop(0)
    
    def is_empty(self) -> bool:
        return len(self.songs) < 1

    # # same as add_url, but also accepts searchwords.
    # def add_search(self, args):
    #     if validators.url(args[0]):
    #         self.add_url(args[0])
    #     else:
    #         # -play [search words] was called
    #         url = yt_search(args, first=True)
    #         self.add_url(url)

    # # adds song to queue, but only accepts an url
    # def add_url(self, url):
    #     http_response = urllib.request.urlopen(url)

    #     x = str(http_response.read())
    #     title = x[x.find("<title>") + 7 : x.find("</title>") - 10]

    #     self.songs.append({"url": url, "title": title})

    # def remove_song(self, index):
    #     if index < 0 or index >= len(self.songs):
    #         raise Exception("index to remove out of range")
    #     else:
    #         del self.songs[index]

    # def pop(self):
    #     return self.songs.pop(0)

    # def get_next_song(self, delete=False):
    #     if delete:
    #         return self.songs.pop(0)
    #     else:
    #         return self.songs[0]

    # def get_urls(self, all=False, index=-1):
    #     if all:
    #         return "\n".join(f"{i} - " + self.songs[i]["url"] for i in range(len(self.songs)))
    #     else:
    #         return str(self.songs[index]["url"])

    # def get_titles(self, all=False, index=-1):
    #     if all:
    #         return "\n".join(f"{i} - " + self.songs[i]["title"] for i in range(len(self.songs)))
    #     else:
    #         return str(self.songs[index]["title"])

    # def is_empty(self):
    #     # DOES NOT WORK FOR SOME REASON
    #     return len(self.songs) == 0


def yt_search(searchwords, first=True):
    searchstring = "+".join(searchwords)
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + searchstring)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    if first:
        return "https://www.youtube.com/watch?v=" + video_ids[0]
    else:
        return video_ids[0:10]


dm_texts = [
    """Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you""",
    """Somebody once told me the world is gonna roll me
I ain't the sharpest tool in the shed
She was looking kind of dumb with her finger and her thumb
In the shape of an "L" on her forehead

Well, the years start coming and they don't stop coming
Fed to the rules and I hit the ground running
Didn't make sense not to live for fun
Your brain gets smart but your head gets dumb

So much to do, so much to see
So what's wrong with taking the back streets?
You'll never know if you don't go
You'll never shine if you don't glow

Hey, now, you're an all-star, get your game on, go play
Hey, now, you're a rock star, get the show on, get paid
And all that glitters is gold
Only shooting stars break the mold""",
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Curabitur vitae nunc sed velit dignissim. Felis donec et odio pellentesque diam volutpat commodo. Id eu nisl nunc mi ipsum faucibus. Pulvinar neque laoreet suspendisse interdum consectetur libero. Enim tortor at auctor urna nunc id. Suspendisse potenti nullam ac tortor vitae purus. Ipsum consequat nisl vel pretium lectus quam. Egestas congue quisque egestas diam in arcu. Quis blandit turpis cursus in hac habitasse platea dictumst quisque. Sed velit dignissim sodales ut eu sem integer. Aenean pharetra magna ac placerat vestibulum. Lectus magna fringilla urna porttitor. Aliquam faucibus purus in massa tempor nec feugiat. Tristique sollicitudin nibh sit amet commodo nulla facilisi. Cursus sit amet dictum sit amet. Ac turpis egestas sed tempus urna et pharetra pharetra. Tellus rutrum tellus pellentesque eu tincidunt tortor aliquam nulla facilisi. Placerat in egestas erat imperdiet sed euismod nisi porta. Et tortor at risus viverra adipiscing at in tellus integer.""",
    """(Black screen with text; The sound of buzzing bees can be heard)

Narrator:
According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.

(Barry is picking out a shirt)

Barry:
Yellow, black. Yellow, black. Yellow, black. Yellow, black. Ooh, black and yellow! Let's shake it up a little.

Janet:
Barry! Breakfast is ready!

Barry:
Coming! Hang on a second.

(Barry uses his antenna like a phone)

Barry:
Hello

(Through phone)

Adam:
Barry?

Barry:
Adam?

Adam:
Can you believe this is happening?

Barry:
I can't. I'll pick you up.

(Barry flies down the stairs)

Martin:
Looking sharp.

Janet:
Use the stairs. Your father paid good money for those.

Barry:
Sorry. I'm excited.

Martin:
Here's the graduate. We're very proud of you, son. A perfect report card, all B's.

Janet:
Very proud.

(Rubs Barry's hair)

Barry:
Ma! I got a thing going here.

Janet:
You got lint on your fuzz.

Barry:
Ow! That's me!

Janet:
Wave to us! We'll be in row 118,000. Bye!

(Barry flies out the door)

Janet:
Barry, I told you, stop flying in the house!

(Barry drives through the hive,and is waved at by Adam who is reading a newspaper)

Barry:
Hey, Adam.

Adam:
Hey, Barry.

(Adam gets in Barry's car)

Adam:
Is that fuzz gel?

Barry:
A little. Special day, graduation.

Adam:
Never thought I'd make it.

(Barry pulls away from the house and continues driving)

Barry:
Three days grade school, three days high school...

Adam:
Those were awkward.

Barry:
Three days college. I'm glad I took a day and hitchhiked around the hive.

Adam:
You did come back different.

(Barry and Adam pass by Artie, who is jogging)

Artie:
Hi, Barry!

Barry:
Artie, growing a mustache? Looks good.

Adam:
Hear about Frankie?
...""",
]
