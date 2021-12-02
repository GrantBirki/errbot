import asyncio
from asyncio.exceptions import CancelledError
import os
import re
import subprocess
import time

import discord

from lib.chat.discord import Discord
from lib.common.utilities import Util

discord_custom = Discord()
util = Util()


class DiscordCustom:
    def __init__(
        self,
        bot,
        play_sleep_duration=1,
        kill_switch_path="plugins/lib/chat/dc_kill_switches",
    ):
        self.bot = bot
        self.play_sleep_duration = play_sleep_duration
        self.kill_switch_path = kill_switch_path

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

    def send_file(self, channel_id, file, content=None):
        """
        Send a file to a Discord channel
        :param channel_id: the channel to send the file to (int)
        :param file: the file to send (path)
        :param content: the content/message to send with the file (str) - (optional)
        :return: False if the file size is too large
        """
        # Check the file size
        max_file_size = 5242880 # 5MB
        file_size = os.path.getsize(file)
        if file_size > max_file_size:
            return False

        # Run the __send_file_runner in a new thread
        asyncio.run_coroutine_threadsafe(
            self.__send_file_runner(channel_id, file, content),
            loop=self.bot.client.loop,
        )

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
            file_duration = int(file_duration)

        # Then we run the runner in a new thread
        future = asyncio.run_coroutine_threadsafe(
            self.__play_audio_file_runner(channel_id, file, file_duration),
            loop=self.bot.client.loop,
        )

        # Create the kill switch path to check - a file who's name matches the plugin path of the file to play
        kill_switch = (
            self.kill_switch_path
            + "/"
            + file.split("plugins/")[1].split("/")[0]
            + ".kill"
        )

        # Get the current time, and add the file duration to it
        now = util.parse_iso_timestamp(util.iso_timestamp())
        while True:
            # look for a 'kill' file on disk and ensure the file has been playing for a couple of seconds to be properly killed
            if os.path.isfile(kill_switch) and util.is_timestamp_older_than_n_seconds(
                now, 3
            ):
                # If the 'kill' file is found, cancel the future and exit the loop
                future.cancel()
                # Remove the kill switch file
                os.remove(kill_switch)
                break

            # If the 'kill' file is not found, check the current time
            if util.is_timestamp_older_than_n_seconds(
                now, file_duration + self.play_sleep_duration
            ):
                # If the current time is greater than the file duration, exit the loop
                break

            # If no 'kill' file is found, and the file duration is still 'playing', sleep check again
            time.sleep(2)

        # Delete the file after it is done playing
        if not preserve_file:
            if os.path.exists(file):
                os.remove(file)

    def channel_flag_helper(self, args, msg):
        """
        A helper method that bundles together command functions around the --channel flag
        :param args: the arguments object
        :param msg: the message object
        :return success: dict {"status": True, "channel": channel_id, "args": args}
        :return error: dict {"status": False, "msg": error_message}
        """
        # Parse the song and channel out of the user's input
        result = self.voice_channel_regex(args)
        if result is None:
            return {
                "status": False,
                "msg": f"❌ My magic regex failed to parse your command!\n`{msg}`",
            }

        # If the --channel flag was not provided, use the channel the user is in as the target channel
        if result["channel"] is None:
            # Get the current voice channel of the user who invoked the command
            channel_dict = self.get_voice_channel_of_a_user(
                discord_custom.guild_id(msg), discord_custom.get_user_id(msg)
            )
            # If the user is not in a voice channel, return a helpful error message
            if not channel_dict:
                return {
                    "status": False,
                    "msg": "❌ You are not in a voice channel. Use the `--channel <id>` flag or join a voice channel to use this command",
                }

            # Otherwise, set the channel to the user's current voice channel
            return {
                "status": True,
                "channel": channel_dict["channel_id"],
                "args": result["args"],
            }
        else:
            # Otherwise, set the channel to the user's input
            return {
                "status": True,
                "channel": result["channel"],
                "args": result["args"],
            }

    def voice_channel_regex(self, args):
        """
        Helper function - Regex for the cmds that use the --channel param
        Captures the args from the command args and the value of --channel if used
        :param args: The args object
        :return: A dict with "args" and "channel"
        note: The value of the channel in the dict will either be an Int or None
        note: The value of the args in the dict will either be a String or None
        :return: None if no matches were found at all
        """

        # If the --channel flag was used, check for the --channel value with different regex patterns
        if "--channel" in args:
            # First, check if the --channel flag is present at the end of the string
            # Note: Args is assumed to be a string with no spaces
            pattern = r"^(\S+)\s--channel\s(\d+)$"
            match = re.search(pattern, args)
            # If there is a match, we have the data we need and can return
            if match:
                return {
                    "args": match.group(1).strip(),
                    "channel": int(match.group(2).strip()),
                }

            # Second, check if the --channel flag is present at the end of the string
            # Note: Args in this case is assumed to be wrapped in "" (quotes) and it CAN have spaces
            pattern = r'^(".*")\s--channel\s(\d+)$'
            match = re.search(pattern, args)
            # If there is a match, we have the data we need and can return
            if match:
                return {
                    "args": match.group(1).strip(),
                    "channel": int(match.group(2).strip()),
                }

            # Third, check if the --channel flag is present at the beginning of the string instead of at the end
            # Note: Args is assumed to be a string with no spaces
            pattern = r"^--channel\s(\d+)\s(\S+)$"
            match = re.search(pattern, args)
            # If there is a match, we have the data we need and can return
            if match:
                return {
                    "args": match.group(2).strip(),
                    "channel": int(match.group(1).strip()),
                }

            # Fourth, check if the --channel flag is present at the beginning of the string instead of at the end
            # Note: Args in this case is assumed to be wrapped in "" (quotes) and it CAN have spaces
            pattern = r'^--channel\s(\d+)\s(".*")$'
            match = re.search(pattern, args)
            # If there is a match, we have the data we need and can return
            if match:
                return {
                    "args": match.group(2).strip(),
                    "channel": int(match.group(1).strip()),
                }

            # Fifth, check if the --channel flag is the ONLY thing present in the args
            pattern = r"^--channel\s(\d+)$"
            match = re.search(pattern, args)
            # If there is a match, we have the data we need and can return
            if match:
                return {"args": None, "channel": int(match.group(1).strip())}

        # If the --channel flag was not used, we return the raw args
        else:
            return {
                "args": args.strip(),
                "channel": None,
            }

        # If there is still no match, return None
        return None

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
        try:
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
        except CancelledError:
            await vc.disconnect()

    async def __send_file_runner(self, channel_id, file, content=None):
        """
        The runner for sending a file to a Discord channel
        """
        # Get the channel object from the ID
        channel = self.bot.client.get_channel(channel_id)

        # If the content is not None, send it as a message attached with the file
        if content:
            result = await channel.send(content, file=discord.File(file))
        # Otherwise, just send the file
        else:
            result = await channel.send(file=discord.File(file))

        # TEMP testing if a message was properly sent
        if len(result.attachments) > 0:
            return True
        else:
            raise Exception("Failed to send file")
