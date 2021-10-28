from __future__ import unicode_literals
import youtube_dl
import uuid


class YtdlLib:
    def __init__(self):
        self.path = "plugins/play/audio"

    def download_audio(self, url):

        output_file = f"{self.path}/{uuid.uuid4()}.mp3"

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": output_file,
            "quiet": True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return output_file
