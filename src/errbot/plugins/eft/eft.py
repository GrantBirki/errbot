import re
from string import Template

import requests
from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.common.errhelper import ErrHelper

chatutils = ChatUtils()

AMMO_TYPES = [
    "7.62x51mm",
    "7.62x39mm",
    "5.56x45mm",
    "5.45x39mm",
    "7.62x54mm",
    "9x39mm",
    "9x19mm",
    "9x18mm",
    "9x21mm",
    "12/70",
    "4.6x30mm",
    ".338 Lapua",
    ".300 Blackout",
    ".45 ACP",
    "5.7x28mm",
    "7.62x25mm",
    "23x75mm",
    "20/70",
    "12.7x55mm",
]


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
            self.general_error(msg, "Invalid input.", "Please check your command and try again.")
            return

        # Execute the graphql query to try and get eft item data
        result = self.graph_ql(self.item_query(args))

        # If the result is false, then the request failed
        if not result:
            self.general_error(
                msg,
                "Request Failed",
                "During the request, the Tarkov API returned an error. Please check the logs.",
            )
            return

        # Get the first result from the query
        try:
            result_data = result["data"]["itemsByName"][0]
        except IndexError:
            self.general_error(msg, "Not found", "The item you requested was not found.")
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
        if result_data["avg24hPrice"] == 0:
            flea_price = "N/A"
        else:
            flea_price = self.fmt_number(result_data["avg24hPrice"])

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

    @botcmd()
    def eft_ammo(self, msg, args):
        """
        Get information about an ammo type

        Run ".eft ammo help" to get all available ammo types

        Example: .eft ammo 556x45
        Syntax: .eft ammo <ammo_type>
        """
        # If the help command is called, show the ammo help card
        if args == "help":
            return self.ammo_help(msg)

        # Get the ammo type from the args
        ammo_type = ""
        for ammo in AMMO_TYPES:
            if ammo.lower() == args.lower().strip():
                ammo_type = ammo
                break
        if ammo_type == "":
            return self.general_error(msg, "Invalid ammo type", "You can view all ammo types with:\n`.eft ammo help`")

        # Make an API call to get all the Tarkov ammo data
        ammo_data = requests.get(
            "https://raw.githubusercontent.com/TarkovTracker/tarkovdata/master/ammunition.json"
        ).json()

        # Loop through the ammo data and find all the matching ammo types
        ammo_list = []
        for item in ammo_data.items():
            if ammo_type in item[1]["name"].lower():
                ammo_list.append(
                    {
                        "name": item[1]["shortName"],
                        "penetration": item[1]["ballistics"]["penetrationPower"],
                        "damage": item[1]["ballistics"]["damage"],
                        "armorDamage": item[1]["ballistics"]["armorDamage"],
                        "penchance": item[1]["ballistics"]["penetrationChance"],
                    }
                )

        # Sort the ammo list by highest penetration power
        ammo_list_sorted = sorted(ammo_list, key=lambda x: x['penetration'], reverse=True)

        # Format the body of the card to send with a table of ammo data
        body = "```Name         Pen  Dmg  Armor  Pen %\n"
        for ammo in ammo_list_sorted:
            name = ammo["name"]
            if len(name) > 10:
                name = name[0:10] + ".."
            body += f"{name: <12} {ammo['penetration']: <4} {ammo['damage']: <4} {ammo['armorDamage']: <6} {round(ammo['penchance'] * 100, 2)}%\n"
        body += "```"

        # Send the ammo card with the ammo data
        self.send_card(
            title=ammo_type.strip(),
            body=body.strip(),
            color=chatutils.color("white"),
            in_reply_to=msg,
            # thumbnail=result_data["iconLink"],
        )
        return

    def ammo_help(self, msg):
        """
        Show the help command to view all the available ammo types
        :param msg: The message object
        :return: None - Sends a card in reply to the message with the ammo types that can be used
        """
        # Format the body of the message with the ammo types
        body = "• " + "\n • ".join(AMMO_TYPES)
        body += "\n**Key**:"
        body += "\n• `Pen` - Penetration Power"
        body += "\n• `Dmg` - Damage"
        body += "\n• `Armor` - Armor Damage"
        body += "\n• `Pen %` - Armor Penetration Chance"

        # Send the ammo help card
        self.send_card(
            title="Available Ammo Types",
            body=body,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

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

    def general_error(self, src_msg, title, msg):
        """
        Helper function for sending a general error card.
        """
        self.send_card(
            title=title,
            body=msg,
            color=chatutils.color("red"),
            in_reply_to=src_msg,
        )
