from errbot import BotPlugin, botcmd, arg_botcmd

from lib.common.youtube_dl_lib import YtdlLib

from lib.chat.discord_custom import DiscordCustom

class Play(BotPlugin):  
    """Play plugin for Errbot"""

    @arg_botcmd("--url", dest="url", type=str, default=None)
    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def play(self, msg, url=None, channel=None):  
        """
        Play a youtube video in chat!
        """

        yield "📁 Downloading started for requested url... please be patient"

        ytdl = YtdlLib()
        out_file = ytdl.download_audio(url)

        yield f"🎵 Playing: `{out_file}`"

        dc = DiscordCustom(self._bot)
        dc.play_audio_file(channel, out_file)
