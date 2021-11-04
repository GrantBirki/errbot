import asyncio
import subprocess
import time
import discord
import os


class DiscordCustom:
    def __init__(self, bot):
        self.bot = bot

    def play_audio_file(self, channel_id, file, preserve_file=False):
        """
        Play an audio file from disk in a Discord voice channel
        :param channel: the voice channel to play the file in (id)
        :param file: the file to play (path)
        """

        # First we get the file duration so we can kick the bot once its done playing
        file_duration = self.get_audio_file_duration(file)

        # Then we run the runner in a new thread
        asyncio.run_coroutine_threadsafe(
            self.__play_audio_file_runner(channel_id, file, file_duration),
            loop=self.bot.client.loop,
        )

        # Sleep for a little longer than the duration of the audio file, then delete it
        if not preserve_file:
            time.sleep(file_duration + 5)
            if os.path.exists(file):
                os.remove(file)

    def get_audio_file_duration(self, file):
        """
        Get's the audio file duration in seconds as a float
        :return: the duration of the file in seconds (float)
        """

        # Use native FFMPEG to get the duration of the file
        process = subprocess.Popen(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout, _ = process.communicate()
        return float(stdout)

    async def __play_audio_file_runner(self, channel_id, file, file_duration):
        """
        A disgusting function to connect to a Discord voice channel and play an audio file. Disconnects once the file is done playing (we hope)
        """

        # Get the channel object from the ID
        channel = self.bot.client.get_channel(channel_id)
        # Connect to the channel
        vc = await channel.connect()

        # Play the file
        vc.play(discord.FFmpegPCMAudio(file), after=vc.stop())

        # Sleep and block the thread for the duration of the audio file
        await asyncio.sleep(file_duration + 0.75)
        # Disconnect from the channel
        await vc.disconnect()
