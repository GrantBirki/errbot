import os
import re
import time
from string import Template
from datetime import datetime

import requests
from errbot import BotPlugin, botcmd, arg_botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom
from lib.common.down_detector import DownDetector
from lib.common.errhelper import ErrHelper
from lib.common.utilities import Util

from lib.database.dynamo import Dynamo
from lib.database.dynamo_tables import EftTrackerTable

downdetector = DownDetector()
chatutils = ChatUtils()
util = Util()
dynamo = Dynamo()

# 7 seconds for every one second in real time
TARKOV_RATIO = 7

BACKEND = os.environ["BACKEND"]
AMMO_TYPES = [
    "7.62x51mm",
    "7.62x39mm",
    "5.56x45mm",
    "5.45x39mm",
    "7.62x54mm",
    "9x39mm",
    "9x19mm",
    "9x18mm",
    "9x21mm",
    "12/70",
    "4.6x30mm",
    ".338 Lapua",
    ".300 Blackout",
    ".45 ACP",
    "5.7x28mm",
    "7.62x25mm",
    "23x75mm",
    "20/70",
    "12.7x55mm",
    ".366 TKM",
]
MAPS = [
    {"name": "shoreline", "players": "9-12", "duration": "40"},
    {"name": "customs", "players": "9-12", "duration": "35"},
    {"name": "reserve", "players": "9-12", "duration": "35"},
    {"name": "labs", "players": "6-10", "duration": "40"},
    {"name": "lighthouse", "players": "9-12", "duration": "40"},
    {"name": "woods", "players": "9-14", "duration": "40"},
    {"name": "factory", "players": "9-12", "duration": "20-25"},
    {"name": "interchange", "players": "10-14", "duration": "45"},
]
MAP_DIR = "plugins/eft/maps"
EFT_CACHE_TIME = 3600  # 1 hour
INTERVAL = 300  # 5 minutes


class Eft(BotPlugin):
    """Escape From Tarkov plugin for Errbot - Cheeki Breeki!"""

    def __init__(self, bot, name=None):
        """
        Initialize the plugin with its class variables
        Note: self.eft_cache_time is used to check the cache time of eft ammo types and items...
        ...This does not need to be constantly refreshed as updates releasing new items and ammo types is not frequent
        """
        super().__init__(bot, name)
        self.eft_cache_time = None
        self.ammo_data = {}
        self.item_data = {}
        self.item_names = []

    def activate(self):
        """
        Runs the item_tracker_cron() function every interval

        Note: the self.start_polling() function will wait for the first cron job to finish before starting the next one
        """
        super().activate()
        disabled = os.environ.get("DISABLE_EFT_CRON", False)
        if disabled.lower().strip() == "true":
            self.log.warn("eft item cron disabled for local testing")
        else:
            self.start_poller(INTERVAL, self.item_tracker_cron)

    def item_tracker_cron(self):
        """
        The cron that runs to check the item tracker database for items that need to be alerted
        """
        # Get all items in the database
        db_items = dynamo.scan("eftitemtracker")

        # If there are no items, return
        if not db_items:
            return

        # Loop through all returned items and check for possible alerts
        for item in db_items:
            try:
                self.eft_tracker_alert(item)
            except Exception as e:
                ErrHelper().capture(e)

    @botcmd
    def eft_track_help(self, msg, args):
        """
        Help command for .eft track
        Get a detailed help command for the eft item tracker
        """
        # Format the body of the message
        body = "**About:**\n"
        body += "This plugin is used to track items in the Escape From Tarkov game.\n"
        body += "You can track items to see when they reach a fixed price or when they increase by a percentage.\n\n"
        body += "**Usage:**\n"
        body += (
            "`.eft track --item <item> --threshold <threshold> --channel <channel>`\n\n"
        )
        body += "**Examples:**\n"
        body += "`.eft track --item m4a1 --threshold 20000 --channel #eft`\n"
        body += "`.eft track --item m4a1 --threshold 10% --channel #eft`\n"
        body += "`.eft track --item m4a1 --threshold 10.5% --channel #alerts`\n"
        body += "`.eft track --item m4a1 --threshold 10.5%` - No --channel flag defaults to `#general`\n"
        body += '`.eft track --item "golden neck chain" --threshold 25% --channel eft` - Notice the "" quotes\n'
        body += '\n> **Note:** If your --item field contains spaces, wrap it in quotes like so `--item "golden neck chain"`\n'

        # Send the ammo help card
        self.send_card(
            title="EFT Tracker Help Command",
            body=body,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

    @botcmd
    def eft_untrack(self, msg, args):
        """
        Untrack/remove an eft alert
        Usage: .eft untrack <item>
        Example: .eft untrack m4a1
        """
        ErrHelper().user(msg)
        if not args or args.strip() == "":
            return f"⚠️ Please provide an item to remove tracking for"

        server_id = chatutils.guild_id(msg)
        if not server_id:
            return "Please run this command in a Discord channel, not a DM"

        # Check if the item is already tracked
        get_result = dynamo.get(EftTrackerTable, server_id, args)
        if get_result:
            # If the item is tracked, delete it
            delete_result = dynamo.delete(get_result)
            if delete_result:
                return f"✅ {chatutils.mention_user(msg)} `{args}` has been removed from the tracker"
            else:
                return f"❌ Failed to remove `{args}` from the tracker"
        elif get_result is False:
            return f"❌ Failed to get tracking data for `{args}`"
        elif get_result is None:
            return f"⚠️ I could not find any record of `{args}` in the tracker... try again?"

    @arg_botcmd("--item", dest="item", type=str)
    @arg_botcmd("--threshold", dest="threshold", type=str)
    @arg_botcmd("--channel", dest="channel", default="general", type=str)
    def eft_track(self, msg, item=None, threshold=None, channel=None):
        """
        Track the price of an Escape from Tarkov item
        Usage: .eft track --item <item> --threshold <threshold> --channel <channel>
        Example 1: .eft track --item m4a1 --threshold 20000 --channel general
        Example 2: .eft track --item m4a1 --threshold 10% --channel eft
        Example 3: .eft track --item "golden neck chain" --threshold 25% --channel eft
        """
        ErrHelper().user(msg)

        server_id = chatutils.guild_id(msg)
        channel = channel.replace("#", "")

        if not server_id:
            return "Please run this command in a Discord channel, not a DM"

        # Basic checks for parameters
        if item is None or item.strip() == "":
            return "⚠️ Please provide an item to track"
        if threshold is None or threshold.strip() == "":
            return "⚠️ Please provide a threshold"
        if channel is None or channel.strip() == "":
            channel = "general"

        # Sanitize the threshold
        threshold = threshold.strip().replace(",", "")

        get_result = dynamo.get(EftTrackerTable, server_id, item)
        if get_result:
            return f"ℹ️ {chatutils.mention_user(msg)} `{item}` is already being tracked"
        elif get_result is False:
            return f"❌ Failed to get tracking data for `{item}`"

        # Validate the input specifically for the item
        if not self.input_validation(item):
            self.general_error(
                msg,
                "Invalid item input.",
                "Please check your command and try again. Note: `.eft track help` is your friend",
            )
            return
        # Validate the input specifically for the threshold it can either be a number or a percentage
        if not re.match(r"^\d+|^\d+%$", threshold):
            self.general_error(
                msg,
                "Invalid threshold input.",
                "Please check your command and try again. Note: `.eft track help` is your friend",
            )
            return
        if "." in threshold and "%" not in threshold:
            self.general_error(
                msg,
                "Invalid threshold input (no decimals in prices please).",
                "Please check your command and try again. Note: `.eft track help` is your friend",
            )
            return
        # Validate the input specifically for the channel
        dc = DiscordCustom(self._bot)
        if not channel in dc.get_all_text_channels(
            chatutils.guild_id(msg), names_only=True
        ):
            self.general_error(
                msg,
                f"Invalid channel input: `{channel}`",
                "The text channel provided cannot be found. Note: `.eft track help` is your friend",
            )
            return

        # Check to ensure the item exists via the tarkov api
        result = self.graph_ql(self.item_query(item))

        # If the result is false, then the request failed
        if not result:
            self.general_error(
                msg,
                "Request Failed",
                "During the request, the Tarkov API returned an error. Please check the logs.",
            )
            return

        # Get the first result from the query
        try:
            result_data = result["data"]["itemsByName"][0]
        except IndexError:
            self.general_error(
                msg, "Not found", "The item you requested was not found."
            )
            return

        # Write the item to track to the database
        write_result = dynamo.write(
            EftTrackerTable(
                server_id=server_id,
                item=item,
                threshold=threshold,
                channel=channel,
                handle=chatutils.mention_user(msg),
            )
        )

        if write_result:
            body = f"I will post to the `#{channel}` channel when this alert triggers\n"
            body += f"To remove this alert, use `.eft untrack {item}`\n\n"
            if channel == "general":
                # If the general channel was used, add a note to the body
                body += f"> Note: Use the `.eft track help` command to set your alert channel"
            self.send_card(
                title=f"✅ Tracking `{result_data['name']}`",
                body=body,
                color=chatutils.color("white"),
                in_reply_to=msg,
                thumbnail=result_data["iconLink"],
                fields=(
                    ("Item:", result_data["name"]),
                    ("Threshold:", threshold),
                ),
            )
            return
        else:
            return f"❌ Failed to track {item}!"

    @botcmd
    def eft_help(self, msg, args):
        """
        Returns a simple help command for the main .eft function
        """
        body = "**💡 About:**\n"
        body += "**errbot** comes with several plugins to help you with Escape from Tarkov!\n\n"
        body += (
            "• `.eft <item>` - Get current information about an item and its prices\n"
        )
        body += "• `.eft ammo <ammo_type>` - Get an ammo type sorted by its performance tier\n"
        body += "• `.eft map <map>` - Have a map returned in chat and info about its location\n"
        body += "• `.eft time` - Get the current time in Tarkov\n"
        body += (
            "• `.eft status` - Get the current status of Escape from Tarkov servers\n\n"
        )
        body += "• `.eft track --item <item> --threshold <threshold> --channel <channel>` - Track an item and alert you when it rises to a price or by a certain percentage\n"
        body += "• `.eft untrack <item> - Untrack an item being tracked for price alerts (use the same name you entered it with)\n"
        body += "**📓 Examples:**\n\n"
        body += "• `.eft ammo help` - View the help command for `.eft ammo`\n"
        body += (
            "• `.eft ammo 7.62x51mm` - Get information about the 7.62x51mm ammo type\n"
        )
        body += "• `.eft map help` - View the help command for `.eft map`\n"
        body += "• `.eft map shoreline` - Get the shoreline map and its details\n"
        body += "• `.eft watch` - Get price info for the 'Roler Submariner gold wrist watch'\n"
        body += "• `.eft track --item m4a1 --threshold 20000 --channel general` - Track the m4a1 and alert you in the general channel when its price rises to the threshold\n"
        body += "• `.eft track --item m4a1 --threshold 10% --channel general` - Track the m4a1 and alert you in the general channel when its price rises by 10%\n"
        body += "• `.eft untrack m4a1` - Stop tracking the m4a1 for price alerts (if you have alerts set)\n"
        body += "• `.eft tracking` - Display all tracked eft items\n"

        # Send the eft help card
        self.send_card(
            title=".eft help command",
            body=body,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

    @botcmd
    def eft(self, msg, args):
        """
        Get the price of an item from Escape From Tarkov.

        Syntax: .eft <item name>
        Example: .eft gas an -> will get the price of a Gas Analyzer
        """
        ErrHelper().user(msg)

        # Set the type of args to a string
        item = str(args).strip().lower()

        # Validate the input
        if not self.input_validation(item):
            self.general_error(
                msg, "Invalid input.", "Please check your command and try again."
            )
            return

        # If we don't have the cached item_names or its not fresh, fetch it
        if (
            not self.item_names
            or self.eft_cache_time is None
            or util.is_timestamp_older_than_n_seconds(
                self.eft_cache_time, EFT_CACHE_TIME
            )
            == True
        ):
            self.refresh_eft_data()

        # Hardcoded name overrides for popular items
        item, hard_coded = self.item_hard_code_replacer(item)

        item_matches = util.close_matches(item, self.item_names, cutoff=0.5)

        alt_matches = None
        # If we have a single match from our cache, use that
        if len(item_matches) == 1:
            if not hard_coded:
                item = item_matches[0]
        # If we have multiple matches, use the first one and make note of the others
        elif len(item_matches) > 1:
            if not hard_coded:
                item = item_matches[0]
            alt_matches = "\n• " + "\n• ".join(item_matches[1:4])

        # Execute the graphql query to try and get eft item data
        result = self.graph_ql(self.item_query(item))

        # If the result is false, then the request failed
        if not result:
            self.general_error(
                msg,
                "Request Failed",
                "During the request, the Tarkov API returned an error. Please check the logs.",
            )
            return

        # Get the first result from the query
        try:
            result_data = result["data"]["itemsByName"][0]
        except IndexError:
            message = f"The item you requested `{args}` was not found."
            if alt_matches:
                message += f"I found some similar items: {alt_matches}"
            self.general_error(
                msg, "Not found", message
            )
            return

        # Format the types to be wrapped in backticks to look pretty
        types = self.fmt_item_types(result_data)

        # Get the highest trader price and the trader name
        highest_price, trader = self.get_highest_trader_price(result_data)

        # Get item 'tier'
        item_tier = self.get_item_tier(highest_price, result_data)

        # Send a successful card with the eft item data
        body = ""
        body += f"**Price and Item Details:**\n"
        body += f"• Wiki: {result_data['link']}\n"
        body += f"• Item Tier: {item_tier['msg']}\n"
        body += f"• Sell to: `{trader}` for `{self.fmt_number(highest_price)}`\n"
        
        if alt_matches:
            body += f"\n**Other items with similar names:**{alt_matches}\n"

        # Get Average Flea Price
        if result_data["avg24hPrice"] == 0:
            flea_price = "N/A"
        else:
            flea_price = self.fmt_number(result_data["avg24hPrice"])

        # Send a successful card with the eft item data
        self.send_card(
            title=result_data["name"],
            body=body,
            color=item_tier["color"],
            in_reply_to=msg,
            thumbnail=result_data["iconLink"],
            fields=(
                ("Avg Flea Price:", flea_price),
                ("Base Price:", self.fmt_number(result_data["basePrice"])),
                (
                    "Change Last 48h:",
                    self.get_price_change(result_data["changeLast48hPercent"]),
                ),
                ("Price Per Grid:", item_tier["price_per_grid"]),
                ("Item Types:", types),
            ),
        )
        return

    @botcmd()
    def eft_status(self, msg, args):
        """
        Get the status of Escape from Tarkov

        Example: .eft status
        Example: .eft status --messages
        """
        ErrHelper().user(msg)

        # Get the status of the Tarkov servers from the graphql API
        result = self.graph_ql(self.status_query())

        # If the result is false, then the request failed
        if not result:
            self.general_error(
                msg,
                "Request Failed",
                "During the request, the Tarkov API returned an error. Please check the logs.",
            )
            return

        # Get the statuses from the query
        try:
            statuses = result["data"]["status"]["currentStatuses"]
        except TypeError:
            self.general_error(
                msg,
                "GraphQL Parsing Error",
                "Failed to parse GraphQL response. Please check the logs.",
            )
            return

        # If the user provided the --messages flag, then send a message with the status
        if "--messages" in args:
            # Check if eft has posted any messages about server statuses
            body = "Status Messages:\n"
            try:
                messages = result["data"]["status"]["messages"]
                for message in messages:
                    if message["solveTime"] == None:
                        resolved = False
                    else:
                        resolved = True
                    body += f"• Message: {message['content']} | Time: {message['time'].split('+')[0]} | Resolved: {resolved}\n"
            # If an error was thrown, then the messages were not found
            except IndexError:
                body = "Current Server Statuses:\n"
        else:
            body = "Current Server Statuses:\n"

        # Check the overall status of all Tarkov servers
        eft_issues = False
        eft_issues_dict = {}
        for status in statuses:
            if status["status"] != 0:
                eft_issues = True
                eft_issues_dict[status["name"]] = "🔴"
            else:
                eft_issues_dict[status["name"]] = "🟢"

        # Format all the embed fields
        fields = tuple([(k, v) for k, v in eft_issues_dict.items()])

        # Set the color of the card based on if there are any detected issues or not
        if eft_issues:
            color = chatutils.color("red")
        else:
            color = chatutils.color("green")

        # Send a card with status info for eft
        self.send_card(
            title="Escape From Tarkov Status",
            body=body,
            color=color,
            in_reply_to=msg,
            fields=fields,
        )

        # Check to see if the message was send from a guild or a DM
        guild_id = chatutils.guild_id(msg)
        if not guild_id:
            yield "⚠️ To view the DownDetector status, please use this command in a channel, not a DM."
            return
        else:
            yield "**DownDetector Status:**"

        # Get and send a screenshot of the eft downdetector chart
        chart_file, status = downdetector.chart("escape-from-tarkov")
        if not chart_file:
            yield "❌ Failed to get chart from DownDetector"
            return

        yield status

        dc = DiscordCustom(self._bot)
        channel_id = chatutils.channel_id(msg)
        dc.send_file(channel_id, chart_file)
        # Remove the chart file after it has been uploaded
        time.sleep(5)
        os.remove(chart_file)
        return

    @botcmd()
    def eft_map(self, msg, args):
        """
        Get HD Tarkov maps right in chat

        Run ".eft map help" to get all available maps

        Example: .eft map shoreline
        Syntax: .eft map <map_name>
        """
        ErrHelper().user(msg)

        # Check to see if the message was send from a guild or a DM
        guild_id = chatutils.guild_id(msg)
        if not guild_id:
            return "⚠️ Please use this command in a channel, not a DM."

        # Format the args as lower-case and stripped
        args = args.lower().strip()

        # If the help command is called, show the ammo help card
        if args == "help":
            return self.map_help(msg)

        # Get a list of all maps
        maps = []
        for map in MAPS:
            maps.append(map["name"])

        # Search the args for a matching map from the map list
        map_matches = util.close_matches(args, maps)

        # If there are no matching maps, return an error message
        if len(map_matches) == 0:
            return self.general_error(
                msg,
                "Invalid map",
                "You can view all maps with:\n`.eft map help`",
            )
        # If there are more than one matching maps, return an error message
        elif len(map_matches) > 1:
            matches_fmt = "\n• ".join(map_matches)
            return self.general_error(
                msg,
                "Multiple matching maps",
                f"Please refine your map search query since more than one map matched your request.\n\n**Matching Maps:**\n• {matches_fmt}\n\nYou can view all available maps with: `.eft map help`",
            )
        # If there is exactly one match, grab it from the list and carry on
        elif len(map_matches) == 1:
            map = map_matches[0]

        # Get the map data from the matching map
        for item in MAPS:
            if item["name"] == map:
                map_data = item

        # Post the map file
        dc = DiscordCustom(self._bot)
        channel_id = chatutils.channel_id(msg)
        dc.send_file(channel_id, f"{MAP_DIR}/{map}.jpg")

        # Format a message with map data
        message = f"**{map.capitalize()} Details:**"
        message += f"\n• Players: `{map_data['players']}`"
        message += f"\n• Duration: `{map_data['duration']}`"

        # If the map is factory, set the time to static values
        if map == "factory":
            left = "15:00"
            right = "03:00"
        # Else, get the current time in Tarkov
        else:
            time = util.utc_milli_timestamp()
            left = self.real_time_to_tarkov_time(time, left=True)
            right = self.real_time_to_tarkov_time(time, left=False)

        message += f"\n• Time: `{left}` - `{right}`"

        return message

    @botcmd()
    def eft_ammo(self, msg, args):
        """
        Get information about an ammo type

        Run ".eft ammo help" to get all available ammo types

        Example: .eft ammo 7.62x51mm
        Syntax: .eft ammo <ammo_type>
        """
        ErrHelper().user(msg)

        # Format the args as lower-case and stripped
        args = args.lower().strip()

        # If the help command is called, show the ammo help card
        if args == "help":
            return self.ammo_help(msg)

        ### custom logic for short char length matches ###
        if "acp" in args.lower():
            ammo_matches = [".45 ACP"]
        elif "366" in args or "tkm" in args.lower():
            ammo_matches = [".366 TKM"]
        else:
            # Get a list of matching ammo types from the query
            ammo_matches = util.close_matches(args, AMMO_TYPES, cutoff=0.6)

        # If there are no matching ammo types, return an error message
        if len(ammo_matches) == 0:
            return self.general_error(
                msg,
                "Invalid ammo type",
                "You can view all ammo types with:\n`.eft ammo help`",
            )
        # If is one or greater matches, grab the first (closest) match and carry on
        elif len(ammo_matches) >= 1:
            ammo_type = ammo_matches[0]

        # If we don't have the cached ammo_data or its not fresh, fetch it
        if (
            not self.ammo_data
            or self.eft_cache_time is None
            or util.is_timestamp_older_than_n_seconds(
                self.eft_cache_time, EFT_CACHE_TIME
            )
            == True
        ):
            self.refresh_eft_data()

        # Loop through and collect data on the selected ammo type
        ammo_list = []
        for item in self.ammo_data.items():
            if ammo_type.lower() in item[1]["name"].lower():
                ammo_list.append(
                    {
                        "name": item[1]["shortName"],
                        "penetration": item[1]["ballistics"]["penetrationPower"],
                        "damage": item[1]["ballistics"]["damage"],
                        "armorDamage": item[1]["ballistics"]["armorDamage"],
                        "penchance": item[1]["ballistics"]["penetrationChance"],
                    }
                )

        # Sort the ammo list by highest penetration power
        ammo_list_sorted = sorted(
            ammo_list, key=lambda x: x["penetration"], reverse=True
        )

        # Format the body of the card to send with a table of ammo data
        body = "```Name         Pen  Dmg  Armor  Pen %\n"
        for ammo in ammo_list_sorted:
            name = ammo["name"]
            if len(name) > 10:
                name = name[0:10] + ".."
            body += f"{name: <12} {ammo['penetration']: <4} {ammo['damage']: <4} {ammo['armorDamage']: <6} {round(ammo['penchance'] * 100, 2)}%\n"
        body += "```"

        # Send the ammo card with the ammo data
        self.send_card(
            title=ammo_type,
            body=body.strip(),
            color=chatutils.color("white"),
            in_reply_to=msg,
            # thumbnail=result_data["iconLink"],
        )
        return

    @botcmd()
    def eft_time(self, msg, args):
        """
        Get the current time in Tarkov
        Example: .eft time
        """
        ErrHelper().user(msg)

        # Get the current time in Tarkov
        time = util.utc_milli_timestamp()
        left = self.real_time_to_tarkov_time(time, left=True)
        right = self.real_time_to_tarkov_time(time, left=False)

        return f"🕒 `{left}` - `{right}`"

    def real_time_to_tarkov_time(self, time, left=True):
        """
        Convert real time to Tarkov time
        :param time: Current UTC epoch in milliseconds -> int(datetime.datetime.utcnow().timestamp()) * 1000
        :param left: True if left side, False if right side (Think eft in-game clock)
        :return: String of the time in the following format: %H:%M:%S
        """

        # tarkov time moves at 7 seconds per second.
        # surprisingly, 00:00:00 does not equal unix 0... but it equals unix 10,800,000.
        # Which is 3 hours. What's also +3? Yep, Russia. UTC+3.
        # therefore, to convert real time to tarkov time,
        # tarkov time = (real time * 7 % 24 hr) + 3 hour

        one_day = util.hrs_to_milliseconds(24)
        russia = util.hrs_to_milliseconds(3)

        if left:
            offset = russia
        else:
            offset = russia + util.hrs_to_milliseconds(12)

        tarkov_time = datetime.fromtimestamp(
            (((offset + (time * TARKOV_RATIO)) % one_day) / 1000)
        )
        return tarkov_time.strftime("%H:%M:%S")

    def item_hard_code_replacer(self, item):
        """
        Hard coded helper function (ew) to replace and find matches on common eft items
        :param item: a string of the item name to check for hard coded replacements
        :return: a string of the item name, could be altered, or the same
        :return bool: True if the item was replaced, False if not
        Example: "lab red keycard" -> "TerraGroup Labs keycard (Red)"
        """
        # Hard coded replacements
        if "lab" in item or "keycard" in item or "key card" in item:
            if "red" in item:
                return "TerraGroup Labs keycard (Red)", True
            elif "blue" in item:
                return "TerraGroup Labs keycard (Blue)", True
            elif "green" in item:
                return "TerraGroup Labs keycard (Green)", True
            elif "yellow" in item:
                return "TerraGroup Labs keycard (Yellow)", True
            elif "violet" in item:
                return "TerraGroup Labs keycard (Violet)", True
            elif "black" in item:
                return "TerraGroup Labs keycard (Black)", True
        if item == "gpu":
            return "Graphics card", True
        
        # If no matches are found, return the original item name
        return item, False

    def refresh_eft_data(self):
        """
        Helper function to refresh static eft data from GitHub - That can be cached in memory
        :return bool: True is successful, False if not
        """
        try:
            # Update static ammo data
            self.ammo_data = requests.get(
                "https://raw.githubusercontent.com/TarkovTracker/tarkovdata/master/ammunition.json"
            ).json()
            # Update static item data
            self.item_data = requests.get(
                "https://raw.githubusercontent.com/TarkovTracker/tarkovdata/master/items.en.json"
            ).json()

            item_names = []
            for _, value in self.item_data.items():
                item_names.append(value['name'].encode('ascii', 'ignore').decode('ascii'))
            self.item_names = item_names

            # Update cache
            self.eft_cache_time = util.parse_iso_timestamp(util.iso_timestamp())

            self.log.info("eft cache data successfully refreshed")

            return True
        except Exception as error:
            ErrHelper().capture(error)
            self.log.error("failed to refresh the eft cache")
            return False

    def map_help(self, msg):
        """
        Show the help command to view all the available maps
        :param msg: The message object
        :return: None - Sends a card in reply to the message with the maps that can be used
        """
        # Get the list of maps
        map_list = []
        for map in MAPS:
            map_list.append(map["name"])

        # Format the body of the message with the maps
        body = "**Available Maps:**\n"
        body += "• " + "\n • ".join(map_list)

        # Send the ammo help card
        self.send_card(
            title="Map Help Command",
            body=body,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

    def ammo_help(self, msg):
        """
        Show the help command to view all the available ammo types
        :param msg: The message object
        :return: None - Sends a card in reply to the message with the ammo types that can be used
        """
        # Format the body of the message with the ammo types
        body = "**Available Ammo Types:**\n"
        body += "• " + "\n • ".join(AMMO_TYPES)
        body += "\n\n**Ammo Table Key**:"
        body += "\n• `Pen` - Penetration Power"
        body += "\n• `Dmg` - Damage"
        body += "\n• `Armor` - Armor Damage"
        body += "\n• `Pen %` - Armor Penetration Chance"

        # Send the ammo help card
        self.send_card(
            title="Ammo Help Command",
            body=body,
            color=chatutils.color("white"),
            in_reply_to=msg,
        )

    def get_item_tier(self, highest_price, result_data):
        """
        Get the 'tier' of the item (color and tier)
        :param highest_price: The highest price (int) the item sells for
        :return: A dict of the item tier data
        """

        # Calculate the price per grid unit
        try:
            price_per_grid = int(highest_price) / (
                int(result_data["width"]) * int(result_data["height"])
            )

            if price_per_grid >= 25000:
                color = chatutils.color("yellow")
                tier_msg = "⭐ Legendary ⭐"
            elif price_per_grid >= 12500:
                color = chatutils.color("green")
                tier_msg = "🟢 Great"
            elif price_per_grid >= 8000:
                color = chatutils.color("blue")
                tier_msg = "🔵 Average"
            else:
                color = chatutils.color("red")
                tier_msg = "🔴 Poor"

            price_per_grid = self.fmt_number(price_per_grid)
        except ZeroDivisionError:
            color = chatutils.color("white")
            tier_msg = "❓ N/A"
            price_per_grid = "N/A"

        return {
            "color": color,
            "price_per_grid": price_per_grid,
            "msg": tier_msg,
        }

    def get_highest_trader_price(self, result_data):
        """
        Helper function for getting the highest trader price.
        :param result_data: The result of the graphql query
        :return: The highest trader price (int) and the trader name (string)
        """
        highest_price = 0
        trader = ""
        for price in result_data["sellFor"]:
            if price["price"] > highest_price:
                highest_price = int(price["price"])
                trader = str(price["source"])
        return highest_price, trader

    def fmt_number(self, number):
        """
        Helper function to format a number to a string with commas.
        :param number: The number to format (int)
        :return: The formatted number (string)
        """
        return "{:,}".format(number)

    def get_price_change(self, price_change):
        """
        Helper function for formatting the price change.
        :param price_change: The price change (float)
        :return: The formatted price change (string)
        """
        if not price_change:
            return "N/A"

        if price_change > 0:
            return f"{price_change}% 📈"
        elif price_change < 0:
            return f"{price_change}% 📉"
        else:
            return "0%"

    def input_validation(self, args):
        """
        Helper function for validating the user input.
        :param args: The user input (string)
        :return: True if the input is valid, False if not
        """
        # Character Allow List
        regex = r"^[a-zA-Z\d\()\s-]+$"

        # If there is a match the input is valid and we can return true
        if re.match(regex, args):
            return True
        # If there is no match, the input is invalid and we can return false
        else:
            return False

    def graph_ql(self, query):
        """
        Helper function for executing a graphql query to the Tarkov API.

        :param query: The query to execute (string)
        :return: The result of the query (dict)
        :return: False if the request failed
        """
        response = requests.post(
            "https://tarkov-tools.com/graphql", json={"query": query}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def fmt_item_types(self, result_data):
        """
        Takes a list of eft item types and returns it as a string with backticks
        :param result_data: The result of the graphql query
        :return: The formatted types (string)
        """
        types = ""
        for type in result_data["types"]:
            types += "`" + type + "`, "
        types = types[:-2]
        return types

    def eft_tracker_alert(self, record):
        """
        Main function for processing an eft tracker record for alerting on price changes
        :param record: The database record to parse for item tracking
        :return: None
        """
        # Get the most recent data for the item via the tarkov api
        result = self.graph_ql(self.item_query(record["item"]))

        # If the result is false, then the request failed
        if not result:
            self.log.error("Failed to get item data from the tarkov api in the cron")
            return

        # Get the first result from the query
        try:
            result_data = result["data"]["itemsByName"][0]
        except IndexError:
            self.info.error("failed to find item in tarkov cron")
            return

        alert = False
        # Check the alert type (price or percentage)
        if "%" in record["threshold"]:
            alert_type = "%"
            if float(result_data["changeLast48hPercent"]) >= float(
                record["threshold"].replace("%", "")
            ):
                alert = True
        else:
            alert_type = "₽"
            if float(result_data["avg24hPrice"]) >= float(record["threshold"]):
                alert = True

        # If there is not an alert, return
        if not alert:
            return

        # If there is an alert, then send the alert
        if alert:
            try:
                # If the alert fired, remove the record from the database
                delete_result = dynamo.delete(
                    dynamo.get(
                        EftTrackerTable, int(record["server_id"]), record["item"]
                    )
                )
                if not delete_result:
                    self.log.error(
                        "Failed to delete tarkov tracker item from the database"
                    )
                    return
            except Exception as e:
                ErrHelper().capture(e)
                return

            # Format the alert
            title = f"🔔 Price Alert: `{record['item']}`"
            body = f"**Item:** `{record['item']}` has crossed the threshold of `{record['threshold'].replace('%', '')}{alert_type}`!\n"
            if alert_type == "₽":
                body += f"**Condition:** `{self.fmt_number(result_data['avg24hPrice'])}₽` (current) >= `{record['threshold']}{alert_type}` (threshold)\n"
            elif alert_type == "%":
                body += f"**Condition:** item % price change `{result_data['changeLast48hPercent']}%` (current) has increased more than `{record['threshold']}` (threshold)\n"
            body += f"**User:** {record['handle']}\n"
            color = chatutils.color("yellow")
            thumbnail = result_data["iconLink"]
            fields = (
                ("Item:", record["item"]),
                (f"Threshold ({alert_type}):", record["threshold"]),
                ("Price:", self.fmt_number(result_data["avg24hPrice"])),
            )

            # Send the alert
            if BACKEND == "discord":
                self.send_card(
                    title=title,
                    body=body,
                    color=chatutils.color("yellow"),
                    to=self.build_identifier(
                        f"#{record['channel']}@{record['server_id']}"
                    ),
                    thumbnail=thumbnail,
                    fields=fields,
                )
            elif BACKEND == "slack":
                self.send_card(
                    title=title,
                    body=body,
                    color=color,
                    to=self.build_identifier(f"#{record['channel']}"),
                    thumbnail=thumbnail,
                    fields=fields,
                )

    def status_query(self):
        """
        Get the query structure for asking the tarkov-tools GraphQL for the eft status
        :return: String of the query structure for the status command
        """
        return """
            {
                status {
                    currentStatuses {
                        name
                        message
                        status
                    },
                    messages {
                        time
                        type
                        content
                        solveTime
                    }
                }
            }
        """

    def item_query(self, name):
        """
        Helper function for building the graphql query for an eft item.
        """
        query = Template(
            """
            {
                itemsByName(name: "$name") {
                    name
                    types
                    avg24hPrice
                    basePrice
                    width
                    height
                    changeLast48hPercent
                    iconLink
                    link
                    sellFor {
                        price
                        source
                    }
                }
            }
            """
        )
        return query.substitute(name=name)

    def general_error(self, src_msg, title, msg):
        """
        Helper function for sending a general error card.
        """
        self.send_card(
            title=title,
            body=msg,
            color=chatutils.color("red"),
            in_reply_to=src_msg,
        )
