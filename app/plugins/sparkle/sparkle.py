import re

from errbot import BotPlugin, botcmd
from lib.chat.discord import Discord
from lib.common.cooldown import CoolDown
from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import SparkleTable
from lib.common.utilities import Util

cooldown = CoolDown(5, SparkleTable)
discord = Discord()
dynamo = Dynamo()
util = Util()


class Sparkle(BotPlugin):
    """Sparkle plugin for Errbot"""

    @botcmd()
    def sparkle(self, msg, args):
        """
        Sparkle another Discord user to show your appreciation

        Example 1: .sparkle @username for being awesome
        Example 2: .sparkle @username
        Example 3: .sparkle @username because are the best
        """

        allowed = cooldown.check(msg)

        if allowed:
            return self.sparkle_main(msg)
        else:
            message = "Slow down!\n"
            message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`"
            return message

    def sparkle_check(self, msg, result, guild_id):
        """
        Sanity checks for the .sparkle command
        """
        # Sparkles cannot be DMs
        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        # Users cannot sparkle themselves
        if discord.handle(msg).lower() == result['handle'].lower():
            return "You can't sparkle yourself but nice try"

        # If no conditions are met then we passed!
        return None

    def sparkle_main(self, msg):
        """
        The main logic which drives the .sparkle command
        """

        # Get the guild_id for the channel where the .sparkle command was run
        guild_id = discord.guild_id(msg)

        # Get the result from the msg which is -> {"handle": handle, "sparkle_reason": sparkle_reason}
        result = self.sparkle_regex(msg)

        # If the sparkle check returns anything other than 'None' it failed
        failed = self.sparkle_check(msg, result, guild_id)
        if failed:
            # Return the failure message
            return failed

        # If the message matches the regex, create the key and value if it is not already in the database
        if result:
            # Try to get the record to see if it exists
            record = dynamo.get(SparkleTable, guild_id, result['handle'])

            # If the record exists, we increment the sparkle count by 1
            if record:
                update_result = dynamo.update(
                    table=SparkleTable,
                    record=record,
                    fields_to_update=[
                        SparkleTable.total_sparkles.set(record.total_sparkles + 1),
                    ],
                )

                # If the db update was successful
                if update_result:
                    # Return the responses to chat depending on if a sparkle_reason was provided or not
                    if result['sparkle_reason'] is not None:
                        # With a sparkle reason
                        return f"{discord.mention_user(msg)} sparkled {result['handle']} for {result['sparkle_reason']}"
                    else:
                        # Without a sparkle reason
                        return f"{discord.mention_user(msg)} sparkled {result['handle']}"
                else:
                    # If the update_result is anything other than True, it failed
                    return f"❌ {discord.mention_user(msg)} I failed to update the database with your `.sparkle` command"
            else:
                # Write the record if it does not exist
                new_record = dynamo.write(
                    SparkleTable(
                        discord_server_id=guild_id,
                        discord_handle=result['handle'],
                        total_sparkles=1,
                        updated_at=util.iso_timestamp(),
                    )
                )
                # If the new record was written successfully, we post a 'first' sparkle message!
                if new_record:
                    return f"{result['handle']} just got their first sparkle!!"
                else:
                    return f"❌ I couldn't write to the database, sorry {discord.mention_user(msg)}"
        else:
            # The sparkle_regex() function failed to get a username or username + reason from the message
            return f"❌ {discord.mention_user(msg)} I couldn't properly parse that command with my magic regex"

    def sparkle_regex(self, msg):
        """
        Find the user being Sparkled and the reason
        :param msg: The message to parse
        :return: A dict of the 'handle' and 'reason' for the sparkling
        If no matches it returns None
        Note: if not 'reason' is supplied it is set to None in the dict
        Example match: .sparkle @birki for things -> Birki's sparkle count will increase by 1
        Alt Example match: .sparkle @birki -> Birki's sparkle count will increase by 1
        Note: The 'reason' is parsed later on and save for historical purposes
        """
        # Check for a .sparkle <handle> for <reason>
        pattern = r"(\.|!)(sparkle)\s(.*)(for|because)\s(.*)"
        match = re.search(pattern, msg.body)
        # If no match, check with no reason
        if not match:
            # Regex pattern with no reason supplied
            pattern = r"(\.|!)(sparkle)\s(.*)"
            match = re.search(pattern, msg.body)
            # If there is still no match then we return None
            if not match:
                return None
            # If there was a match, set the handle and make the sparkle_reason 'None'
            handle = match.group(3).strip()
            sparkle_reason = None
        
        # If there is an initial match we have a handle and a sparkle_reason.. yay!
        else:
            handle = match.group(3).strip()
            sparkle_reason = match.group(5).strip()

        # return the dict of the handle and sparkle_reason
        return {"handle": handle, "sparkle_reason": sparkle_reason}
