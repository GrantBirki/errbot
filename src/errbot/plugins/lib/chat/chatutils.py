import hashlib
import os
import re

COLORS = {
    "red": "#FF0000",
    "green": "#008000",
    "yellow": "#FFA500",
    "blue": "#0000FF",
    "white": "#FFFFFF",
    "cyan": "#00FFFF",
    "black": "#000000",
}

BACKEND = os.environ["BACKEND"]


class ChatUtils:
    def color(self, color):
        """
        Gets the hex of a color for send_card() calls
        """
        return COLORS[color]

    def guild_id(self, msg):
        """
        Returns the guild_id / slack server name as an int

        For discord, this is the guild_id which is an int
        For Slack, this is a pure int hash of the server name
        """
        if BACKEND == "discord":
            try:
                return int(msg.frm.room.__dict__["_guild_id"])
            except AttributeError:
                return False
        elif BACKEND == "slack":
            # Get the name of the Slack server (a string)
            server_name = str(msg.frm.room.__dict__["_bot"].__dict__["auth"]['team'])
            # Hash the severname with sha256
            hashed = hashlib.sha256(server_name.encode('utf8'))
            hashed.hexdigest()
            # Convert the hash to an int and get the first 16 digits
            unique_slack_server_hash_init = int(str(int(hashed.hexdigest(), base=16))[:16])
            return unique_slack_server_hash_init

    def channel_id(self, msg):
        """
        Returns the channel ID
        Discord will be an int while Slack will be a string
        """
        if BACKEND == "discord":
            return int(msg.frm.room.__dict__["_channel_id"])
        elif BACKEND == "slack":
            return str(msg.frm.__dict__["_channelid"])

    def handle(self, msg):
        """
        Gets the handle of a user
        This does not support mentions but is useful for getting the handle of a user

        Example: Birki#0001@bots -> Birki#0001
        Example: channel/handle -> handle
        Use mention_user to get the ID to mention a user
        """
        if BACKEND == "discord":
            return msg.frm.person.split("@")[0]
        elif BACKEND == 'slack':
            return str(msg.frm).split("/")[1]

    def mention_user(self, msg):
        """
        Gets the user's mention_id which can be used to directly mention a Discord user in chat
        Returns the the 'mention_id' with proper formatting for a mention
        """
        if BACKEND == 'discord':
            return f"<@{msg.frm.__dict__['_user_id']}>"
        elif BACKEND == 'slack':
            return msg.frm.person

    def get_user_id(self, msg):
        """
        Gets the user's raw ID and returns it
        Note: The user ID for Discord is an integer
        Example: 12345678909876543

        Note: The user ID for Slack is a string
        Example: U123456789
        """
        if BACKEND == "discord":
            try:
                return int(msg.frm.__dict__["_user_id"])
            except (ValueError, AttributeError):
                pattern = r"^<\D+(\d+)>$"
                match = re.search(pattern, msg)
                if not match:
                    raise ValueError("Could not find user ID")
                return int(match.group(1).strip())
        elif BACKEND == "slack":
            try:
                return str(msg.frm.__dict__["_userid"])
            except (ValueError, AttributeError):
                pattern = r"^.*(@\S+)$"
                match = re.search(pattern, msg)
                if not match:
                    raise ValueError("Could not find user ID")
                return str(match.group(1).strip())

    def send_card_helper(
        self,
        bot_self=None,
        to=None,
        title=None,
        body=None,
        color=None,
        in_reply_to=None,
        retries=3,
    ):
        """
        Helper function for sending a message card for the stats command
        :param bot_self: The bot object (self from the @botcmd function calling this method)
        :param to: The message to reply to (usually a Discord.Message object)
        :param title: The title of the card (string)
        :param message: The message to send (string)
        :param color: The color of the card (color object)
        :param in_reply_to: The message to reply to (usually a Discord.Message object) (if used)
        :param retries: The number of times to retry the request
        """
        for i in range(retries):
            try:
                if in_reply_to is None:
                    bot_self.send_card(
                        to=to,
                        title=title,
                        body=body,
                        color=color,
                    )
                else:
                    bot_self.send_card(
                        title=title,
                        body=body,
                        color=color,
                        in_reply_to=in_reply_to,
                    )
                return
            except TimeoutError:
                if i == retries - 1:
                    raise
