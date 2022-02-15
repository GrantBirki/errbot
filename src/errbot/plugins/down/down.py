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

        # Check to see if the message was send from a guild or a DM
        guild_id = chatutils.guild_id(msg)
        if not guild_id:
            yield "⚠️ To view DownDetector status graphs, please use this command in a channel, not a DM."
            return

        query = args.lower().strip()

        yield f"📊 Fetching chart data for `{query}`..."

        chart_file, status = downdetector.chart(query, search=True)
        if chart_file == False:
            if "bad search string" in status.lower():
                yield status
                return
            yield f"❌ Failed to get chart from DownDetector for `{query}`"
            return
        elif chart_file == None:
            yield f"🔎 No matching services found for `{query}`"
            return

        yield status

        dc = DiscordCustom(self._bot)
        channel_id = chatutils.channel_id(msg)
        dc.send_file(channel_id, chart_file)
        # Remove the chart file after it has been uploaded
        time.sleep(5)
        os.remove(chart_file)
        return
