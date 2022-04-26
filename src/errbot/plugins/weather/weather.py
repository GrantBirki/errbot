import requests
from errbot import BotPlugin, botcmd
from lib.common.errhelper import ErrHelper
from lib.chat.chatutils import ChatUtils

chatutils = ChatUtils()

WEATHER_URL = "https://goweather.herokuapp.com/weather/"


class Weather(BotPlugin):
    """Weather plugin for Errbot"""

    @botcmd
    def weather(self, msg, args):
        """
        Get the weather for a given region
        Usage: .weather <city>
        Example: .weather denver
        """
        ErrHelper().user(msg)
        region = args.strip().replace(" ", "%20")

        response = requests.get(WEATHER_URL + region)

        if response.status_code != 200:
            return f"Error: {response.status_code}"

        weather = response.json()

        message = "**Current:\n**"
        message += f"• Desc: {weather['description']}\n"
        message += f"• Temp: {self.c_to_f(weather['temperature'])} °F\n"
        message += f"• Wind: {self.km_to_mi(weather['wind'])} mph\n"

        message += "\n***Forecast:***\n"

        message += "**Tomorrow:**\n"
        message += f"• Temp: {self.c_to_f(weather['forecast'][0]['temperature'])} °F\n"
        message += f"• Wind: {self.km_to_mi(weather['forecast'][0]['wind'])} mph\n"

        message += "**Next Day:**\n"
        message += f"• Temp: {self.c_to_f(weather['forecast'][1]['temperature'])} °F\n"
        message += f"• Wind: {self.km_to_mi(weather['forecast'][1]['wind'])} mph\n"

        message += "**Next Next Day:**\n"
        message += f"• Temp: {self.c_to_f(weather['forecast'][2]['temperature'])} °F\n"
        message += f"• Wind: {self.km_to_mi(weather['forecast'][2]['wind'])} mph\n"

        self.send_card(
            title=f"Weather for {args} {self.weather_icon(weather['description'])}",
            body=message,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

    def c_to_f(self, c):
        c = int(c.split(" ")[0])
        return int(c * 9 / 5 + 32)

    def km_to_mi(self, km):
        km = int(km.split(" ")[0])
        return int(km * 0.621371)

    def weather_icon(self, desc):
        desc = desc.lower()

        if "sunny" in desc:
            return "☀️"
        if "clear" in desc:
            return "🌅"
        elif "partly cloudly" in desc:
            return "⛅"
        elif "cloudly" in desc:
            return "☁️"
        elif "rain" in desc:
            return "🌧"
