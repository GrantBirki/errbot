from errbot import BotPlugin, botcmd

from lib.chat.discord_custom import DiscordCustom


VOICE_CHANNEL = 901023702626484255


class Tts(BotPlugin):
    """Tts plugin for Errbot"""

    @botcmd
    def tts(self, msg, args):
        """
        Send a text to speech message
        """

        dc = DiscordCustom(self._bot)

        dc.play_audio_file(VOICE_CHANNEL, "plugins/tts/gden-youre.mp3")

        return "done"
