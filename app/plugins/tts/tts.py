from errbot import BotPlugin, botcmd, arg_botcmd

from lib.chat.text_to_speech import TextToSpeech
from lib.common.cooldown import CoolDown
from lib.database.dynamo_tables import TtsTable
from lib.chat.discord_custom import DiscordCustom

cooldown = CoolDown(3, TtsTable)


class Tts(BotPlugin):
    """TTS plugin for Errbot"""

    @arg_botcmd("--text", dest="text", type=str, default=None)
    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def tts(self, msg, text=None, channel=None):
        """
        Play a TTS message from a string of text

        --channel <channel ID> - The full channel id to play the video/audio in
        --text "some cool text" - The text to play wrapped in quotes
        """

        allowed = cooldown.check(msg)

        if allowed:

            yield "⚙ Processing..."

            tts = TextToSpeech()
            out_file = tts.convert_to_mp3(text)

            yield f"🎵 Playing: `{out_file}`"

            dc = DiscordCustom(self._bot)
            dc.play_audio_file(channel, out_file)

        else:
            message = "Slow down!\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
