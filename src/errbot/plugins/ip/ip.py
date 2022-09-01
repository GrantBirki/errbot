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

        if response.status_code == 400:
            return "❌ 400 Bad Request. Please check your input. Is that a valid public IP address?"
        elif response.status_code != 200:
            return f"❌ Error from Geolocation API - HTTP: {response.status_code}"

        data = response.json()

        message = f"🏙️ City: {data['city']}\n"
        message += f"🌎 Country: {data['country']}\n"
        message += (
            f"📍 Longitude: {data['longitude']} | Latitude: {data['latitude']}\n\n"
        )
        message += f"🔒 Is VPN: {data['security']['is_vpn']}\n\n"
        message += f"📡 ISP Name: {data['connection']['isp_name']}\n"
        message += f"🛰️ ASN: {data['connection']['autonomous_system_number']} | Name: {data['connection']['autonomous_system_organization']}\n"

        chatutils.send_card_helper(
            bot_self=self,
            title=f"🌐 IP Lookup: {args} - {data['flag']['emoji']}",
            body=message,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )
