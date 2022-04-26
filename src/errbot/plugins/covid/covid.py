from errbot import BotPlugin, arg_botcmd
from lib.common.errhelper import ErrHelper
from lib.chat.chatutils import ChatUtils

chatutils = ChatUtils()

DATA_URL = "https://corona.dnsforfamily.com/graph.png?c="


class Covid(BotPlugin):
    """Covid plugin for Errbot"""

    @arg_botcmd("--region", dest="region", default="us", type=str)
    def covid(self, msg, region=None):
        """
        Get Covid-19 stats for a region as an image

        Usage: .covid --region <two letter region code>

        Example: .covid
        Example: .covid --region=us
        Example: .covid --region=global
        """
        ErrHelper().user(msg)

        self.send_card(
            title="COVID-19 Statistics",
            body=f"Chart for: {region}",
            image=f"{DATA_URL}{region}",
            color=chatutils.color("white"),
            in_reply_to=msg,
        )
