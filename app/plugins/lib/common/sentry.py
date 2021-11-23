from sentry_sdk import set_user
from lib.chat.discord import Discord

discord = Discord()


class Sentry:
    """
    Sentry helper class for dealing with exceptions and tracing
    """

    def user(self, msg):
        """
        Set the Sentry context for a user

        Simply call Sentry().user(msg) to set the context for a user from any @botcmd function
        """
        set_user({"username": discord.handle(msg)})
