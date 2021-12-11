from errbot import BotPlugin, botcmd
import requests

from lib.chat.discord import Discord

discord = Discord()


class Insult(BotPlugin):
    """
    Insult plugin for Errbot

    Insult yourself or friends!
    """

    @botcmd
    def insult(self, msg, args):
        """
        Insult a specifc user
        Example: .insult @user
        """

        if args == "me":
            user = discord.mention_user(msg)
        else:
            user = args

        return f"{user} {self.get_insult()}"

    def get_insult(self):
        return requests.get(
            "https://evilinsult.com/generate_insult.php?lang=en&type=json"
        ).json()["insult"]
