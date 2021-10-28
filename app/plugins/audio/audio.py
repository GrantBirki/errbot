from errbot import BotPlugin, botcmd, arg_botcmd

from lib.chat.discord_custom import DiscordCustom


PATH = "plugins/audio"

class Audio(BotPlugin):
    """Audio plugin for Errbot"""

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    @arg_botcmd("--sound", dest="sound", type=str, default=None)
    def audio(self, msg, channel=None, sound=None):
        """
        Send a text to speech message
        """
        
        yield f"🎵 Playing: `{sound}`"

        dc = DiscordCustom(self._bot)
        dc.play_audio_file(channel, f"{PATH}/{sound}")
