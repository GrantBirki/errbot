from sentry_sdk import set_user, capture_exception
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
        :param msg: The message object from the @botcmd function
        :return: None
        """
        set_user({"username": discord.handle(msg)})
    
    def capture(self, error):
        """
        Capture an exception and send it to Sentry
        :param error: The exception to be captured
        :return: None
        """
        capture_exception(error)
