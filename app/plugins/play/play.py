from errbot import BotPlugin, botcmd, arg_botcmd
import validators

from lib.common.youtube_dl_lib import YtdlLib
from lib.common.cooldown import CoolDown
from lib.database.dynamo_tables import PlayTable


from lib.chat.discord_custom import DiscordCustom

cooldown = CoolDown(10, PlayTable)


class Play(BotPlugin):
    """Play plugin for Errbot"""

    @arg_botcmd("--url", dest="url", type=str, default=None)
    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def play(self, msg, url=None, channel=None):
        """
        Play a YouTube video in chat!

        --channel <channel ID> - The full channel id to play the video/audio in
        --url <url> - The full url of the video/audio to play in chat
        """

        if not validators.url(url):
            yield "❌ Invalid URL"
            return

        if not url.startswith("https://www.youtube.com/"):
            yield "❌ I only accept URLs that start with `https://www.youtube.com/`"
            return

        allowed = cooldown.check(msg)

        if allowed:
            ytdl = YtdlLib()

            length = ytdl.video_length(url)
            if length == 0:
                yield f"❌ Cannot play a live stream from YouTube"
                return

            if length > ytdl.max_length:
                yield f"❌ Video is longer than the max accepted length: `{ytdl.max_length}` seconds"
                return

            yield "📁 Download started for requested url... please be patient"
            out_file = ytdl.download_audio(url)

            yield f"🎵 Playing: `{out_file}`"

            dc = DiscordCustom(self._bot)
            dc.play_audio_file(channel, out_file)

        else:
            message = "Slow down!\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            yield message
