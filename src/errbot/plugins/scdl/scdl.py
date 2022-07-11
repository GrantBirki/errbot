import uuid

from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom
from lib.common.errhelper import ErrHelper
from lib.common.scdl_lib import Scdl

chatutils = ChatUtils()
scdl = Scdl(path="plugins/scdl/downloads")

MAX_FILE_SIZE = 15728640 # 15MB
SOUNDCLOUD_BASE_URL = "https://soundcloud.com/"

class Scdl(BotPlugin):  
    """Scdl plugin for Errbot"""

    @botcmd
    def scdl(self, msg, args):  
        """
        The most basic example of a chatbot command/function
        Tip: The name of the function above is literally how you invoke the chatop: .scdl
        Pro Tip: "_" in function names render as spaces so you can do 'def send_scdl(...)' -> .send scdl
        """
        ErrHelper().user(msg)

        guild_id = chatutils.guild_id(msg)

        # If the message is a private message
        if not guild_id:
            yield "Please run this command in a Discord channel, not a DM"
            return

        # Check to ensure the user provided some form of arguments
        if len(args) == 0:
            yield "⚠ No arguments provided! - Use the `.scdl help` command for examples"
            return

        # Attempt to parse the URL from the args
        url = args.strip()

        # Validate the URL
        if not url.startswith(SOUNDCLOUD_BASE_URL):
            yield f"⚠ I only accept links to {SOUNDCLOUD_BASE_URL}"
            return
        if "/sets/" in url:
            yield "❌ I do not support Soundcloud sets/playlists"
            return

        # Init the DiscordCustom object
        dc = DiscordCustom(self._bot)

        # Get the channel ID from the message to send the file to
        channel_id = chatutils.channel_id(msg)

        # Generate a random file name
        song_uuid = str(uuid.uuid4())

        # Attempt to download the song from soundcloud with scdl
        result = scdl.download(url, song_uuid)
        if result["result"] == False:
            raise Exception(result["message"])
        else:
            file_path = result["path"]

        # Send the file
        dc.send_file(channel_id, file_path)

        yield "Done"
        return
