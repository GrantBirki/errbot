import os
import json

import psutil
from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom
from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import BotDataTable

from lib.common.errhelper import ErrHelper

chatutils = ChatUtils()
dynamo = Dynamo()

STATUS_PAGE_URL = os.environ.get("STATUS_PAGE_URL", False)
DOCS_URL = os.environ.get("DOCS_URL", False)
BACKEND = os.environ["BACKEND"]
BOT_NAME = os.environ["BOT_NAME"].strip()
BOT_PREFIX = os.environ.get("BOT_PREFIX", ".")


class Core(BotPlugin):  
    """Core plugins for Errbot"""

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
        """Get all the stats for the bot's command usage"""

        # Attempt to get the bot data table for this bot
        record = dynamo.get(BotDataTable, BOT_NAME)

        # If the record exists, update it with the most recent values collected
        if record:
            record_parsed = json.loads(record.command_usage_data)
        elif record is None:
            return "❌ I could not find a record for this bot in the database. Please contact the bot owner."
        elif record is False:
            return "❌ I failed to get the bot usage totals from the database for this bot. Please contact the bot owner."

        # Format the totals message
        message = f"**Command Usage Totals:**\n"
        for key, value in record_parsed.items():
            message += f"• `{BOT_PREFIX}{key}` **: {value}**\n"

        # Return a card with the totals message
        chatutils.send_card_helper(
            bot_self=self,
            title="📊 Bot Usage Totals",
            body=message,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )
