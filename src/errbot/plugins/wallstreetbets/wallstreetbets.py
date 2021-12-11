from errbot import BotPlugin, botcmd
import requests


class Wallstreetbets(BotPlugin):
    """Wallstreetbets plugin for Errbot - For getting S T O N K S"""

    @botcmd
    def wallstreetbets(self, msg, args):
        """
        Get the top stonks from Wallstreetbets and their sentiment
        """

        stonks = self.get_wallstreebets()[:5]

        message = []
        for stonk in stonks:
            message.append(
                f"Ticker: `${stonk['ticker'].ljust(4)}` | Sentiment: `{stonk['sentiment']}` | Comments: `{stonk['no_of_comments']}`"
            )

        return "\n".join(message)

    def get_wallstreebets(self):
        return requests.get("https://dashboard.nbshare.io/api/v1/apps/reddit").json()
