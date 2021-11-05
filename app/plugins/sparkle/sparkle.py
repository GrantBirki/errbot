import re

from errbot import BotPlugin, botcmd
from lib.chat.discord import Discord
from lib.common.cooldown import CoolDown
from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import SparkleTable
from lib.common.utilities import Util

cooldown = CoolDown(2, SparkleTable)
discord = Discord()
dynamo = Dynamo()
util = Util()

MAX_SPARKLE_REASON_LENGTH = 100

class Sparkle(BotPlugin):
    """Sparkle plugin for Errbot"""

    @botcmd()
    def sparkle(self, msg, args):
        """
        ✨ Sparkle another Discord user to show your appreciation ✨

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

        # If the result is None, it failed the regex
        if not result:
            return f"❌ {discord.mention_user(msg)} I couldn't properly parse that command with my magic regex"

        if result["sparkle_reason"] is not None and "|" in result['sparkle_reason']:
            return f"❌ {discord.mention_user(msg)} The `|` is a reserved character for this command and cannot be used"

        # Users cannot sparkle themselves
        if int(discord.get_user_id(msg)) == int(result['handle']):
            return "You can't sparkle yourself but nice try"

        # If no conditions are met then we passed!
        return None

    def sparkle_main(self, msg):
        """
        The main logic which drives the .sparkle command
        """

        # Get the guild_id for the channel where the .sparkle command was run
        guild_id = discord.guild_id(msg)

        # Get the result from the msg by parsing it with regex
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

            # If the record exists, we can run logic to update the record with the new sparkle
            if record:
                    
                    # Logic if a sparkle reason is supplied
                    if result['sparkle_reason'] is not None:

                        # Update the record with a sparkle reason
                        update_result = dynamo.update(
                            table=SparkleTable,
                            record=record,
                            fields_to_update=[
                                SparkleTable.total_sparkles.set(record.total_sparkles + 1),
                                SparkleTable.sparkle_reasons.set(record.sparkle_reasons + f"|{result['sparkle_reason']}")
                            ],
                        )
                        # The update passed
                        if update_result:
                            return f"{discord.mention_user(msg)} sparkled {result['handle_full']} for {result['sparkle_reason']} ✨✨**{record.total_sparkles}**✨✨"
                        else:
                            # If the update_result is anything other than True, it failed
                            return f"❌ {discord.mention_user(msg)} I failed to update the database with your `.sparkle` command"

                    # Logic if no sparkle reason is supplied
                    else:
                        # Update the record with no sparkle reason supplied
                        update_result = dynamo.update(
                            table=SparkleTable,
                            record=record,
                            fields_to_update=[
                                SparkleTable.total_sparkles.set(record.total_sparkles + 1)
                            ],
                        )
                        # The update passed
                        if update_result:
                            return f"{discord.mention_user(msg)} sparkled {result['handle_full']} ✨✨**{record.total_sparkles}**✨✨" 
                        else:
                            # If the update_result is anything other than True, it failed
                            return f"❌ {discord.mention_user(msg)} I failed to update the database with your `.sparkle` command"
                                           
            else:
                if result['sparkle_reason'] is not None:
                    # Write the record if it does not exist
                    new_record = dynamo.write(
                        SparkleTable(
                            discord_server_id=guild_id,
                            discord_handle=result['handle'],
                            total_sparkles=1,
                            sparkle_reasons=result['sparkle_reason'],
                            updated_at=util.iso_timestamp(),
                        )
                    )
                else:
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
                    return f"✨🌟✨ {result['handle_full']} just got their first sparkle!! ✨🌟✨"
                else:
                    return f"❌ I couldn't write to the database, sorry {discord.mention_user(msg)}"

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
        try:
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
                # If the sparkle_reason is blank we toss it out
                if len(sparkle_reason) == 0:
                    sparkle_reason = None
                # If the sparkle reason is more than 100 characters, truncate it
                elif len(sparkle_reason) > MAX_SPARKLE_REASON_LENGTH:
                    sparkle_reason = sparkle_reason[:MAX_SPARKLE_REASON_LENGTH]

            # return the dict of the handle and sparkle_reason
            return {
                "handle": str(discord.get_user_id(handle)),
                "sparkle_reason": sparkle_reason,
                "handle_full": handle
            }
        except:
            # If anything goes wrong, return None
            return None
