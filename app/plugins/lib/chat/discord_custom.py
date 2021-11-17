import asyncio
import subprocess
import time
import discord
import os


class DiscordCustom:
    def __init__(self, bot, play_sleep_duration=1):
        self.bot = bot
        self.play_sleep_duration = play_sleep_duration

    def get_channel(self, channel_id):
        """
        Get's the channel object from the ID
        :return: the channel object (discord.VoiceChannel)
        """
        return self.bot.client.get_channel(channel_id)

    def get_voice_channel_of_a_user(self, guild_id, user_id):
        """
        Helper method to find what voice channel a user is in
        :param guild_id: the guild ID (int)
        :param user_id: the user ID (int)
        :return: a dict with the channel_id and channel_name - if the user is not in a voice channel, return None
        """
        # Loops through all the voice channels in the guild
        for channel in self.get_all_voice_channels(guild_id):
            # Get all the members in a given voice channel
            member_ids = self.get_voice_channel_members(channel.id)
            # If the user_id is in the list of member_ids, return the channel dict
            if user_id in member_ids:
                return {
                    "channel_id": channel.id,
                    "channel_name": channel.name,
                }
        # If no matches are found, the user is not in a voice channel - Return None
        return None

    def get_all_voice_channels(self, guild_id):
        """
        Get's all the voice channels in a guild
        :return: a list of channels (list)
        """
        guild = self.bot.client.get_guild(guild_id)
        return guild.voice_channels

    def get_voice_channel_members(self, channel_id):
        """
        Get's the member IDs of a Discord voice channel
        :return: a list of member IDs (list)
        """
        channel = self.bot.client.get_channel(channel_id)
        member_ids = channel.voice_states.keys()
        return list(member_ids)

    def play_audio_file(
        self, channel_id, file, preserve_file=False, file_duration=None
    ):
        """
        Play an audio file from disk in a Discord voice channel
        :param channel: the voice channel to play the file in (id)
        :param file_duration: the duration of the file in seconds (int) - Default None will get the duration from youtube-dl
        :param file: the file to play (path)
        """

        # First we get the file duration so we can kick the bot once its done playing
        if file_duration is None:
            file_duration = self.get_audio_file_duration(file)
        # If the file_duration is not None that means it was provided to this function
        else:
            file_duration = float(file_duration)

        # Then we run the runner in a new thread
        asyncio.run_coroutine_threadsafe(
            self.__play_audio_file_runner(channel_id, file, file_duration),
            loop=self.bot.client.loop,
        )

        # Sleep for a little longer than the duration of the audio file, then delete it
        if not preserve_file:
            time.sleep(file_duration + self.play_sleep_duration)
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
