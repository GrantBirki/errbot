from sentry_sdk import set_user, capture_exception, capture_message
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
        :param error: The exception to be captured (String or Exception)
        :return: None
        """
        # If the provided message type is a string, then we'll send it to Sentry as a message
        if type(error) == str:
            capture_message(error)
        # Otherwise, we'll send it to Sentry as an exception (assumed)
        else:
            capture_exception(error)
