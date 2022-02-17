import os
import json
import logging

from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import BotDataTable
from lib.common.utilities import Util

dynamo = Dynamo()
util = Util()

LOG = logging.getLogger(__name__)
BOT_NAME = os.environ["BOT_NAME"].strip()
BAN_USER_RECORD = "user-bans"
BAN_SERVER_RECORD = "server-bans"


class Ban:
    def remove_ban(self, ban, ban_type="user"):
        """
        Remove a ban from the remote state
        :param ban: The user or server to remove from the ban list
        :param ban_type: The type of ban to remove. "user" or "server"
        :return: True if successful, False if it fails
        """
        # Attempt to get the ban record
        if ban_type == "user":
            ban_record = BAN_USER_RECORD
        elif ban_type == "server":
            ban_record = BAN_SERVER_RECORD
        record = dynamo.get(BotDataTable, ban_record)

        # If the record exists, update it with the removal
        if record:
            record_parsed = json.loads(record.value)
            record_parsed.remove(ban)

            # Update the record with the latest data
            update_result = dynamo.update(
                table=BotDataTable,
                record=record,
                fields_to_update=[BotDataTable.value.set(json.dumps(record_parsed))],
            )

            # If the update was successful, return
            if update_result:
                # uncomment the line(s) below for debugging and verbosity
                LOG.info(f'Successfully removed ban for "{ban}"')
                return True
            # If the update failed due to a missing record, log the error
            elif update_result is None:
                LOG.error(f'Failed to remove ban for "{ban}" due to a missing record')
                return False
            # If the update failed, log an error and return
            elif update_result is False:
                LOG.error(f'Failed to remove ban for "{ban}"')
                return False

        # If the record doesn't exist, exit
        elif record is None:
            LOG.info(
                f'Could not remove ban for "{ban}" because the "{BAN_USER_RECORD}" record was not found"'
            )
            return False

    def add_ban(self, ban, ban_type="user"):
        """
        Ban a given user or server
        :param ban: The user or server to add to the ban list
        :param ban_type: The type of ban to remove. "user" or "server"
        :return: True if successful, False if it fails
        """
        # Attempt to get the ban record
        if ban_type == "user":
            ban_record = BAN_USER_RECORD
        elif ban_type == "server":
            ban_record = BAN_SERVER_RECORD
        record = dynamo.get(BotDataTable, ban_record)

        # If the record exists, update it with the most recent values collected
        if record:
            record_parsed = json.loads(record.value)
            record_parsed.append(ban)

            # Update the record with the latest data
            update_result = dynamo.update(
                table=BotDataTable,
                record=record,
                fields_to_update=[BotDataTable.value.set(json.dumps(record_parsed))],
            )

            # If the update was successful, return
            if update_result:
                # uncomment the line(s) below for debugging and verbosity
                LOG.info(f'Successfully updated ban record with "{ban}"')
                return True
            # If the update failed due to a missing record, log the error
            elif update_result is None:
                LOG.error(
                    f'Failed to update ban record with "{ban}" due to a missing record'
                )
                return False
            # If the update failed, log an error and return
            elif update_result is False:
                LOG.error(f'Failed to update ban record with "{ban}"')
                return False

        # If the record doesn't exist, create it
        elif record is None:
            LOG.info(
                f'BotDataTable record for "{ban_record}" was not found. Creating..."'
            )
            new_record = dynamo.write(
                BotDataTable(
                    key=ban_record,
                    value=json.dumps([ban]),
                    updated_at=util.iso_timestamp(),
                )
            )
            # If the write was successful, log and return
            if new_record:
                LOG.info(f'Created new BotDataTable record for "{ban_record}"')
                return True
            # If the write failed, log an error and return
            elif new_record is False:
                LOG.error(f'Failed to write to BotDataTable for "{ban_record}"')
                return False

    def get_bans(self, ban_type="user"):
        """
        Gets a list of all bans from the remote state (users or servers)
        :param ban_type: The type of bans to get. "user" or "server"
        :return: A list of all bans
        Note: If the record does not exist, it will be created as an empty list []
        """
        # Attempt to get the ban record
        if ban_type == "user":
            ban_record = BAN_USER_RECORD
        elif ban_type == "server":
            ban_record = BAN_SERVER_RECORD
        record = dynamo.get(BotDataTable, ban_record)

        # If the record exists, return it
        if record:
            return json.loads(record.value)

        # If the record doesn't exist, create it
        # Note: This should only ever happen once, when the ban record does not exist
        elif record is None:
            LOG.warning(
                f'BotDataTable record for "{ban_record}" was not found. Creating..."'
            )
            new_record = dynamo.write(
                BotDataTable(
                    key=ban_record,
                    value=json.dumps([]),  # create a brand new empty record
                    updated_at=util.iso_timestamp(),
                )
            )
            # If the write was successful, log and return
            if new_record:
                LOG.info(f'Created new BotDataTable record for "{ban_record}"')
                # Return the empty list as the record was just created
                return []
            # If the write failed, log an error and return
            elif new_record is False:
                LOG.error(f'Failed to write to BotDataTable for "{ban_record}"')
                return False
