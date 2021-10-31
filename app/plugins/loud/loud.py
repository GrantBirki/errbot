from errbot import BotPlugin, botcmd, arg_botcmd

from lib.chat.discord_custom import DiscordCustom
from lib.database.dynamo import Dynamo, LoudTable
from lib.chat.discord import Discord

dynamo = Dynamo()
discord = Discord()

import os, random

PATH = "plugins/loud/sounds"


class Load(BotPlugin):
    """Loud plugin for Errbot - Plays loud sounds"""

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    @arg_botcmd("--sound", dest="sound", type=str, default=None)
    def loud(self, msg, channel=None, sound=None):
        """
        Play an audio file from the sounds folder in a given channel
        """

        yield f"📢 LOUD Playing: `{sound}`"

        dc = DiscordCustom(self._bot)
        dc.play_audio_file(channel, f"{PATH}/{sound}")

    @arg_botcmd("--channel", dest="channel", type=int, default=None)
    def random_audio(self, msg, channel=None):
        """
        Play a random audio file from the sounds folder in a given channel
        """

        sound = random.choice(os.listdir("plugins/audio/sounds"))

        yield f"📢 LOUD Playing Random Sound: `{sound}`"

        dc = DiscordCustom(self._bot)
        dc.play_audio_file(channel, f"{PATH}/{sound}")

    def check_last_used(self, msg):
        """
        Checks when the 'loud' command was last used for cool down timers
        """

        guild_id = discord.guild_id(msg)

        # If the message matches the regex, create the key and value if it is not already in the database
        # Try to get the record to see if it exists
        record = dynamo.get(LoudTable, guild_id, result["key"])
        if record:
            message = f"I am already remembering something for `{result['key']}`:"
            message += f"> Use `.forget {result['key']}` to forget it"
            message += str(record.rem_value)
            return "\n".join(message)
        else:
            # Write the record if it does not exist
            new_record = dynamo.write(
                LoudTable(
                    discord_server_id=guild_id,
                    rem_key=result["key"],
                    rem_value=result["value"],
                )
            )
            if new_record:
                return f"✅ Ok {discord.mention_user(msg)}, I'll remember `{result['key']}` for you"
            else:
                return f"❌ I couldn't write to the database, sorry {discord.mention_user(msg)}"

        # If there was a match, we need to check if the record exists
        record = dynamo.get(RememberTable, guild_id, args)

        # If the record exists, return the value
        if record:
            return str(record.rem_value)
        else:
            return f"🤔 I couldn't remember anything for `{args}`"

