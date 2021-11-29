import glob
import json
import os
import re
import uuid

import spotipy
import validators
from errbot import BotPlugin, botcmd
from lib.chat.discord import Discord
from lib.chat.discord_custom import DiscordCustom
from lib.common.sentry import Sentry
from lib.common.utilities import Util
from lib.common.youtube_dl_lib import YtdlLib
from lib.database.dynamo_tables import PlayTable
from lib.database.dynamo import Dynamo
from requests import ReadTimeout
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch

util = Util()
discord = Discord()
ytdl = YtdlLib()
dynamo = Dynamo()

# Try to initialize the Spotify client, if anything fails set sp -> None
try:
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=os.environ["SPOTIFY_CLIENT_ID"],
            client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        ),
        requests_session=False,
        requests_timeout=3,
        backoff_factor=0.1,
        retries=3,
    )
except Exception as e:
    Sentry().capture(e)
    sp = None

CRON_INTERVAL = 2  # seconds
QUEUE_PATH = "plugins/play/queue"
KILL_SWITCH_PATH = "plugins/lib/chat/dc_kill_switches"
QUEUE_ERROR_MSG_READ = f"❌ An error occurring reading the .play queue!"


class Play(BotPlugin):
    """Play plugin for Errbot"""

    def play_cron(self):
        """
        The core logic for the .play cron (aka running from the queue)
        """
        try:
            # Scans all the .play queue files (checks all guilds/servers)
            for queue in self.scan_queue_dir():
                # If a queue file is found for a guild/server, read it
                queue_items = self.read_queue(queue)

                # If the queue file is not ready for reads, exit the function
                if queue_items is False:
                    self.log.warn(
                        f"play_cron() blocked due to a failed read on the queue: {queue}"
                    )
                    return

                # If the queue is empty, return
                if len(queue_items) == 0:
                    # Stop the poller and wait until another .play command invokes it
                    self.log.info(
                        "0.1: Queue is empty, stopping the play_cron() poller"
                    )  # DEBUG
                    self.stop_poller(self.play_cron)
                    return

                # Load the first item in the queue since we are processing songs in FIFO order
                self.log.info("1: Loading the first item in the queue")  # DEBUG
                queue_item = queue_items[0]

                self.log.info("2: calculating song hms")  # DEBUG
                hms = util.hours_minutes_seconds(queue_item["song_duration"])
                message = f"• **Song:** {queue_item['song']}\n"
                message += f"• **Duration:** {hms['minutes']:02}:{hms['seconds']:02}\n"
                message += f"• **Requested by:** <@{queue_item['user_id']}>\n"

                self.log.info("3: trying to get spotify URL")  # DEBUG
                spotify_url = self.spotify_url(queue_item)
                if spotify_url:
                    message += f"• **Spotify:** {spotify_url}\n"

                self.log.info("4: get next song info")  # DEBUG
                try:
                    message += f"> **Next song:** {queue_items[1]['song']}"
                except IndexError:
                    message += "> **Next song:** None"

                self.log.info("5: send card to #errbot channel")  # DEBUG
                # Send the currently playing song into to the BOT_HOME_CHANNEL
                discord.send_card_helper(
                    bot_self=self,
                    to=self.build_identifier(
                        f"#{os.environ['BOT_HOME_CHANNEL']}@{queue_item['guild_id']}"
                    ),
                    title="🎶 Now Playing:",
                    body=message,
                    color=discord.color("blue"),
                )

                self.log.info("6: init DiscordCustom lib")  # DEBUG
                # Play the item in the queue
                dc = DiscordCustom(self._bot)
                self.log.info("7: play the audio file")  # DEBUG
                dc.play_audio_file(
                    queue_item["discord_channel_id"],
                    queue_item["file_path"],
                    file_duration=queue_item["song_duration"],
                )

                self.log.info("8: remove the item from the queue")  # DEBUG
                # Remove the item from the queue after it has been played
                self.delete_from_queue(queue_item["guild_id"], queue_item["song_uuid"])

                self.log.info("9: update the play stats")  # DEBUG
                # Update the play stats with the current song data
                self.update_play_stats(queue_item)
                self.log.info("10: play_cron() logic done - OK")  # DEBUG

        except Exception as e:
            Sentry().capture(e)
            self.log.exception(f"The play_cron() failed! - Error: {e}")

    @botcmd
    def play(self, msg, args):
        """
        Play the audio from a YouTube video in chat!

        Usage: .play <youtube url>

        --channel <channel ID> - Optional: The full channel id to play the video/audio in
        Note: Use the --channel flag if you are not in a voice channel or want to play in a specific channel
        """
        Sentry().user(msg)

        # Dev Notes: This command always adds files to the queue. The play_cron() is responsible for playing all songs

        # Parse the URL and channel out of the user's input
        regex_result = self.play_regex(args)
        if regex_result is None:
            yield f"❌ My magic regex failed to parse your command!\n`{msg}`"
            return
        elif regex_result is False:
            yield f"❌ You must provide the exact URL to a song if you are using the --channel flag"
            return
        url = regex_result["url"]
        channel = regex_result["channel"]

        # If the user provided a string instead of a raw URL, we search YouTube for the given string
        if regex_result["text_search"]:
            yt_search_result = self.youtube_text_search(regex_result["text_search"])
            # If a result was returned, use the returned URL
            if yt_search_result:
                url = yt_search_result
            # If a result was not returned, return an error message
            else:
                yield f"❌ No results found for `{regex_result['text_search']}`"
                return

        # Run some validation on the URL the user is providing
        if not validators.url(url):
            yield f"❌ Invalid URL\n{url}"
            return
        if not url.startswith("https://www.youtube.com/"):
            yield "❌ I only accept URLs that start with `https://www.youtube.com/`"
            return

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
            return

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

        # Check if there are any files in the queue
        queue_items = self.read_queue(discord.guild_id(msg))
        # If it is not ready and open by another process we have to exit
        if queue_items is False:
            yield QUEUE_ERROR_MSG_READ
            return

        # If the queue is empty, change the response message
        if len(queue_items) == 0:
            response_message = f"🎵 Now playing: `{video_metadata['title']}`"
        # If the queue is not empty, change the response message to 'added'
        else:
            response_message = f"💃🕺💃 Added to queue: `{video_metadata['title']}`"

        # If the queue file is ready, we can add the song to the queue
        add_result = self.add_to_queue(
            msg, channel, video_metadata, file_path, song_uuid, regex_result
        )

        # If something went wrong, we can't add the song to the queue and send an error message
        if not add_result:
            yield "❌ An error occurred writing your request to the `.play` queue!"
            return

        # If we got this far, the song has been queue'd and will be picked up and played by the cron
        yield response_message

        # If a cron poller for self.play_cron is not running, start it
        # Dev note: pollers are isolated to an errbot plugin so it can't affect other plugin cron pollers
        if len(self.current_pollers) == 0:
            self.log.info("0: Starting the play_cron() poller")  # DEBUG
            self.start_poller(CRON_INTERVAL, self.play_cron)

        return

    @botcmd
    def play_queue(self, msg, args):
        """
        See what is in the .play queue
        Usage: .play queue
        """
        Sentry().user(msg)

        queue_items = self.read_queue(discord.guild_id(msg))
        # If it is not ready and open by another process we have to exit
        if queue_items is False:
            return QUEUE_ERROR_MSG_READ

        # If the queue is empty, return
        if len(queue_items) == 0:
            return "🎵 No songs in the queue"

        # If the queue is not empty, return the queue items
        message = "🎵 Songs in the queue:\n"
        for place, item in enumerate(queue_items):
            hms = util.hours_minutes_seconds(item["song_duration"])
            message += f"**{place + 1}:** `{item['song']}` - `{hms['minutes']:02}:{hms['seconds']:02}` - <@{item['user_id']}>\n"

        return message

    @botcmd()
    def play_stats(self, msg, args):
        """
        Gets stats about the .play command for your server
        Usage: .play stats
        """
        Sentry().user(msg)

        # Set the default message and title for the response to be returned via chat
        title = f"🎵 **`.play` stats for this Discord server:** 🎵"
        message = ""

        # Get the .play stats for the Discord server where the command is run
        record = dynamo.get(PlayTable, discord.guild_id(msg))

        # Pre-check the record we get from the DB
        if record is None:
            return "0️⃣ No stats yet for this Discord server!\nRun some `.play` commands to rack up some stats"
        elif record is False:
            return "❌ Error getting stats for this Discord server"

        # Parse the record from json into a dict
        stats = json.loads(record.stats)

        # Adds general server stats the the message
        message += (
            f"• 🎧 Total Songs Played: **{stats['play_stats']['total_songs_played']}**\n"
        )
        message += f"• 🕐 Total Time Played: **{self.fmt_play_time(stats['play_stats']['total_time_played'])}**\n"
        message += "\n"

        # Add DJ stats to the message
        djs = stats["dj_stats"]["djs"]
        top_djs = sorted(djs, key=lambda i: i["total_songs_played"], reverse=True)

        # Try to get the top 3 DJs - IndexError for each if there are less than 3
        try:
            dj_1 = top_djs[0]
        except IndexError:
            dj_1 = None
        try:
            dj_2 = top_djs[1]
        except IndexError:
            dj_2 = None
        try:
            dj_3 = top_djs[2]
        except IndexError:
            dj_3 = None

        # Add top DJ stats to the message
        if dj_1:
            message += f"🥇 **Top DJ:** <@{dj_1['user_id']}>\n"
            message += f"• Songs Played: **{dj_1['total_songs_played']}**\n"
            message += f"• Total Play Time: **{self.fmt_play_time(dj_1['total_time_played'])}**\n\n"
        else:
            message += "No top DJs yet\n"
            return discord.send_card_helper(
                bot_self=self,
                title=title,
                body=message,
                color=discord.color("blue"),
                in_reply_to=msg,
            )
        if dj_2:
            message += f"🥈 **2nd Top DJ:** <@{dj_2['user_id']}>\n"
            message += f"• Songs Played: **{dj_2['total_songs_played']}**\n"
            message += f"• Total Play Time: **{self.fmt_play_time(dj_2['total_time_played'])}**\n\n"
        else:
            return discord.send_card_helper(
                bot_self=self,
                title=title,
                body=message,
                color=discord.color("blue"),
                in_reply_to=msg,
            )
        if dj_3:
            message += f"🥉 **3rd Top DJ:** <@{dj_3['user_id']}>\n"
            message += f"• Songs Played: **{dj_3['total_songs_played']}**\n"
            message += f"• Total Play Time: **{self.fmt_play_time(dj_3['total_time_played'])}**\n\n"
        else:
            return discord.send_card_helper(
                bot_self=self,
                title=title,
                body=message,
                color=discord.color("blue"),
                in_reply_to=msg,
            )

        return discord.send_card_helper(
            bot_self=self,
            title=title,
            body=message,
            color=discord.color("blue"),
            in_reply_to=msg,
        )

    @botcmd
    def stop(self, msg, args):
        """
        Stop the current song and removes all songs from the queue
        Usage: .stop (triggers a command flow for confirmation)
        Note: This command is kinda ugly but is helpful to full stop the .play queue
        """
        Sentry().user(msg)

        if msg.ctx.get("confirmed", None) == True:
            stopped = False
            yield "✅ Request confirmed\nStopping playback and removing all songs from the queue"

            # Compute the queue path
            queue_path = f"{QUEUE_PATH}/{discord.guild_id(msg)}_queue.json"
            # Check if the queue file exists
            file_exists = os.path.exists(queue_path)

            # Delete the entire queue file if it exists
            if file_exists:
                stopped = True
                os.remove(queue_path)

            # If no poller/cron is running, then Errbot is not playing a song
            if len(self.current_pollers) == 0:
                yield "Nothing is currently playing so no kill switch will be created"
            else:
                # Use the kill switch to stop the current song
                with open(f"{KILL_SWITCH_PATH}/play.kill", "w") as _:
                    pass
                stopped = True

            if stopped:
                yield "✅ `.stop` command completed"
                return
            else:
                yield "Nothing to `stop` - OK"
                return

        if msg.ctx.get("confirmed", None) == False:
            yield "❌ Request failed confirmation"
            return

        message = "💡 Running this command will stop the current playback and remove ALL songs from the queue.\n"
        message += (
            "To run this command, you need to follow a command flow for confirmation:\n"
        )
        message += "1. `.stop`\n2. `.confirm yes`\n3. `.stop` - Needed once more now that you provided confirmation\n"
        message += "> *Note: If you are looking to skip the current song, run `.skip`*"

        yield message
        return

    @botcmd
    def skip(self, msg, args):
        """
        Skip the current song in the .play queue
        Usage: .skip
        """
        Sentry().user(msg)

        queue_items = self.read_queue(discord.guild_id(msg))
        # If it is not ready and open by another process we have to exit
        if queue_items is False:
            return QUEUE_ERROR_MSG_READ

        # If the queue is empty, return
        if len(queue_items) == 0:
            return "🎵 No songs in the queue - nothing to skip!"

        # If no poller/cron is running, then Errbot is not playing a song
        if len(self.current_pollers) == 0:
            return "🎵 I'm not playing anything at the moment - nothing to skip!"

        # If the queue is not empty, and there is a poller/cron - skip the current song via the kill switch file
        with open(f"{KILL_SWITCH_PATH}/play.kill", "w") as _:
            pass

        return "⏩ Skipping the current song"

    def youtube_title_sanitizer(self, title):
        """
        Helper function for spotify_url to get all the YouTube title junk out
        :param title: The title of the YouTube video (String)
        :return: The title of the YouTube video without the YouTube junk (String)
        """
        # Try to strip out all the [OFFICIAL VIDEO] and (****) junk from the title
        title = re.sub(r"\(.*\)|\[.*]", "", title)

        return title.strip()

    def spotify_url(self, queue_item):
        """
        Get the Spotify URL for a song
        :param queue_item: The queue item to get the Spotify URL for (Dict)
        If a match is found, return the Spotify URL (string)
        If no matches are found, or it fails, return None
        """
        try:
            # If the user used a text search with .play, use that to find the song in Spotify
            # This is the most reliable way to find the song
            if queue_item["text_search"]:
                song = queue_item["text_search"]
            # If the user provided a URL, then we need to parse the YouTube title
            # This is the least reliable way to find the song as YouTube titles can be wild
            else:
                song = queue_item["song"]
                # Get a cleaner version of the YouTube title/song
                song = self.youtube_title_sanitizer(song)

            # Search Spotify for the song
            self.log.info(f"3.1: searching Spotify for {song}")
            results = sp.search(q=song, limit=1)
            self.log.info(f"3.2: search results complete")

            # If no matches were found, return None
            if len(results["tracks"]["items"]) == 0:
                return None

            # Return the Spotify URL as a string
            return results["tracks"]["items"][0]["external_urls"]["spotify"]

        # If the request times out, return None
        except ReadTimeout:
            return None

        except Exception as e:
            Sentry().capture(e)
            return None

    def read_queue(self, guild_id):
        """
        Helper function - Read the .play queue for a given guild/server
        :param guild_id: The guild/server ID
        :return: A list of queue items - each item is a dictionary if successful, False if not ready for reads
        """
        # Check if the queue .json file is read for reads/writes
        file_ready = util.check_file_ready(f"{QUEUE_PATH}/{guild_id}_queue.json")
        # If it is not ready and open by another process we have to exit
        if not file_ready:
            return False

        # Attempt to read the queue file
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

    def add_to_queue(
        self, msg, channel, video_metadata, file_name, song_uuid, regex_result
    ):
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
            "text_search": regex_result["text_search"],
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
        Captures the song URL from the command args
        :param args: The args object
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

    def update_play_stats(self, queue_item):
        """
        Update the play stats with the given queue item for a guild
        :param queue_item: The queue item to update
        :return: None (False if it fails)
        """
        try:
            record = dynamo.get(PlayTable, queue_item["guild_id"])

            # Dev note: both method below will 'write' to the table (not update)
            # If the record exists, update values in memory and re-write the record
            if record:
                # Parse the record's json data into a dict
                record_dict = json.loads(record.stats)

                # Update the play_stats dict with the new queue item
                total_time_played = (
                    record_dict["play_stats"]["total_time_played"]
                    + queue_item["song_duration"]
                )
                total_songs_played = record_dict["play_stats"]["total_songs_played"] + 1

                # Update the dj_stats dict with the new queue item
                dj_updated = False
                djs = record_dict["dj_stats"]["djs"]
                # Check to see if a DJ already has a stats record
                for i, dj in enumerate(djs):
                    # If the DJ has a stats record, update it with the new queue item
                    if dj["user_id"] == queue_item["user_id"]:
                        dj_updated = True
                        djs[i].update(
                            {
                                "total_time_played": dj["total_time_played"]
                                + queue_item["song_duration"],
                                "total_songs_played": dj["total_songs_played"] + 1,
                            }
                        )
                        break
                # If the DJ does not have a stats record, create one and append it to the djs list
                if not dj_updated:
                    djs.append(
                        {
                            "user_id": queue_item["user_id"],
                            "total_time_played": queue_item["song_duration"],
                            "total_songs_played": 1,
                        }
                    )
            # If the record doesn't exist, 'create' it
            elif record is None:
                total_time_played = queue_item["song_duration"]
                total_songs_played = 1
                djs = [
                    {
                        "user_id": queue_item["user_id"],
                        "total_time_played": queue_item["song_duration"],
                        "total_songs_played": 1,
                    }
                ]
            # If we fail to get the record, exit to avoid overwriting our data (results in wiping a servers stats)
            elif record is False:
                return

            # Write to the DB with the updated (or newly created) values
            stats = json.dumps(
                {
                    "play_stats": {
                        "total_time_played": total_time_played,
                        "total_songs_played": total_songs_played,
                    },
                    "dj_stats": {"djs": djs},
                }
            )
            dynamo.write(
                PlayTable(discord_server_id=queue_item["guild_id"], stats=stats)
            )
        except Exception as e:
            Sentry().capture(e)
            return False

    def fmt_play_time(self, play_time):
        """
        Gets the play time for a DJ
        """
        hms = util.hours_minutes_seconds(play_time)
        return f"h{hms['hours']:02}:m{hms['minutes']:02}:s{hms['seconds']:02}"
