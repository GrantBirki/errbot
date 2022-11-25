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

# Get the bot admins and strip out any '@' symbols
BOT_ADMINS = [x.strip("@") for x in os.environ["BOT_ADMINS"].split(",")]

# Get the allow listed servers for the Discord server lock
server_lock_env = os.environ.get("SERVER_LOCK_ALLOW_LIST", None)
if server_lock_env is not None:
    SERVER_LOCK_ALLOW_LIST = server_lock_env.split(",")
else:
    SERVER_LOCK_ALLOW_LIST = None


class ChatUtils:
    def color(self, color):
        """
        Gets the hex of a color for send_card() calls
        :param color: The color to get the hex of (red, green, yellow, blue, white, cyan, black)
        :return: The hex of the color
        """
        return COLORS[color]

    def is_admin(self, msg):
        """
        Checks if a given user is a BOT_ADMIN
        :param msg: The message object
        :return: True if the user is an admin, False otherwise
        """
        if self.handle(msg) in BOT_ADMINS:
            return True
        else:
            return False

    def guild_id(self, msg):
        """
        Gets the guild ID of a message
        :param msg: The message object
        :return: the guild_id / slack server name (Int)

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
            server_name = str(msg.frm.room.__dict__["_bot"].__dict__["auth"]["team"])
            # Hash the severname with sha256
            hashed = hashlib.sha256(server_name.encode("utf8"))
            hashed.hexdigest()
            # Convert the hash to an int and get the first 16 digits
            unique_slack_server_hash_init = int(
                str(int(hashed.hexdigest(), base=16))[:16]
            )
            return unique_slack_server_hash_init

    def channel_id(self, msg):
        """
        Gets the channel ID of a message
        :param msg: The message object
        :return: the Discord channel_id (Int) / slack channel id (String)
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
        :param msg: The message object
        :return: The handle of the user (String)

        Example: Birki#0001@bots -> Birki#0001
        Example: channel/handle -> handle
        Use mention_user to get the ID to mention a user
        """
        if BACKEND == "discord":
            return msg.frm.person.split("@")[0]
        elif BACKEND == "slack":
            return str(msg.frm).split("/")[1]

    def mention_user(self, msg):
        """
        Gets the user's mention_id which can be used to directly mention a Discord user in chat
        :param msg: The message object
        :return: the the 'mention_id' with proper formatting for a mention (String)
        """
        if BACKEND == "discord":
            return f"<@{msg.frm.__dict__['_user_id']}>"
        elif BACKEND == "slack":
            return msg.frm.person

    def get_user_id(self, msg):
        """
        Gets the user's raw ID and returns it
        :param msg: The message object
        :return: the user's Discord ID (Int) / Slack ID (String)

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

    def locked(self, msg, bot_self):
        """
        Used to lock a bot command behind the SERVER_LOCK_ALLOW_LIST
        All commands that invoke this function (at the top of the bot command) will prevent execution of the bot funct...
        ion unless the server is in the SERVER_LOCK_ALLOW_LIST

        Note: This function currently only works for Discord

        :param msg: The message object
        :return: True if the server is not in the SERVER_LOCK_ALLOW_LIST otherwise, False

        Note: Chat functions should immediately exit if this function returns true meaning that it is locked
        """
        try:
            # If the SERVER_LOCK_ALLOW_LIST env is not set, lock the command by default
            if SERVER_LOCK_ALLOW_LIST is None:
                self.locked_message(msg, bot_self)
                return True
            # If the SERVER_LOCK_ALLOW_LIST is set to "disabled", unlock all the command locks
            elif "disabled" in SERVER_LOCK_ALLOW_LIST:
                return False

            # Only execute if the backend is discord
            if BACKEND == "discord":
                # If the server id 'is not' in the allow list, return True because it is locked
                if str(self.guild_id(msg)) not in SERVER_LOCK_ALLOW_LIST:
                    self.locked_message(msg, bot_self)
                    return True
                # If the servier id 'is' in the allow list, return False because it is unlocked
                else:
                    return False
            # If the backend is not discord, return True to lock by default
            else:
                self.locked_message(msg, bot_self)
                return True
        except:
            # Catch all exceptions and return True to lock by default
            self.locked_message(msg, bot_self)
            return True

    def locked_message(self, msg, bot_self):
        return self.send_card_helper(
            bot_self=bot_self,
            title="🔒 Command Locked",
            body="This command is locked and not publicly available",
            color=self.color("red"),
            in_reply_to=msg,
        )

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
        :return: None
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
