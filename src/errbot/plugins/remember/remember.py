from errbot import BotPlugin, botcmd
import re
from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import RememberTable
from lib.chat.chatutils import ChatUtils
from lib.common.utilities import Util

dynamo = Dynamo()
chatutils = ChatUtils()
util = Util()

MAX_SEARCH_ITEMS_TO_DISPLAY = 20

class Remember(BotPlugin):
    """Remember plugin for Errbot"""

    @botcmd
    def remember(self, msg, args):
        """
        Remember something / anything for any reason
        .rem <key> is <value>
        """
        return self.remember_main(msg, args)

    @botcmd
    def rem(self, msg, args):
        """
        Remember something / anything for any reason
        The shorthand of .remember
        """
        return self.remember_main(msg, args)

    def remember_main(self, msg, args):
        """
        The main logic which drives the .rem/.remember command
        """

        guild_id = chatutils.guild_id(msg)

        # If the message is a private message
        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        result = self.rem_regex(msg)

        # If the message matches the regex, create the key and value if it is not already in the database
        if result:
            # Try to get the record to see if it exists
            record = dynamo.get(RememberTable, guild_id, result["key"])
            if record:
                message = f"I am already remembering something for `{result['key']}`:"
                message += f"> Use `.forget {result['key']}` to forget it"
                message += str(record.rem_value)
                return "\n".join(message)
            else:
                # Write the record if it does not exist
                new_record = dynamo.write(
                    RememberTable(
                        discord_server_id=guild_id,
                        rem_key=result["key"],
                        rem_value=result["value"],
                    )
                )
                if new_record:
                    return f"✅ Ok {chatutils.mention_user(msg)}, I'll remember `{result['key']}` for you"
                else:
                    return f"❌ I couldn't write to the database, sorry {chatutils.mention_user(msg)}"

        # If there was a match, we need to check if the record exists
        record = dynamo.get(RememberTable, guild_id, args)

        # If the record exists, return the value
        if record:
            return str(record.rem_value)
        else:
            return f"🤔 I couldn't remember anything for `{args}`"

    @botcmd
    def forget(self, msg, args):
        """
        Forget something that is being remembered
        .forget <key>
        """
        guild_id = chatutils.guild_id(msg)

        # If the message is a private message
        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        # Try to get the record to see if it exists
        record = dynamo.get(RememberTable, guild_id, args)
        if record is None:
            return f"⚠ Did you type that correctly? I didn't find anything in the database for `{args}`"

        # Delete the record
        result = dynamo.delete(record)

        # If the record was deleted, return a message
        if result:
            return f"✅ Ok {chatutils.mention_user(msg)}, I'll forget about `{args}` for you"
        else:
            return f"❌ Failed to forget about `{args}`!"

    @botcmd
    def rem_search(self, msg, args):
        """
        Search for something that is being remembered
        .rem search or .rem search <text> 
        """

        guild_id = chatutils.guild_id(msg)

        # If the message is a private message
        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        # Get all items in the database
        db_items = dynamo.scan("remember")

        # If there are no items, return
        if not db_items:
            return "🤔 I couldn't find anything in the `remember` database"

        # Check to see if there is a search term
        pattern = r"(\.|!)(rem search)\s(.*)"
        match = re.search(pattern, msg.body)
        if match:
            # Grab the search term from the regex query
            search_term = match.group(3).strip()

            # Get all items from the db in a list if the guild_id matches the discord_server_id
            db_items_list = [
                item["rem_key"]
                for item in db_items
                if item["discord_server_id"] == guild_id
            ]

            # Get all the close matches to the search term
            matches = util.close_matches(search_term, db_items_list, n=100)

            if not matches:
                return f"🤔 I couldn't find anything for `{search_term}` - Please try refining your search"

            # Loop through all the matches and display them
            counter = 0
            message = ""
            for match in matches:
                if counter >= MAX_SEARCH_ITEMS_TO_DISPLAY:
                    message += f"\nAnd {len(matches) - counter} more..."
                    break

                message += f"• {match}\n"
                counter += 1

            # Return the message
            return chatutils.send_card_helper(
                bot_self=self,
                title=f"🔍 Remember Search - `{search_term}`",
                body=message,
                color=chatutils.color("blue"),
                in_reply_to=msg,
            )
        # If no search term was used, return all the items from the db for the search
        else:
            items = db_items

        # Loop through all the saved rem items and return them
        counter = 0
        message = ""
        for record in items:
            if guild_id != record["discord_server_id"]:
                continue

            if counter >= MAX_SEARCH_ITEMS_TO_DISPLAY:
                message += f"\nAnd {len(items) - counter} more..."
                break

            message += f"• {record['rem_key']}\n"
            counter += 1

        # Return the message
        return chatutils.send_card_helper(
            bot_self=self,
            title="🔍 Remember Search",
            body=message,
            color=chatutils.color("blue"),
            in_reply_to=msg,
        )

    def rem_regex(self, msg):
        """
        Create the key and value of the remember command from the message
        :param msg: The message to parse
        :return: A dict of the key and value of the message to remember
        If no matches it returns None
        Example match: .rem hello is world -> The value of 'hello' will be remembered as 'world'
        """
        pattern = r"(\.|!)(rem|remember)\s(.*)is\s(.*)"
        match = re.search(pattern, msg.body)
        # If no match, return None
        if not match:
            return None
        key = match.group(3).strip()
        value = match.group(4).strip()

        # If there is a match, return a dict of the key and value
        return {"key": key, "value": value}
