from errbot import BotPlugin, botcmd
import requests


class Facts(BotPlugin):
    """Facts plugin for Errbot - Get a random fact"""

    @botcmd
    def random_fact(self, msg, args):
        """
        Get a random fact!
        """
        return requests.get(
            "https://uselessfacts.jsph.pl/random.json?language=en"
        ).json()["text"]
