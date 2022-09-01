import os

import requests

from errbot import BotPlugin, botcmd
from lib.common.errhelper import ErrHelper
from lib.chat.chatutils import ChatUtils

chatutils = ChatUtils()

GEOLOCATION_KEY = os.environ.get("GEOLOCATION_KEY", None)
BASE_URL = f"https://ipgeolocation.abstractapi.com/v1/?api_key={GEOLOCATION_KEY}"


class Ip(BotPlugin):
    """Ip plugin for Errbot"""

    def activate(self):
        """
        Activate the plugin conditionally if the GEOLOCATION_KEY is set
        """
        # If the RIOT_TOKEN is not set, deactivate the plugin
        if GEOLOCATION_KEY is None:
            self.log.warn(
                "GEOLOCATION_KEY not found in environment variables. Disabling the ip plugin."
            )
            super().deactivate()
        else:
            super().activate()

    @botcmd
    def ip(self, msg, args):
        """
        Get the geolocation of an IP address
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        response = requests.get(f"{BASE_URL}&ip_address={args}")

        # Return a message / output below
        return response.json()
