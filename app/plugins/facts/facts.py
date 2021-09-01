from errbot import BotPlugin, botcmd
import requests

class Facts(BotPlugin):
    """Facts plugin for Errbot"""

    @botcmd
    def random_fact(self, msg, args):
        """
        Get a random fact!
        """
        return self.get_random_fact()

    def get_random_fact(self):
        """
        Get a random fact from the file
        """
        return requests.get('https://uselessfacts.jsph.pl/random.json?language=en').json()['text']
