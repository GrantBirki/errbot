import re
from string import Template

import requests
from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.common.errhelper import ErrHelper

chatutils = ChatUtils()


class Eft(BotPlugin):
    """Escape From Tarkov plugin for Errbot - Cheeki Breeki!"""

    @botcmd
    def eft(self, msg, args):
        """
        Get the price of an item from Escape From Tarkov.

        Syntax: .eft <item name>
        Example: .eft gas an -> will get the price of a Gas Analyzer
        """
        ErrHelper().user(msg)

        # Set the type of args to a string
        args = str(args).strip()

        # Validate the input
        if not self.input_validation(args):
            self.general_error(msg, "Invalid input. Please try again.")
            return

        # Execute the graphql query to try and get eft item data
        result = self.graph_ql(self.item_query(args))

        # If the result is false, then the request failed
        if not result:
            self.general_error(
                msg,
                "During the request, the Tarkov API returned an error. Please check the logs.",
            )
            return

        # Get the first result from the query
        try:
            result_data = result["data"]["itemsByName"][0]
        except IndexError:
            self.general_error(msg, "The item you requested was not found.")
            return

        # Format the types to be wrapped in backticks to look pretty
        types = self.fmt_item_types(result_data)

        # Get the highest trader price and the trader name
        highest_price, trader = self.get_highest_trader_price(result_data)

        # Get item 'tier'
        item_tier = self.get_item_tier(highest_price, result_data)

        # Send a successful card with the eft item data
        body = ""
        body += f"**Price and Item Details:**\n"
        body += f"• Wiki: {result_data['link']}\n"
        body += f"• Item Tier: {item_tier['msg']}\n"
        body += f"• Sell to: `{trader}` for `{self.fmt_number(highest_price)}`\n"

        # Get Average Flea Price
        flea_price = self.fmt_number(result_data["avg24hPrice"])
        if flea_price == 0 or flea_price == "0":
            flea_price = "N/A"

        # Send a successful card with the eft item data
        self.send_card(
            title=result_data["name"],
            body=body,
            color=item_tier["color"],
            in_reply_to=msg,
            thumbnail=result_data["iconLink"],
            fields=(
                ("Avg Flea Price:", flea_price),
                ("Base Price:", self.fmt_number(result_data["basePrice"])),
                (
                    "Change Last 48h:",
                    self.get_price_change(result_data["changeLast48hPercent"]),
                ),
                ("Price Per Grid:", item_tier["price_per_grid"]),
                ("Item Types:", types),
            ),
        )
        return

    def get_item_tier(self, highest_price, result_data):
        """
        Get the 'tier' of the item (color and tier)
        :param highest_price: The highest price (int) the item sells for
        :return: A dict of the item tier data
        """

        # Calculate the price per grid unit
        try:
            price_per_grid = int(highest_price) / (
                int(result_data["width"]) * int(result_data["height"])
            )

            if price_per_grid >= 25000:
                color = chatutils.color("yellow")
                tier_msg = "⭐ Legendary ⭐"
            elif price_per_grid >= 12500:
                color = chatutils.color("green")
                tier_msg = "🟢 Great"
            elif price_per_grid >= 8000:
                color = chatutils.color("blue")
                tier_msg = "🔵 Average"
            else:
                color = chatutils.color("red")
                tier_msg = "🔴 Poor"

            price_per_grid = self.fmt_number(price_per_grid)
        except ZeroDivisionError:
            color = chatutils.color("white")
            tier_msg = "❓ N/A"
            price_per_grid = "N/A"

        return {
            "color": color,
            "price_per_grid": price_per_grid,
            "msg": tier_msg,
        }

    def get_highest_trader_price(self, result_data):
        """
        Helper function for getting the highest trader price.
        :param result_data: The result of the graphql query
        :return: The highest trader price (int) and the trader name (string)
        """
        highest_price = 0
        trader = ""
        for price in result_data["sellFor"]:
            if price["price"] > highest_price:
                highest_price = int(price["price"])
                trader = str(price["source"])
        return highest_price, trader

    def fmt_number(self, number):
        """
        Helper function to format a number to a string with commas.
        :param number: The number to format (int)
        :return: The formatted number (string)
        """
        return "{:,}".format(number)

    def get_price_change(self, price_change):
        """
        Helper function for formatting the price change.
        :param price_change: The price change (float)
        :return: The formatted price change (string)
        """
        if not price_change:
            return "N/A"

        if price_change > 0:
            return f"{price_change}% 📈"
        elif price_change < 0:
            return f"{price_change}% 📉"
        else:
            return "0%"

    def input_validation(self, args):
        """
        Helper function for validating the user input.
        :param args: The user input (string)
        :return: True if the input is valid, False if not
        """
        # Character Allow List
        regex = r"^[a-zA-Z\d\s-]+$"

        # If there is a match the input is valid and we can return true
        if re.match(regex, args):
            return True
        # If there is no match, the input is invalid and we can return false
        else:
            return False

    def graph_ql(self, query):
        """
        Helper function for executing a graphql query to the Tarkov API.

        :param query: The query to execute (string)
        :return: The result of the query (dict)
        :return: False if the request failed
        """
        response = requests.post(
            "https://tarkov-tools.com/graphql", json={"query": query}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def fmt_item_types(self, result_data):
        """
        Takes a list of eft item types and returns it as a string with backticks
        :param result_data: The result of the graphql query
        :return: The formatted types (string)
        """
        types = ""
        for type in result_data["types"]:
            types += "`" + type + "`, "
        types = types[:-2]
        return types

    def item_query(self, name):
        """
        Helper function for building the graphql query for an eft item.
        """
        query = Template(
            """
            {
                itemsByName(name: "$name") {
                    name
                    types
                    avg24hPrice
                    basePrice
                    width
                    height
                    changeLast48hPercent
                    iconLink
                    link
                    sellFor {
                        price
                        source
                    }
                }
            }
            """
        )
        return query.substitute(name=name)

    def general_error(self, src_msg, msg):
        """
        Helper function for sending a general error card.
        """
        self.send_card(
            title="Request Failed",
            body=msg,
            color=chatutils.color("red"),
            in_reply_to=src_msg,
        )
