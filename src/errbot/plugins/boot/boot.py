import json
import os
import time
from collections import Counter

import requests
from errbot import BotPlugin, botcmd
from lib.common.utilities import Util
from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import BotDataTable
from lib.common.ban import Ban

dynamo = Dynamo()
util = Util()

# Version of the message that's triggered after installing the plugin
# Incrementing this ensures the message is re-triggered, even if it had
# already been triggered in the past.
INSTALL_MESSAGE_VERSION = 1
# Message text to send to bot admins upon installing/updating plugin
INSTALL_MESSAGE_TEXT = "🟢 Systems are now online"
# Interval for pushing health checks to the status_page endpoint
STATUS_INTERVAL = 15
# Interval for the command usage publish cron
REMOTE_SYNC_INTERVAL = 120  # seconds
STATUS_PUSH_ENDPOINT = os.environ.get("STATUS_PUSH_ENDPOINT", False)
STATUS_PUSH_ENDPOINT_FAILURE_RETRY = 15  # seconds
BOT_NAME = os.environ["BOT_NAME"].strip()


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
            self.start_poller(STATUS_INTERVAL, self.push_health_status)

        # Run a remote_sync on startup
        # Note: We won't publish usage data on startup, as we will wait for that to collect
        self.remote_sync(retries=10, usage_publish=False)

        # Start the remote_sync cron
        self.start_poller(REMOTE_SYNC_INTERVAL, self.remote_sync)

    def remote_sync(self, retries=3, usage_publish=True):
        self.sync_ban_list(retries=retries)
        if usage_publish:
            self.publish_command_usage_data()

    def sync_ban_list(self, retries=3):
        """
        Ensures the ban lists are in sync with the remote state in DynamoDB
        """
        # Attempt to get the ban list from the remote state with retries
        for i in range(retries):
            # Get the ban list
            remote_ban_list = Ban().get_banned_users()
            if remote_ban_list or remote_ban_list == []:
                # If we got the ban list, break out of the loop
                break
            # If the ban list is None or False, something went wrong
            else:
                # If we are out of retries, log an error and exit
                if i == retries - 1:
                    self.log.error(
                        "Failed to get remote ban list after {} retries".format(retries)
                    )
                    return
                # If we are not out of retries, sleep and try again
                time.sleep(0.5)

        # Check if the ban list from the remote state is different from the local state
        local_ban_list = self._bot.banned_users
        if sorted(local_ban_list) == sorted(remote_ban_list):
            # uncomment this to debug or for extra verbosity
            # self.log.info(
            #     f"Ban lists are in sync with remote state in DynamoDB for {BOT_NAME}"
            # )
            return
        else:
            self._bot.banned_users = remote_ban_list
            self.log.info("Ban list has been synced with remote state")
            return

    def publish_command_usage_data(self):
        """
        Runs inside of the remote_sync cron to publish command usage data DynamoDB
        """
        # Grab the current command counter dictionary
        command_usage_data_snapshot = self._bot.command_usage_data
        # Reset the global command counter
        self._bot.command_usage_data = {}

        # If the command counter dict is empty, don't do anything
        if not command_usage_data_snapshot:
            # uncomment the line(s) below for debugging and verbosity
            # self.log.info(f"command_counter dict is empty, not publishing")
            return

        # Attempt to get the bot data table for this bot
        record = dynamo.get(BotDataTable, BOT_NAME)

        # If the record exists, update it with the most recent values collected
        if record:
            record_parsed = json.loads(record.value)
            updated_usage_data = dict(
                Counter(record_parsed) + Counter(command_usage_data_snapshot)
            )

            # Update the record with the updated usage data
            update_result = dynamo.update(
                table=BotDataTable,
                record=record,
                fields_to_update=[
                    BotDataTable.value.set(json.dumps(updated_usage_data))
                ],
            )

            # If the update was successful, return
            if update_result:
                # uncomment the line(s) below for debugging and verbosity
                # self.log.info(
                #     f"Successfully published command usage data for {BOT_NAME}"
                # )
                return
            # If the update failed due to a missing record, log the error
            elif update_result is None:
                self.log.error(
                    f'Failed to update BotDataTable due to a DoesNotExist exception from DynamoDB for "{BOT_NAME}"'
                )
                return
            # If the update failed, log an error and return
            elif update_result is False:
                self.log.error(f'Failed to update BotDataTable for "{BOT_NAME}"')
                return

        # If the record doesn't exist, create it
        elif record is None:
            self.log.info(
                f'BotDataTable record for "{BOT_NAME}" was not found. Creating..."'
            )
            new_record = dynamo.write(
                BotDataTable(
                    key=BOT_NAME,
                    value=json.dumps(command_usage_data_snapshot),
                    updated_at=util.iso_timestamp(),
                )
            )
            # If the write was successful, log and return
            if new_record:
                self.log.info(f'Created new BotDataTable record for "{BOT_NAME}"')
                return
            # If the write failed, log an error and return
            elif new_record is False:
                self.log.error(f'Failed to write to BotDataTable for "{BOT_NAME}"')
                return

    def push_health_status(self):
        try:
            requests.get(STATUS_PUSH_ENDPOINT)
        # If we get a ConnectionError, retry once more before raising an exception
        except Exception as e:
            # Log a warning
            self.log.warn(
                f"Could not reach status_page endpoint - {e} - trying again in {STATUS_PUSH_ENDPOINT_FAILURE_RETRY} seconds"
            )
            # Sleep for the retry interval
            time.sleep(STATUS_PUSH_ENDPOINT_FAILURE_RETRY)
            # Make the request again - This time with no error handling to raise an exception if it fails again
            requests.get(STATUS_PUSH_ENDPOINT)

    @botcmd(admin_only=True)
    def sentry(self, mess, args):
        """
        Get the status of the Sentry integration
        Useful for checking if the ErrHelper class is using Sentry.io
        """
        sentry_disabled = os.environ.get("SENTRY_DISABLED", False)
        if sentry_disabled:
            return "❌ Sentry is disabled"
        else:
            return "🟢 Sentry is enabled"
