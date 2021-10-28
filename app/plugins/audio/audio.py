from errbot import BotPlugin, botcmd, arg_botcmd

from lib.chat.discord_custom import DiscordCustom

import os, random

PATH = "plugins/audio/sounds"


class Audio(BotPlugin):
    """Audio plugin for Errbot"""

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    @arg_botcmd("--sound", dest="sound", type=str, default=None)
    def audio(self, msg, channel=None, sound=None):
        """
        Play an audio file from the sounds folder in a given channel
        """

        yield f"🎵 Playing: `{sound}`"

        dc = DiscordCustom(self._bot)
        dc.play_audio_file(channel, f"{PATH}/{sound}")

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def random_audio(self, msg, channel=None):
        """
        Play a random audio file from the sounds folder in a given channel
        """

        sound = random.choice(os.listdir("plugins/audio/sounds"))

        yield f"🎵 Playing Random Sound: `{sound}`"

        dc = DiscordCustom(self._bot)
        dc.play_audio_file(channel, f"{PATH}/{sound}")
