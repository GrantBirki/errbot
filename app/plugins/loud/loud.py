import os
import random

from errbot import BotPlugin, arg_botcmd, botcmd
from lib.chat.discord import Discord
from lib.chat.discord_custom import DiscordCustom
from lib.common.utilities import Util
from lib.database.dynamo import Dynamo, LoudTable

dynamo = Dynamo()
discord = Discord()
util = Util()

PATH = "plugins/loud/sounds"
COOLDOWN = 1  # Days


class Load(BotPlugin):
    """Loud plugin for Errbot - Plays loud sounds"""

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    @arg_botcmd("--sound", dest="sound", type=str, default=None)
    def loud(self, msg, channel=None, sound=None):
        """
        Play an audio file from the sounds folder in a given channel
        """

        if self.check_updated_at(msg):

            yield f"📢 LOUD Playing: `{sound}`"

            dc = DiscordCustom(self._bot)
            dc.play_audio_file(channel, f"{PATH}/{sound}")
        else:
            yield "Not playing sound! You can only use this command once per day"

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def random_loud(self, msg, channel=None):
        """
        Play a random audio file from the sounds folder in a given channel
        """

        sound = random.choice(os.listdir(PATH))

        if self.check_updated_at(msg):

            yield f"📢 LOUD Playing Random Sound: `{sound}`"

            dc = DiscordCustom(self._bot)
            dc.play_audio_file(channel, f"{PATH}/{sound}")
        else:
            yield "Not playing sound! You can only use this command once per day"

    def check_timestamp(self, timestamp):
        """
        Checks if the timestamp is within the cool down period
        :return: False if the timestamp is within the cool down period, True if not
        """
        timestamp = util.parse_iso_timestamp(timestamp)
        return util.is_timestamp_older_than_n_days(timestamp, COOLDOWN)

    def check_updated_at(self, msg):
        """
        Checks when the 'loud' command was last used for cool down timers
        :return: True if the command was used recently, False if not
        """

        guild_id = discord.guild_id(msg)
        handle = discord.handle(msg)

        # If the message matches the regex, create the key and value if it is not already in the database
        # Try to get the record to see if it exists
        record = dynamo.get(LoudTable, guild_id, handle)
        if record:
            if self.check_timestamp(record.updated_at):
                # Update record with new timestamp
                dynamo.update(
                    table=LoudTable,
                    record=record,
                    fields_to_update=[],  # no items to update as the update method changes the timestamp
                )

                return True
            else:
                return False
        else:
            # Write the record if it does not exist
            new_record = dynamo.write(
                LoudTable(
                    discord_server_id=guild_id,
                    discord_handle=handle,
                    updated_at=util.iso_timestamp(),
                )
            )
            if new_record:
                # Return true as the record was created for a first time user
                return True
            else:
                # Failed to write to the DB so we will let the user play the sound
                return False
