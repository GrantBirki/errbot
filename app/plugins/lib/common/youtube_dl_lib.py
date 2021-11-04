from __future__ import unicode_literals
import youtube_dl
import uuid


class YtdlLib:
    def __init__(self, max_length=600):
        """
        Initialize the youtube_dl library
        :param max_length: the maximum length of a video in seconds (default 600 aka 10 minutes)
        """
        self.path = "plugins/play/audio"
        self.max_length = max_length

    def video_length(self, url):
        """
        Get the length of a video in seconds given a url
        Does not download the video, only reads the metadata
        :param url: the full url to the video
        :return: the length of the video in seconds (int)
        """
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "prefer_ffmpeg": True,
            "audioformat": "wav",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            dictMeta = ydl.extract_info(url, download=False)
            return int(dictMeta["duration"])

    def download_audio(self, url):
        """
        Downloads an audio file from a given youtube url
        :param url: the full url to the video
        :return: the path to the downloaded audio file
        """

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
