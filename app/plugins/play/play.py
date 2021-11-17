import glob
import json
import os
import re
import sys
import uuid

import validators
from errbot import BotPlugin, botcmd
from lib.chat.discord import Discord
from lib.chat.discord_custom import DiscordCustom
from lib.common.cooldown import CoolDown
from lib.common.utilities import Util
from lib.common.youtube_dl_lib import YtdlLib
from lib.database.dynamo_tables import PlayTable
from youtubesearchpython import VideosSearch

# cooldown = CoolDown(10, PlayTable) # uncomment to enable cooldowl
util = Util()
discord = Discord()
ytdl = YtdlLib()

CRON_INTERVAL = 2
QUEUE_PATH = "plugins/play/queue"
QUEUE_ERROR_MSG = f"❌ An error occurring writing your request to the `.play` queue!"


class Play(BotPlugin):
    """Play plugin for Errbot"""

    def play_cron(self):
        """
        The core logic for the .play cron (aka running from the queue)
        """

        # Scans all the .play queue files (checks all guilds/servers)
        for queue in self.scan_queue_dir():
            # If a queue file is found for a guild/server, read it
            queue_items = self.read_queue(queue)

            # If the queue is empty, return
            if len(queue_items) == 0:
                # Stop the poller as well until another .play command invokes it
                self.stop_poller(self.play_cron)
                return

            # Load the first item in the queue since we are processing songs in FIFO order
            queue_item = queue_items[0]

            hms = util.hours_minutes_seconds(queue_item["song_duration"])
            message = f"• **Song:** {queue_item['song']}\n"
            message += f"• **Duration:** {hms['minutes']}:{hms['seconds']}\n"
            message += f"• **Requested by:** <@{queue_item['user_id']}>\n"

            try:
                message += f"> **Next song:** {queue_items[1]['song']}"
            except IndexError:
                message += "> **Next song:** None"

            # Send the currently playing song into to the BOT_HOME_CHANNEL
            self.send_card(
                to=self.build_identifier(
                    f"#{os.environ['BOT_HOME_CHANNEL']}@{queue_item['guild_id']}"
                ),
                title=f"🎶 Now Playing:",
                body=message,
                color=discord.color("blue"),
            )

            # Play the item in the queue
            dc = DiscordCustom(self._bot)
            dc.play_audio_file(
                queue_item["discord_channel_id"],
                queue_item["file_path"],
                file_duration=queue_item["song_duration"],
            )

            # Remove the item from the queue after it has been played
            self.delete_from_queue(queue_item["guild_id"], queue_item["song_uuid"])

    @botcmd
    def play(self, msg, args):
        """
        Play the audio from a YouTube video in chat!

        Usage: .play <youtube url>

        --channel <channel ID> - Optional: The full channel id to play the video/audio in
        Note: Use the --channel flag if you are not in a voice channel or want to play in a specific channel
        """

        # Dev Notes: This command always adds files to the queue. The play_cron() is responsible for playing all songs

        # Parse the URL and channel out of the user's input
        result = self.play_regex(args)
        if result is None:
            yield f"❌ My magic regex failed to parse your command!\n`{msg}`"
            return
        elif result is False:
            yield f"❌ You must provide the exact URL to a song if you are using the --channel flag"
            return
        url = result["url"]
        channel = result["channel"]

        # If the user provided a string instead of a raw URL, we search YouTube for the given string
        if result["text_search"]:
            yt_search_result = self.youtube_text_search(result["text_search"])
            # If a result was returned, use the returned URL
            if yt_search_result:
                url = yt_search_result
            # If a result was not returned, return an error message
            else:
                yield f"❌ No results found for `{result['text_search']}`"
                return

        # Run some validation on the URL the user is providing
        if not validators.url(url):
            yield f"❌ Invalid URL\n{url}"
            return
        if not url.startswith("https://www.youtube.com/"):
            yield "❌ I only accept URLs that start with `https://www.youtube.com/`"
            return

        # Check the user's cooldown for the .play command
        # allowed = cooldown.check(msg) # uncomment to enable cooldowl
        allowed = True  # comment to enable cooldowl

        if allowed:
            # Get all the metadata for a given video from a URL
            video_metadata = ytdl.video_metadata(url)

            length = video_metadata["duration"]
            # If the length is 0 it is probably a live stream
            if length == 0:
                yield f"❌ Cannot play a live stream from YouTube"
                return

            # If the video is greater than the configured max length, don't play it
            if length > ytdl.max_length:
                yield f"❌ Video is longer than the max accepted length: `{ytdl.max_length}` seconds"
                yield

            # Check if the queue .json file is read for reads/writes
            file_ready = util.check_file_ready(
                f"{QUEUE_PATH}/{discord.guild_id(msg)}_queue.json"
            )

            # If it is not ready and open by another process we have to exit
            if not file_ready:
                yield QUEUE_ERROR_MSG
                return

            # Check if there are any files in the queue
            queue_items = self.read_queue(discord.guild_id(msg))
            # If the queue is empty, change the response message
            if len(queue_items) == 0:
                response_message = f"🎵 Now playing: `{video_metadata['title']}`"
            # If the queue is not empty, change the response message to 'added'
            else:
                response_message = f"💃🕺💃 Added to queue: `{video_metadata['title']}`"

            # If the --channel flag was not provided, use the channel the user is in as the .play target channel
            if channel is None:
                # Get the current voice channel of the user who invoked the command
                dc = DiscordCustom(self._bot)
                channel_dict = dc.get_voice_channel_of_a_user(
                    discord.guild_id(msg), discord.get_user_id(msg)
                )
                # If the user is not in a voice channel, return a helpful error message
                if not channel_dict:
                    yield "❌ You are not in a voice channel. Use the --channel <id> flag or join a voice channel to use this command"
                    return
                channel = channel_dict["channel_id"]

            # Pre-Download the file for the queue
            yield f"📂 Downloading: `{video_metadata['title']}`"
            song_uuid = str(uuid.uuid4())
            file_path = ytdl.download_audio(url, file_name=song_uuid)

            # If the queue file is ready, we can add the song to the queue
            result = self.add_to_queue(
                msg, channel, video_metadata, file_path, song_uuid
            )

            # If something went wrong, we can't add the song to the queue and send an error message
            if not result:
                yield QUEUE_ERROR_MSG

            # If we got this far, the song has been queue'd and will be picked up and played by the cron
            yield response_message

            # If a cron poller for self.play_cron is not running, start it
            # Dev note: pollers are isolated to an errbot plugin so it can't affect other plugin cron pollers
            if len(self.current_pollers) == 0:
                self.start_poller(CRON_INTERVAL, self.play_cron)

            return

        else:
            # A user is trying to play a song too quickly
            message = "Slow down!\n"
            # message += f"⏲️ Cooldown expires in `{cooldown.remaining()}`" # uncomment to enable cooldowl
            yield message
            return

    @botcmd
    def play_queue(self, msg, args):
        """
        See what is in the .play queue
        Usage: .play queue
        """
        queue_items = self.read_queue(discord.guild_id(msg))

        # If the queue is empty, return
        if len(queue_items) == 0:
            return "🎵 No songs in the queue"

        # If the queue is not empty, return the queue items
        message = "🎵 Songs in the queue:\n"
        for place, item in enumerate(queue_items):
            hms = util.hours_minutes_seconds(item["song_duration"])
            message += f"**{place + 1}:** `{item['song']}` - `{hms['minutes']}:{hms['seconds']}` - <@{item['user_id']}>\n"

        return message

    def read_queue(self, guild_id):
        """
        Helper function - Read the .play queue for a given guild/server
        :param guild_id: The guild/server ID
        :return: A list of queue items - each item is a dictionary
        """
        try:
            with open(f"{QUEUE_PATH}/{guild_id}_queue.json", "r") as queue_file:
                queue_items = json.loads(queue_file.read())
            return queue_items
        except FileNotFoundError:
            return []

    def scan_queue_dir(self):
        """
        Helper function for scanning all the .play queue files
        :return: A list of all the queue files (each item in the list is an int of the guild ID)
        """
        queue_files = []
        for filepath in glob.iglob(f"{QUEUE_PATH}/*.json"):
            queue_files.append(
                int(
                    filepath.strip()
                    .replace("_queue.json", "")
                    .replace(f"{QUEUE_PATH}/", "")
                )
            )
        return queue_files

    def add_to_queue(self, msg, channel, video_metadata, file_name, song_uuid):
        """
        Helper function - Add a song to the .play queue
        """

        queue_path = f"{QUEUE_PATH}/{discord.guild_id(msg)}_queue.json"

        # Truncate long song titles
        title_length = 40
        if len(video_metadata["title"]) > title_length:
            song = video_metadata["title"][:title_length] + "..."
        else:
            song = video_metadata["title"]

        queue_item = {
            "guild_id": discord.guild_id(msg),
            "user_id": discord.get_user_id(msg),
            "discord_channel_id": channel,
            "song_uuid": song_uuid,
            "song": song,
            "song_duration": video_metadata["duration"],
            "url": video_metadata["webpage_url"],
            "file_path": file_name,
        }

        # Check if the queue file exists
        file_exists = os.path.exists(queue_path)

        # The the file exists, we read the queue data
        if file_exists:
            with open(queue_path, "r+") as queue_file:
                # Append to the queue with the new queue item
                queue = json.loads(queue_file.read()) + [queue_item]
                # Seek to the start of the file and nuke the contents
                queue_file.seek(0)
                queue_file.truncate(0)
                # Overwrite the file with the new queue data
                queue_file.write(json.dumps(queue))
        # If the file doesn't exist, we create it and add the queue item
        else:
            with open(queue_path, "w") as queue_file:
                queue_file.write(json.dumps([queue_item]))

        return True

    def delete_from_queue(self, guild_id, song_uuid):
        """
        Helper function - Delete a song from the .play queue
        :param guild_id: The guild/server ID of the queue file
        :param song_uuid: The song UUID to delete
        """
        # Compute the queue path
        queue_path = f"{QUEUE_PATH}/{guild_id}_queue.json"
        # Check if the queue file exists
        file_exists = os.path.exists(queue_path)

        # If the file exists, we read the queue data
        if file_exists:
            with open(queue_path, "r+") as queue_file:
                # Read and load the queue data as json
                queue = json.loads(queue_file.read())

                # Loop through the queue and delete the item with the matching UUID
                queue_list = []
                for item in queue:
                    # If the UUID matches, we skip it (effectively deleting it)
                    if item["song_uuid"] == song_uuid:
                        continue
                    # Add all the other non-matching items to the queue list
                    else:
                        queue_list.append(item)

                # Seek to the start of the file and nuke the contents
                queue_file.seek(0)
                queue_file.truncate(0)
                # Overwrite the file with the new queue data
                queue_file.write(json.dumps(queue_list))

    def youtube_text_search(self, query):
        """
        Helper function - Search for a song on YouTube
        :param query: The search query (string)
        :return: The URL of the first result or None if no results / bad results
        """
        # Search YouTube with a given query and return the first result
        result = VideosSearch(query, limit=1)
        result = result.result()["result"]

        # If the search returns no results, return None
        if len(result) == 0:
            return None
        # If the type of the search is not a video, return None
        if result[0]["type"] != "video":
            return None

        # Return the video link/url if present, otherwise return None
        return result[0].get("link", None)

    def play_regex(self, args):
        """
        Helper function - Regex for the .play command
        Captures the song URL from the message
        :param msg: The message object
        :param channel: The --channel flag value
        :return 1: False if --channel was used without an exact URL
        :return 2: A dict with "url", "channel", and "text_search" values
        :return 3: None if no other conditions were met
        """

        # Check if the user is attempting a text search with --channel
        # This could lead to a random song playing so we actively prevent it
        if "--channel" in args and not "https://www.youtube.com" in args:
            return False

        # If the --channel flag was used, check for the URL with different regex patterns
        if "--channel" in args:
            # First, check if the --channel flag is present at the end of the string
            pattern = r"^(https:\/\/www\.youtube\.com\/.*)\s--channel\s(\d+)$"
            match = re.search(pattern, args)
            # If there is a match, we have the data we need and can return
            if match:
                return {
                    "url": match.group(1),
                    "channel": int(match.group(2).strip()),
                    "text_search": None,
                }

            # Second, check if the --channel flag is present at the beginning of the string
            pattern = r"^--channel\s(\d+)\s(https:\/\/www\.youtube\.com\/.*)$"
            match = re.search(pattern, args)
            # If there is a match, we have the data we need and can return
            if match:
                return {
                    "url": match.group(2),
                    "channel": int(match.group(1).strip()),
                    "text_search": None,
                }

        # If the --channel flag was not used, we first look for the URL
        else:
            pattern = r"^(https:\/\/www\.youtube\.com\/.*)$"
            match = re.search(pattern, args)
            # If a match was found, return the URL
            if match:
                return {
                    "url": match.group(1).strip(),
                    "channel": None,
                    "text_search": None,
                }
            # If no match was found then we assume a text search is taking place
            else:
                return {"url": None, "channel": None, "text_search": args}

        # If there is still no match, return None
        return None
