import requests
from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils

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

        # Send a successful card with the eft item data
        self.send_card(
            title=result_data["name"],
            body="Price and Item Details:",
            link=result_data["link"],
            color=chatutils.color("white"),
            in_reply_to=msg,
            thumbnail=result_data["iconLink"],
            fields=(
                ("Avg. 24h Price:", result_data["avg24hPrice"]),
                ("Base Price:", result_data["basePrice"]),
                ("Change Last 48h:", result_data["changeLast48hPercent"]),
                ("Types:", types),
            ),
        )

        return

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

    def item_query(self, args):
        """
        Helper function for building the graphql query for an eft item.
        """
        query = """
            {
                itemsByName(name: "{}") {
                    name
                    types
                    avg24hPrice
                    basePrice
                    changeLast48hPercent
                    iconLink
                    link
                }
            }
            """.format(
            args
        )
        return query

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
