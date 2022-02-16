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

class Ban:
    def remove_user(self, user):
        """
        Remove a ban for a given user
        :param user: The handle of the user to un-ban
        :return: True if successful, False if it fails
        """
        # Attempt to get the user bans record
        record = dynamo.get(BotDataTable, BAN_USER_RECORD)

        # If the record exists, update it with the user removal
        if record:
            record_parsed = json.loads(record.value)
            record_parsed.remove(user)

            # Update the record with the latest data
            update_result = dynamo.update(
                table=BotDataTable,
                record=record,
                fields_to_update=[
                    BotDataTable.value.set(json.dumps(record_parsed))
                ],
            )

            # If the update was successful, return
            if update_result:
                # uncomment the line(s) below for debugging and verbosity
                LOG.info(
                    f'Successfully removed ban for "{user}"'
                )
                return True
            # If the update failed due to a missing record, log the error
            elif update_result is None:
                LOG.error(
                    f'Failed to remove ban for "{user}" due to a missing record'
                )
                return False
            # If the update failed, log an error and return
            elif update_result is False:
                LOG.error(f'Failed to remove ban for "{user}"')
                return False

        # If the record doesn't exist, exit
        elif record is None:
            LOG.info(
                f'Could not remove ban for "{user}" because the "{BAN_USER_RECORD}" record was not found"'
            )
            return False

    def user(self, user):
        """
        Ban a given user
        :param user: The handle of the user to ban
        :return: True if successful, False if it fails
        """
        # Attempt to get the user bans record
        record = dynamo.get(BotDataTable, BAN_USER_RECORD)

        # If the record exists, update it with the most recent values collected
        if record:
            record_parsed = json.loads(record.value)
            record_parsed.append(user)

            # Update the record with the latest data
            update_result = dynamo.update(
                table=BotDataTable,
                record=record,
                fields_to_update=[
                    BotDataTable.value.set(json.dumps(record_parsed))
                ],
            )

            # If the update was successful, return
            if update_result:
                # uncomment the line(s) below for debugging and verbosity
                LOG.info(
                    f'Successfully updated banned users record with "{user}"'
                )
                return True
            # If the update failed due to a missing record, log the error
            elif update_result is None:
                LOG.error(
                    f'Failed to update banned users record with "{user}" due to a missing record'
                )
                return False
            # If the update failed, log an error and return
            elif update_result is False:
                LOG.error(f'Failed to update banned users record with "{user}"')
                return False

        # If the record doesn't exist, create it
        elif record is None:
            LOG.info(
                f'BotDataTable record for "{BAN_USER_RECORD}" was not found. Creating..."'
            )
            new_record = dynamo.write(
                BotDataTable(
                    key=BAN_USER_RECORD,
                    value=json.dumps([user]),
                    updated_at=util.iso_timestamp(),
                )
            )
            # If the write was successful, log and return
            if new_record:
                LOG.info(f'Created new BotDataTable record for "{BAN_USER_RECORD}"')
                return True
            # If the write failed, log an error and return
            elif new_record is False:
                LOG.error(f'Failed to write to BotDataTable for "{BAN_USER_RECORD}"')
                return False

    def get_banned_users(self):
        """
        Gets a list of all banned users from the remote state
        :return: A list of all banned users

        Note: If the record does not exist, it will be created as an empty list []
        """
        # Attempt to get the user bans record
        record = dynamo.get(BotDataTable, BAN_USER_RECORD)

        # If the record exists, return it
        if record:
            return json.loads(record.value)

        # If the record doesn't exist, create it
        # Note: This should only ever happen once, when the ban record does not exist
        elif record is None:
            LOG.warning(
                f'BotDataTable record for "{BAN_USER_RECORD}" was not found. Creating..."'
            )
            new_record = dynamo.write(
                BotDataTable(
                    key=BAN_USER_RECORD,
                    value=json.dumps([]), # create a brand new empty record
                    updated_at=util.iso_timestamp(),
                )
            )
            # If the write was successful, log and return
            if new_record:
                LOG.info(f'Created new BotDataTable record for "{BAN_USER_RECORD}"')
                # Return the empty list as the record was just created
                return []
            # If the write failed, log an error and return
            elif new_record is False:
                LOG.error(f'Failed to write to BotDataTable for "{BAN_USER_RECORD}"')
                return False
