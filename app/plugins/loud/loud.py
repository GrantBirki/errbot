import os
import random

from errbot import BotPlugin, botcmd
from lib.chat.discord import Discord
from lib.chat.discord_custom import DiscordCustom
from lib.common.cooldown import CoolDown
from lib.common.utilities import Util
from lib.database.dynamo_tables import LoudTable

discord = Discord()
util = Util()
cooldown = CoolDown(21600, LoudTable)

PATH = "plugins/loud/sounds"


class Load(BotPlugin):
    """Loud plugin for Errbot - Plays loud sounds"""

    @botcmd
    def loud(self, msg, args):
        """
        Play an audio file from the sounds folder in a given channel
        These are insanely loud sounds
        📢📢📢 bye bye ears
        """

        allowed = cooldown.check(msg)

        if allowed:

            # Initialize the Discord client
            dc = DiscordCustom(self._bot)

            # Parse the song and channel out of the user's input
            result = dc.voice_channel_regex(args)
            if result is None:
                yield f"❌ My magic regex failed to parse your command!\n`{msg}`"
                return
            sound = result["args"]
            channel = result["channel"]

            # Check if the requested file exists
            if not os.path.isfile(f"{PATH}/{sound}"):
                yield f"❌ I couldn't find the requested sound file!\n`{sound}`"
                return

            # If the --channel flag was not provided, use the channel the user is in as the .loud target channel
            if channel is None:
                # Get the current voice channel of the user who invoked the command
                channel_dict = dc.get_voice_channel_of_a_user(
                    discord.guild_id(msg), discord.get_user_id(msg)
                )
                # If the user is not in a voice channel, return a helpful error message
                if not channel_dict:
                    yield "❌ You are not in a voice channel. Use the --channel <id> flag or join a voice channel to use this command"
                    return
                channel = channel_dict["channel_id"]

            yield f"📢 LOUD Playing: `{sound}`"
            dc.play_audio_file(channel, f"{PATH}/{sound}", preserve_file=True)
            return
        else:
            message = "Not playing sound! You can use this command again when your cooldown expires.\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
            return

    @botcmd
    def loud_random(self, msg, args):
        """
        Play a random audio file from the sounds folder in a given channel
        """

        allowed = cooldown.check(msg)

        if allowed:

            # Initialize the Discord client
            dc = DiscordCustom(self._bot)

            # Parse the song and channel out of the user's input
            result = dc.voice_channel_regex(args)
            if result is None:
                yield f"❌ My magic regex failed to parse your command!\n`{msg}`"
                return
            channel = result["channel"]
            sound = random.choice(os.listdir(PATH))

            # If the --channel flag was not provided, use the channel the user is in as the .loud target channel
            if channel is None:
                # Get the current voice channel of the user who invoked the command
                channel_dict = dc.get_voice_channel_of_a_user(
                    discord.guild_id(msg), discord.get_user_id(msg)
                )
                # If the user is not in a voice channel, return a helpful error message
                if not channel_dict:
                    yield "❌ You are not in a voice channel. Use the --channel <id> flag or join a voice channel to use this command"
                    return
                channel = channel_dict["channel_id"]

            yield f"📢 LOUD Playing Random Sound: `{sound}`"
            dc.play_audio_file(channel, f"{PATH}/{sound}", preserve_file=True)
            return
        else:
            message = "Not playing sound! You can only use this command once per day\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
            return
