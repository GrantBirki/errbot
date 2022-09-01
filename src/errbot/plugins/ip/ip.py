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
        # If the GEOLOCATION_KEY is not set, deactivate the plugin
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

        # Make an API call to get data about the IP address
        response = requests.get(f"{BASE_URL}&ip_address={args}")

        # Handle non 200 responses
        if response.status_code == 400:
            return "❌ 400 Bad Request. Please check your input. Is that a valid public IP address?"
        elif response.status_code == 429:
            return f"⚠️ 429 Too Many Requests. Whoa slow down there! Please try again in a moment"
        elif response.status_code != 200:
            return f"❌ Error from Geolocation API - HTTP: {response.status_code}"

        # Get the data in JSON form
        data = response.json()

        # Format the message

        message = ""

        if "city" and "country" in data:
            message += f"🏙️ City: {data.get('city', None)}\n"
            message += f"🌎 Country: {data.get('country', None)}\n"

        if "longitude" in data and "latitude" in data:
            message += f"📍 Longitude: {data.get('longitude', None)} | Latitude: {data.get('latitude', None)}\n\n"

        if "security" in data:
            if "is_vpn" in data["security"]:
                message += f"🔒 Is VPN: {data['security']['is_vpn']}\n\n"

        if "connection" in data:
            connection = data["connection"]
            message += f"📡 ISP Name: {connection.get('isp_name', None)}\n"
            message += f"🛰️ ASN: {connection.get('autonomous_system_number', None)} | Name: {connection.get('autonomous_system_organization', None)}\n"

        # Format the title of the message and try to use the emoji
        title = f"🌐 IP Lookup: {args}"
        if "flag" in data:
            flag = data["flag"]
            emoji = flag.get("emoji", None)

            if emoji is None:
                title = f"🌐 IP Lookup: {args}"
            else:
                title = f"🌐 IP Lookup: {args} - {data['flag']['emoji']}"

        # Send the message
        chatutils.send_card_helper(
            bot_self=self,
            title=title,
            body=message,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )
