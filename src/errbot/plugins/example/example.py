import os

import psutil
from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom

chatutils = ChatUtils()

STATUS_PAGE_URL = os.environ.get("STATUS_PAGE_URL", False)
DOCS_URL = os.environ.get("DOCS_URL", False)

BACKEND = os.environ["BACKEND"]

class Example(BotPlugin):
    """Example 'Hello, world!' plugin for Errbot"""

    @botcmd
    def hello(self, msg, args):
        """Say hello to the world"""
        return "hello world!"

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
    def show_args(self, msg, args):
        # How the heck do I parse args?? -> https://errbot.readthedocs.io/en/latest/user_guide/plugin_development/botcommands.html
        # Shows the args which the command was invoked with
        return f"{type(args)} | args: {args}"

    @botcmd
    def show_msg(self, msg, args):
        """
        Used for showing message attributes from Discord (gross)
        """
        # Displays msg attributes
        message = []
        message.append(f"__Checking General Message Info__")
        message.append(f"• `Type of msg`: {type(msg)}")
        message.append(f"• `msg.__dict__`: {msg.__dict__}")
        message.append(f"• `msg.frm`: {msg.frm}")
        message.append(
            f"• `msg.frm.__dict__['_user_id']`: {msg.frm.__dict__['_user_id']}"
        )
        message.append(
            f"• `type(msg.frm.__dict__['_user_id'])`: {type(msg.frm.__dict__['_user_id'])}"
        )
        message.append(f"• `msg.frm.__dict__`: {msg.frm.__dict__}")
        message.append(
            f'• `msg.frm.__dict__["_channel"]__dict__`: {msg.frm.__dict__["_channel"].__dict__}"'
        )
        message.append(f"• `msg.to`: {msg.to}")
        message.append(f"• `msg.to.__dict__`: {msg.to.__dict__}")
        message.append(f"• `msg.body`: {msg.body}")
        message.append(f"• `msg.is_direct`: {msg.is_direct}")
        message.append(f"• `msg.frm.id`: {msg.frm.id}")

        try:
            message.append(f"\n__Checking Room / Channel info from `msg`__")
            message.append(f"• `msg.frm.room.name`: {msg.frm.room.name}")
            message.append(
                f"• `msg.frm.room.id`: {msg.frm.room.id}"
            )  # same as _channel_id
            message.append(f"• `msg.frm.room`: {msg.frm.room}")
            message.append(f"• `msg.frm.room.__dict__`: {msg.frm.room.__dict__}")
            message.append(
                f"• `msg.frm.room.__dict__['_guild_id']`: {msg.frm.room.__dict__['_guild_id']}"
            )
            # yield f"• `occupants`: {msg.frm.room.occupants}" # noisy
            message.append("Room checks passed")
        except:
            message.append("Room checks failed. Are you in a room / channel?")

        message.append(f"\n__Checking Person info from `msg`__")
        message.append(f"• `msg.frm.person`: {msg.frm.person}")
        message.append(f"• `@ test`: {chatutils.mention_user(msg)}")

        message.append(f"Done! 🎉")

        return "\n".join(message)

    @botcmd
    def card(self, msg, args):
        """
        Sends a card
        Example: .card <color>
        """
        if not args:
            color = chatutils.color("white")
        else:
            color = chatutils.color(args)

        self.send_card(
            # to=self.build_identifier(f'#general@873463331917299722'),
            title="Hey!",
            body="body",
            # image='https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png',
            # link='http://www.google.com',
            color=color,
            in_reply_to=msg,
            thumbnail="https://raw.githubusercontent.com/errbotio/errbot/master/docs/_static/errbot.png",
            fields=(("field1", "field2"), ("field1", "field2")),
        )

    @botcmd
    def usertest(self, msg, args):
        """Send a message directly to a user"""
        yield f"Sending private message to: {msg.frm.person}"
        if BACKEND == "discord":
            self.send(
                self.build_identifier(chatutils.handle(msg)),
                "Boo! Bet you weren't expecting me, were you?",
            )
        elif BACKEND == "slack":
            self.send(
                self.build_identifier(msg.frm.person),
                "Boo! Bet you weren't expecting me, were you?",
            )

    @botcmd
    def version(self, msg, args):
        """Get the version (IMAGE_TAG) that this instance of errbot is running"""
        return str(os.environ["IMAGE_TAG"])

    @botcmd
    def bean(self, msg, args):
        """Example of sending a file"""
        filename = "plugins/example/bean.gif"

        # Init the DiscordCustom object
        dc = DiscordCustom(self._bot)

        # Get the channel ID from the message to send the file to
        channel_id = chatutils.channel_id(msg)

        # Send the file
        dc.send_file(channel_id, filename)

    @botcmd
    def load(self, msg, args):
        """Get the system load"""
        message = "**System load:**\n"
        cpu = f"CPU usage: {psutil.cpu_percent(4)}%\n"
        memory = f"Memory usage: {psutil.virtual_memory()[2]}%"
        return message + cpu + memory
