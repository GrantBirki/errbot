from errbot import BotPlugin, botcmd

from lib.chat.text_to_speech import TextToSpeech
from lib.common.cooldown import CoolDown
from lib.database.dynamo_tables import TtsTable
from lib.chat.discord_custom import DiscordCustom
from lib.chat.chatutils import ChatUtils
from lib.common.errhelper import ErrHelper

cooldown = CoolDown(3, TtsTable)
chatutils = ChatUtils()


class Tts(BotPlugin):
    """TTS plugin for Errbot"""

    @botcmd
    def tts(self, msg, args):
        """
        Play a TTS message from a string of text

        --channel <channel ID> - The full channel id to play the video/audio in
        --text "some cool text" - The text to play wrapped in quotes
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

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
                text = result["args"]

            yield "⚙ Processing..."

            tts = TextToSpeech()
            out_file = tts.convert_to_mp3(text)

            yield f"🎵 Playing: `{out_file}`"

            dc.play_audio_file(channel, out_file)

        else:
            message = "Slow down!\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
