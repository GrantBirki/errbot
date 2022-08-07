import os
import time
import uuid

from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom
from lib.common.errhelper import ErrHelper
from lib.common.scdl_lib import Scdl

chatutils = ChatUtils()
scdl = Scdl(path="plugins/scdl/downloads")

MAX_FILE_SIZE = 94,371,840  # 90MB
SOUNDCLOUD_BASE_URL = "https://soundcloud.com/"
DOWNLOAD_WAIT = 15  # seconds


class Scdl(BotPlugin):
    """Scdl plugin for Errbot"""

    @botcmd
    def scdl(self, msg, args):
        """
        Soundcloud music downloader

        Usage: .scdl <soundcloud_song_url>
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        guild_id = chatutils.guild_id(msg)

        # If the message is a private message
        if not guild_id:
            yield "Please run this command in a Discord channel, not a DM"
            return

        # Check to ensure the user provided some form of arguments
        if len(args) == 0:
            yield "⚠ No arguments provided!"
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
        yield f"📂 Downloading with scdl: `{url.replace(SOUNDCLOUD_BASE_URL, '')}`\nFilename: `{song_uuid}.mp3`"
        result = scdl.download(url, song_uuid)
        if result["result"] == False:
            raise Exception(result["message"])
        else:
            file_path = result["path"]

        # Send the file
        dc.send_file(channel_id, file_path, max_file_size=MAX_FILE_SIZE)

        # Delete the file after it has been uploaded - But first, sleep for 30 seconds so it can download
        time.sleep(DOWNLOAD_WAIT)
        if os.path.exists(file_path):
            os.remove(file_path)

        return
