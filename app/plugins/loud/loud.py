import os
import random
from lib.common.cooldown import CoolDown

from errbot import BotPlugin, arg_botcmd, botcmd
from lib.chat.discord import Discord
from lib.chat.discord_custom import DiscordCustom
from lib.common.utilities import Util
from lib.common.cooldown import CoolDown
from lib.database.dynamo import LoudTable

discord = Discord()
util = Util()
cooldown = CoolDown(86400, LoudTable)

PATH = "plugins/loud/sounds"


class Load(BotPlugin):
    """Loud plugin for Errbot - Plays loud sounds"""

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    @arg_botcmd("--sound", dest="sound", type=str, default=None)
    def loud(self, msg, channel=None, sound=None):
        """
        Play an audio file from the sounds folder in a given channel
        These are insanely loud sounds which can only be played once per user per day
        📢📢📢 bye bye ears
        """

        allowed = cooldown.check(msg)

        if allowed:

            yield f"📢 LOUD Playing: `{sound}`"

            dc = DiscordCustom(self._bot)
            dc.play_audio_file(channel, f"{PATH}/{sound}")
        else:
            message = "Not playing sound! You can only use this command once per day\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def random_loud(self, msg, channel=None):
        """
        Play a random audio file from the sounds folder in a given channel
        """

        sound = random.choice(os.listdir(PATH))

        allowed = cooldown.check(msg)

        if allowed:

            yield f"📢 LOUD Playing Random Sound: `{sound}`"

            dc = DiscordCustom(self._bot)
            dc.play_audio_file(channel, f"{PATH}/{sound}")
        else:
            message = "Not playing sound! You can only use this command once per day\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
