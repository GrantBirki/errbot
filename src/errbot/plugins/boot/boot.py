from errbot import BotPlugin, botcmd
import os
import requests

# Version of the message that's triggered after installing the plugin
# Incrementing this ensures the message is re-triggered, even if it had
# already been triggered in the past.
INSTALL_MESSAGE_VERSION = 1
# Message text to send to bot admins upon installing/updating plugin
INSTALL_MESSAGE_TEXT = "🟢 Systems are now online"
# Interval for pushing health checks to the status_page endpoint
INTERVAL = 15
STATUS_PUSH_ENDPOINT = os.environ.get("STATUS_PUSH_ENDPOINT", False)


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

        if not STATUS_PUSH_ENDPOINT:
            self.log.warn("STATUS_PUSH_ENDPOINT is disabled")
        else:
            self.log.info(
                f"STATUS_PUSH_ENDPOINT is configured to: {STATUS_PUSH_ENDPOINT}"
            )
            self.start_poller(INTERVAL, self.push_health_status)

    def push_health_status(self):
        requests.get(STATUS_PUSH_ENDPOINT)

    @botcmd(admin_only=True)
    def sentry(self, mess, args):
        """Get the status of the Sentry integration"""
        sentry_disabled = os.environ.get("SENTRY_DISABLED", False)
        if sentry_disabled:
            return "❌ Sentry is disabled"
        else:
            return "🟢 Sentry is enabled"
