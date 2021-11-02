from errbot import BotPlugin, botcmd, arg_botcmd

from lib.common.youtube_dl_lib import YtdlLib
from lib.common.cooldown import CoolDown
from lib.database.dynamo import PlayTable


from lib.chat.discord_custom import DiscordCustom

cooldown = CoolDown(30, PlayTable)

class Play(BotPlugin):
    """Play plugin for Errbot"""

    @arg_botcmd("--url", dest="url", type=str, default=None)
    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def play(self, msg, url=None, channel=None):
        """
        Play a youtube video in chat!

        --channel <channel ID> - The full channel id to play the video/audio in
        --url <url> - The full url of the video/audio to play in chat
        """

        allowed = cooldown.check(msg)

        if allowed:

            yield "📁 Download started for requested url... please be patient"

            ytdl = YtdlLib()
            out_file = ytdl.download_audio(url)

            yield f"🎵 Playing: `{out_file}`"

            dc = DiscordCustom(self._bot)
            dc.play_audio_file(channel, out_file)

        else:
            message = "Slow down!\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message