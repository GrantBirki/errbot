from errbot import BotPlugin, botcmd
import os

# Version of the message that's triggered after installing the plugin
# Incrementing this ensures the message is re-triggered, even if it had
# already been triggered in the past.
INSTALL_MESSAGE_VERSION = 1
# Message text to send to bot admins upon installing/updating plugin
INSTALL_MESSAGE_TEXT = "🟢 Systems are now online"


class Boot(BotPlugin):
    """Boot file for starting the chatbot and sending a status message to admins"""

    def activate(self):
        super(Boot, self).activate()
        if (
            not "INSTALL_MESSAGE_VERSION" in self.keys()
            or self["INSTALL_MESSAGE_VERSION"] < INSTALL_MESSAGE_VERSION
        ):
            self.warn_admins(INSTALL_MESSAGE_TEXT)
            self["INSTALL_MESSAGE_VERSION"] = INSTALL_MESSAGE_VERSION

    @botcmd(admin_only=True)
    def sentry(self, mess, args):
        """Get the status of the Sentry integration"""
        sentry_enabled = os.environ.get('SENTRY_DISABLED', False)
        if sentry_enabled:
            return "🟢 Sentry is enabled"
        else:
            return "❌ Sentry is disabled"
