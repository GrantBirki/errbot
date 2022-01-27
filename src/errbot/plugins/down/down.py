import os
import time

from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom
from lib.common.down_detector import DownDetector
from lib.common.errhelper import ErrHelper

chatutils = ChatUtils()
downdetector = DownDetector()


class Down(BotPlugin):
    """DownDetector plugin for Errbot"""

    @botcmd
    def down(self, msg, args):
        """
        Check the status of a game, service, or website with DownDetector

        Returns a screenshot of the DownDetector report chart

        Example: .down google
        """
        ErrHelper().user(msg)

        query = args.lower().strip()

        chart_file = downdetector.chart(query, search=True)
        if not chart_file:
            return f"❌ Failed to get chart from DownDetector for `{query}`"

        dc = DiscordCustom(self._bot)
        channel_id = chatutils.channel_id(msg)
        dc.send_file(channel_id, chart_file)
        # Remove the chart file after it has been uploaded
        time.sleep(5)
        os.remove(chart_file)
        return
