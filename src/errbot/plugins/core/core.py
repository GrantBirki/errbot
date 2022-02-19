import os
import json

import psutil
from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom
from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import BotDataTable
from lib.common.ban import Ban

chatutils = ChatUtils()
dynamo = Dynamo()

STATUS_PAGE_URL = os.environ.get("STATUS_PAGE_URL", False)
DOCS_URL = os.environ.get("DOCS_URL", False)
BOT_NAME = os.environ["BOT_NAME"].strip()
BOT_PREFIX = os.environ.get("BOT_PREFIX", ".")


class Core(BotPlugin):
    """Core plugins for Errbot that return information, stats, and other useful info about the bot"""

    @botcmd
    def version(self, msg, args):
        """Get the version (IMAGE_TAG) that this instance of errbot is running"""
        return str(os.environ["IMAGE_TAG"])

    @botcmd
    def docs(self, msg, args):
        """View the public errbot docs"""
        if DOCS_URL:
            message = f"📚 View my public documentation\n{DOCS_URL}"
        else:
            message = "I don't have a public documentation URL set!"
        return message

    @botcmd
    def ping(self, msg, args):
        """Check if the bot is up"""
        if STATUS_PAGE_URL:
            message = f"🟢 Pong!\nBot status:\n{STATUS_PAGE_URL}"
        else:
            message = "🟢 Pong!"
        return message

    @botcmd
    def load(self, msg, args):
        """Get the system load"""
        message = "**System load:**\n"
        cpu = f"CPU usage: {psutil.cpu_percent(4)}%\n"
        memory = f"Memory usage: {psutil.virtual_memory()[2]}%"
        return message + cpu + memory

    @botcmd
    def stats(self, msg, args):
        """Get all the stats for the bot's command usage and total servers"""

        # Attempt to get the bot data table for this bot
        record = dynamo.get(BotDataTable, BOT_NAME)

        # If the record exists, update it with the most recent values collected
        if record:
            record_parsed = json.loads(record.value)
        elif record is None:
            return "❌ I could not find a record for this bot in the database. Please contact the bot owner."
        elif record is False:
            return "❌ I failed to get the bot usage totals from the database for this bot. Please contact the bot owner."

        # Initialize the custom Discord client to get the server count
        dc = DiscordCustom(self._bot)

        # Format the totals message
        message = f"**Total Servers: {dc.total_servers()}**\n\n"
        message += f"**Command Usage Totals:**\n\n"

        # Loop through the sorted command usage totals and append to the message variable
        for key, value in sorted(
            record_parsed.items(), key=lambda x: x[1], reverse=True
        ):
            message += f"• `{BOT_PREFIX}{key}` **: {value}**\n"

        # Return a card with the totals message
        chatutils.send_card_helper(
            bot_self=self,
            title="📊 Bot Usage Totals",
            body=message,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

    @botcmd()
    def users(self, msg, args):
        """
        Get the total number of users in all servers the bot is connected to
        """
        # Check to ensure the user is an admin
        if not chatutils.is_admin(msg):
            return "This command is only available to bot admins."
        dc = DiscordCustom(self._bot)
        return f"**Total Users: {dc.total_users()}**"

    @botcmd()
    def servers(self, msg, args):
        """
        Get the total servers the bot is in with details
        :admin only:
        """
        # Check to ensure the user is an admin
        if not chatutils.is_admin(msg):
            yield "This command is only available to bot admins."
            return

        dc = DiscordCustom(self._bot)
        servers = dc.active_servers()

        message = "📊 Active Server Information\n\n"
        message += f"**Active Servers: {len(servers)}**\n\n"

        count = 0
        for server in servers:
            message += f"• **{server['name']}**\n"
            message += f"  - ID: `{server['id']}`\n"
            message += f"  - Owner: `{server['owner']}`\n"
            message += f"  - Member count: `{server['member_count']}`\n"
            message += "\n"
            if count >= 25:
                yield message
                message = ""
                count = 0
            count += 1

        yield message
        return

    @botcmd
    def unban(self, msg, args):
        """
        Admin command for unbanning users
        Example: .unban user#1234
        """
        # Check to ensure the user is an admin
        if not chatutils.is_admin(msg):
            return "This command is only available to bot admins."

        # If the user is not already banned, return
        if args not in self._bot.banned_users:
            return f"ℹ️ User: `{args}` is **not** banned. Nothing to do..."

        # Remove the banned user from the ban list in memory
        self._bot.banned_users.remove(args)

        # Remove the user from the ban database so it persists across restarts
        result = Ban().remove_ban(args, ban_type="user")

        # Return a message based on the result of the database update
        if result:
            return f"✅ User: `{args}` has been **removed** from the ban list"
        else:
            return f"❌ Failed to remove user: `{args}` from the ban list\n🗒️Check the logs for more info"

    @botcmd
    def ban(self, msg, args):
        """
        Admin command for banning users globally from using the bot
        Example: .ban user#1234
        """
        # Check to ensure the user is an admin
        if not chatutils.is_admin(msg):
            return "This command is only available to bot admins."

        # If the user is already banned, return
        if args in self._bot.banned_users:
            return f"ℹ️ User: `{args}` is already banned"

        # If the user is not already banned, add them to the ban list in memory
        self._bot.banned_users.append(args)

        # Update the database with the new user ban so it persists across restarts
        result = Ban().add_ban(args, ban_type="user")

        # Return a message based on the result of the database update
        if result:
            return f"⛔ User: `{args}` has been **banned**"
        else:
            return f"❌ Failed to ban user: `{args}`\n🗒️Check the logs for more info"

    @botcmd
    def banned_users(self, msg, args):
        """
        Admin command for listing all banned users
        """
        if not chatutils.is_admin(msg):
            return "This command is only available to bot admins."

        banned_users_list = self._bot.banned_users
        message = f"**Banned Users: {len(banned_users_list)}**\n\n"
        for user in banned_users_list:
            message += f"• `{user}`\n"

        chatutils.send_card_helper(
            bot_self=self,
            title="⛔ Banned Users",
            body=message,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

    @botcmd
    def unban_server(self, msg, args):
        """
        Admin command for unbanning servers
        Example: .unban server 1234567890
        Note: This is not tested with Slack
        """
        # Check to ensure the server is an admin
        if not chatutils.is_admin(msg):
            return "This command is only available to bot admins."

        # If the server not already banned, return
        if args not in self._bot.banned_servers:
            return f"ℹ️ Server: `{args}` is **not** banned. Nothing to do..."

        # Remove the banned server from the ban list in memory
        self._bot.banned_servers.remove(args)

        # Remove the server from the ban database so it persists across restarts
        result = Ban().remove_ban(args, ban_type="server")

        # Return a message based on the result of the database update
        if result:
            return f"✅ Server: `{args}` has been **removed** from the ban list"
        else:
            return f"❌ Failed to remove server: `{args}` from the ban list\n🗒️Check the logs for more info"

    @botcmd
    def ban_server(self, msg, args):
        """
        Admin command for banning servers globally from using the bot
        Example: .ban 1234567890
        """
        # Check to ensure the server is an admin
        if not chatutils.is_admin(msg):
            return "This command is only available to bot admins."

        # If the server is already banned, return
        if args in self._bot.banned_servers:
            return f"ℹ️ Server: `{args}` is already banned"

        # If the server is not already banned, add them to the ban list in memory
        self._bot.banned_servers.append(args)

        # Update the database with the new server ban so it persists across restarts
        result = Ban().add_ban(args, ban_type="server")

        # Return a message based on the result of the database update
        if result:
            return f"⛔ Server: `{args}` has been **banned**"
        else:
            return f"❌ Failed to ban server: `{args}`\n🗒️Check the logs for more info"

    @botcmd
    def banned_servers(self, msg, args):
        """
        Admin command for listing all banned servers
        """
        if not chatutils.is_admin(msg):
            return "This command is only available to bot admins."

        banned_servers_list = self._bot.banned_servers
        message = f"**Banned Servers: {len(banned_servers_list)}**\n\n"
        for server in banned_servers_list:
            message += f"• `{server}`\n"

        chatutils.send_card_helper(
            bot_self=self,
            title="⛔ Banned Servers",
            body=message,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )
