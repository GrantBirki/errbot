from errbot import BotPlugin, botcmd
import requests
class Insult(BotPlugin):
    """Insult plugin for Errbot"""

    @botcmd
    def insult_me(self, msg, args):
        """
        Get insulted to reset your confidence
        """
        return self.insult()
    
    @botcmd
    def insult(self, msg, args):
        """
        Insult a specifc user
        Example: .insult @user
        """
        return f"{args} {self.get_insult()}"

    def get_insult(self):
        return requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json').json()['insult']
