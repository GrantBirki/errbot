import os

from lib.chat.discord import Discord
from sentry_sdk import capture_exception, capture_message, set_user

discord = Discord()

# Check if Sentry is enabled
SENTRY_DISABLED = os.environ.get("SENTRY_DISABLED", False)


class ErrHelper:
    """
    Error handling helper class for dealing with exceptions and tracing

    This class assumes that you are using Discord as your chat client.
    If Sentry.io is successfully enabled in config.py, then this class will automatically send errors to Sentry.io. Otherwise, it will send errors to its usual logging methods.
    """

    def user(self, msg):
        """
        Set the Sentry context for a user

        Simply call Sentry().user(msg) to set the context for a user from any @botcmd function
        :param msg: The message object from the @botcmd function
        :return: None
        """
        if not SENTRY_DISABLED:
            set_user({"username": discord.handle(msg)})

    def capture(self, error):
        """
        Capture an exception
        :param error: The exception to be captured (String or Exception)
        :return: None

        Note: If Sentry.io is enabled it will be sent to Sentry, otherwise it will be logged via the usual logging methods
        """
        if not SENTRY_DISABLED:
            # If the provided message type is a string, then we'll send it to Sentry as a message
            if type(error) == str:
                capture_message(error)
            # Otherwise, we'll send it to Sentry as an exception (assumed)
            else:
                capture_exception(error)
