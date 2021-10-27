from errbot import BotPlugin, botcmd
import time
from lib.chat.discord_websocket import DiscordWebSocket
import os

class Tts(BotPlugin):
    """Tts plugin for Errbot"""

    @botcmd
    def tts(self, msg, args):
        """
        Send a text to speech message
        """

        dws = DiscordWebSocket()
        dws.join_voice(873463331917299722, 873463331917299726)
        time.sleep(5)
        dws.close()

        # Return a message / output below
        return "done"
