from datetime import datetime
from lib.chat.discord import Discord
from lib.common.utilities import Util
from lib.database.dynamo import Dynamo

dynamo = Dynamo()
discord = Discord()
util = Util()

class CoolDown:
    """
    Helper class for checking / setting a cool down for a given user for a given command
    Example: You can check and set a cool down for the user "bob" if they use a command that you consider annoying and have created a cooldown for. An example of this would be the ".loud" command which can only be used once per day
    """

    def __init__(self, cooldown_in_seconds, db_table):
        """
        To init the cooldown class you need to provide the cooldown and the db table to use
        :param: cooldown_in_seconds - int - ex: 60
        :param: db_table - object - ex: LoudTable - The DB table object where dynamodb should read/write the records
        """
        self.cooldown_in_seconds = cooldown_in_seconds
        self.db_table = db_table
        self.updated_at = datetime

    def remaining(self):
        """
        Returns a formatted string of the hours, minutes, and seconds remaining on a cooldown timer
        Note: it is required to init the class first and call the .check function on the class
        """
        timestamp = util.parse_iso_timestamp(self.updated_at)
        hms = util.when_ready_timestamp(timestamp, self.cooldown_in_seconds)
        return util.fmt_hms(hms)

    def check_timestamp(self, timestamp):
        """
        Checks if the timestamp is within the cool down period
        :return: True if the timestamp is no longer on cool down. False if the timestamp is still on cooldown
        """
        timestamp = util.parse_iso_timestamp(timestamp)
        return util.is_timestamp_older_than_n_seconds(timestamp, self.cooldown_in_seconds)

    def check(self, msg):
        """
        Checks the cooldown for a user given a specific command / DB table
        :return first: True if the user is on a cooldown timer, False if not
        """

        guild_id = discord.guild_id(msg)
        handle = discord.handle(msg)

        # If the message matches the regex, create the key and value if it is not already in the database
        # Try to get the record to see if it exists
        record = dynamo.get(self.db_table, guild_id, handle)
        if record:
            if self.check_timestamp(record.updated_at):
                # If check_timestamp() the user is no longer on cooldown
                # Update record with new timestamp
                dynamo.update(
                    table=self.db_table,
                    record=record,
                    fields_to_update=[],  # no items to update as the update method changes the timestamp
                )

                # Update the updated_at variable for the class with the latest updated_at time
                self.updated_at = record.updated_at

                # Return true to allow the user to use the command
                return True
            
            # The user is still on cooldown
            else:
                # Set the updated_at value so we have a current version of what the cooldown looks like
                self.updated_at = record.updated_at
                return False
        else:
            # Write the record if it does not exist
            dynamo.write(
                self.db_table(
                    discord_server_id=guild_id,
                    discord_handle=handle,
                    updated_at=util.iso_timestamp(),
                )
            )
            # We write the record and let the user play the sound
            return True