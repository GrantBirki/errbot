from errbot import BotPlugin, botcmd
import requests


class Crypto(BotPlugin):
    """Crypto plugin for Errbot"""

    @botcmd
    def crypto(self, msg, args):
        """
        Get crypto price for a given currency
        Example: .crypto ada
        Example: .crypto btc
        """

        value = requests.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={args}&tsyms=USD"
        ).json()["USD"]

        return f"**{args.upper()}**: ${value}"
