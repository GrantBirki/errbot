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

        Example: .loud rickroll.mp3
        """

        allowed = cooldown.check(msg)

        if allowed:

            # Initialize the Discord client
            dc = DiscordCustom(self._bot)

            # Use the channel_flag_helper to get the args and channel the user wants to play the sound in
            result = dc.channel_flag_helper(args, msg)
            if result["status"] is False:
                yield result["msg"]
                return
            else:
                channel = result["channel"]
                sound = result["args"]

            # Check if the requested file exists
            if not os.path.isfile(f"{PATH}/{sound}"):
                yield f"❌ I couldn't find the requested sound file!\n`{sound}`"
                return

            yield f"📢 LOUD Playing: `{sound}`"
            dc.play_audio_file(channel, f"{PATH}/{sound}", preserve_file=True)
            return
        else:
            message = "Not playing sound! You can use this command again when your cooldown expires.\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
            return

    @botcmd
    def loud_list(self, msg, args):
        """
        List all the files that are ready to be played with the .loud command
        """
        # Get the list of files in the sounds folder
        files = os.listdir(PATH)

        # If there are no files, return a helpful error message
        if not files:
            return "❌ There are no sounds in the sounds folder!"

        # If there are files, return a message of them
        message = "📢 LOUD Sounds:\n"
        for file in files:
            message += f"• `{file}`\n"

        return message

    @botcmd
    def loud_random(self, msg, args):
        """
        Play a random audio file from the sounds folder in a given channel
        """

        allowed = cooldown.check(msg)

        if allowed:

            # Initialize the Discord client
            dc = DiscordCustom(self._bot)

            # Use the channel_flag_helper to get the channel the user wants to play the sound in
            result = dc.channel_flag_helper(args, msg)
            if result["status"] is False:
                yield result["msg"]
                return
            else:
                channel = result["channel"]

            # Get the list of files in the sounds folder
            sound = random.choice(os.listdir(PATH))

            yield f"📢 LOUD Playing Random Sound: `{sound}`"
            dc.play_audio_file(channel, f"{PATH}/{sound}", preserve_file=True)
            return
        else:
            message = "Not playing sound! You can only use this command once per day\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
            return
