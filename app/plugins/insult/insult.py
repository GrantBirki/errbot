from errbot import BotPlugin, botcmd
import requests

class Insult(BotPlugin):
    """Insult plugin for Errbot"""

    @botcmd
    def insult_me(self, msg, args):
        """
        Get insulted to reset your confidence
        """
        return requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json').json()['insult']
