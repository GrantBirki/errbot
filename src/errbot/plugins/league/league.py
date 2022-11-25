import json
import os
import random
from urllib.error import HTTPError

import requests
from errbot import BotPlugin, arg_botcmd, botcmd
from lib.chat.chatutils import ChatUtils
from lib.common.utilities import Util
from lib.database.dynamo import Dynamo
from lib.common.errhelper import ErrHelper
from lib.database.dynamo_tables import LeagueTable
from riotwatcher import ApiError, LolWatcher

# Get the RIOT_TOKEN and ensure it is a string and not a bytestring
RIOT_TOKEN = os.environ.get("RIOT_TOKEN", None)

# If the RIOT_TOKEN is not set, do not continue
if RIOT_TOKEN:
    if isinstance(RIOT_TOKEN, bytes):
        RIOT_TOKEN = RIOT_TOKEN.decode("utf-8").replace("\n", "").strip()
    LOL_WATCHER = LolWatcher(RIOT_TOKEN, timeout=15)
    REGION = os.environ["RIOT_REGION"]
    RIOT_REGION_V5 = os.environ["RIOT_REGION_V5"]
    chatutils = ChatUtils()
    util = Util()
    dynamo = Dynamo()
    BACKEND = os.environ["BACKEND"]

    # Load the responses from disk into memory as a global variable
    with open("plugins/league/responses.json", "r") as raw:
        RESPONSES = json.loads(raw.read())

    # Load the queue id data from disk into memory as a global variable
    with open("plugins/league/queue_id_cache.json", "r") as raw:
        QUEUE_ID_CACHE = json.loads(raw.read())

    # Query the league API to get the current version of league
    LEAGUE_VERSION = json.loads(
        requests.get("https://ddragon.leagueoflegends.com/realms/na.json").text
    )["n"]["champion"]
    # Get the latest champion data and save it to memory as a global variable
    CHAMPION_DATA = json.loads(
        requests.get(
            f"https://ddragon.leagueoflegends.com/cdn/{LEAGUE_VERSION}/data/en_US/champion.json",
            timeout=10,
        ).text
    )["data"]

    # Specify the default league channel to use in discord
    LEAGUE_CHANNEL = "#league"

    # last_match_cron interval
    INTERVAL = 90  # seconds


class League(BotPlugin):
    """
    League plugin for Errbot

    Add yourself to the 'league' watcher, and you'll get a message every time you play a game.
    You can also view your data, your last game, and more!
    """

    def activate(self):
        """
        Runs the last_match_cron() function every interval

        Note: the self.start_polling() function will wait for the first cron job to finish before starting the next one
        """
        # If the RIOT_TOKEN is not set, deactivate the plugin
        if RIOT_TOKEN is None:
            self.log.warn(
                "RIOT_TOKEN not found in environment variables. Disabling the League plugin."
            )
            super().deactivate()
        else:
            super().activate()
            disabled = os.environ.get("DISABLE_LEAGUE_CRON", False)
            if disabled.lower().strip() == "true":
                self.log.warn("League cron disabled for local testing")
            else:
                self.start_poller(INTERVAL, self.last_match_cron)

    @botcmd(admin_only=True)
    def league_disable(self, msg, args):
        """
        Disable the league cron
        """
        ErrHelper().user(msg)
        if len(self.current_pollers) == 0:
            return "⚠ League cron already disabled"
        else:
            self.stop_poller(self.last_match_cron)
            return "🔴 League cron disabled"

    @botcmd(admin_only=True)
    def league_enable(self, msg, args):
        """
        Enable the league cron
        """
        ErrHelper().user(msg)
        if len(self.current_pollers) == 0:
            self.start_poller(INTERVAL, self.last_match_cron)
            return "🟢 League cron enabled"
        else:
            return "⚠ League cron already enabled"

    def last_match_cron_main(self, item):
        # Gets the last match data

        # Query the RIOT API for a list of all matches for the summoner
        match_list = self.get_summoner_match_list(item["puuid"])

        # Calcutes a unique hash of the last matches for a summoner
        current_matches_sha256 = util.sha256(json.dumps(match_list))
        # Checks if the last match data is already in the database
        if item.get("last_match_sha256", None) == current_matches_sha256:
            # Uncomment the line below for extra verbose logs as the league cron runs
            # self.log.info(
            #     f"skipping... last: {item.get('last_match_sha256', None)[:8]} | current: {current_matches_sha256[:8]} | {item['summoner_name']}"
            # )
            return "duplicate_sha"

        # Grab only the most recent match [0]
        last_match = match_list[0]

        # Query the RIOT API for the full match data for a given gameId
        match_data_full = self.get_match_data(last_match)

        # Parse the output of the last match and use the puuid to get exact summoner data for the match (no API call)
        match_data_summoner = self.find_summoner_specific_match_data(
            match_data_full, item["puuid"]
        )

        # Return the summoner specific data and the full match data
        match_data = {"summoner": match_data_summoner, "full": match_data_full}

        if not match_data["summoner"]:
            # summoner_name was not found so we skip it
            self.log.error(f"error getting game data for {item['summoner_name']}")
            return False

        # Get the Discord Server guild_id
        guild_id = int(item["discord_server_id"])

        # Updates the match sha so results for a match are never posted twice
        get_result = dynamo.get(LeagueTable, guild_id, item["discord_handle"])

        if get_result:

            # Check and update the win/loss streak
            if get_result.win_streak is not None:
                last_win_streak = get_result.win_streak
            else:
                last_win_streak = 0
            if get_result.loss_streak is not None:
                last_loss_streak = get_result.loss_streak
            else:
                last_loss_streak = 0

            if match_data["summoner"]["win"]:
                win_streak = last_win_streak + 1
                loss_streak = 0
            else:
                win_streak = 0
                loss_streak = last_loss_streak + 1

            # Update the win/loss streak in the match_data dict for message display later on
            match_data["win_streak"] = win_streak
            match_data["loss_streak"] = loss_streak

            # Update the DynamoDB entry
            update_result = dynamo.update(
                table=LeagueTable,
                record=get_result,
                fields_to_update=[
                    LeagueTable.last_match_sha256.set(current_matches_sha256),
                    LeagueTable.win_streak.set(win_streak),
                    LeagueTable.loss_streak.set(loss_streak),
                ],
            )
        else:
            ErrHelper().capture(
                f"❌ Something went wrong finding a db entry for `{item['summoner_name']}`"
            )
            self.log.error(
                f"error processing game: {current_matches_sha256[:8]} | {item['summoner_name']}"
            )
            return False

        if update_result:
            # Sends a message to the user's discord channel which they registered with
            message_data = self.league_message(match_data)
            if message_data["win"] == True:
                color = chatutils.color("green")
            else:
                color = chatutils.color("red")

            if BACKEND == "discord":
                chatutils.send_card_helper(
                    bot_self=self,
                    to=self.build_identifier(f"{LEAGUE_CHANNEL}@{guild_id}"),
                    title=f"Last Match For: `{item['summoner_name']}`",
                    body=message_data["message"],
                    color=color,
                )
            elif BACKEND == "slack":
                chatutils.send_card_helper(
                    bot_self=self,
                    to=self.build_identifier(f"{LEAGUE_CHANNEL}"),
                    title=f"Last Match For: `{item['summoner_name']}`",
                    body=message_data["message"],
                    color=color,
                )
        else:
            ErrHelper().capture(
                f"❌ Something went wrong posting/updating the db record for`{item['summoner_name']}`"
            )
            self.log.error(
                f"error processing game: {current_matches_sha256[:8]} | {item['summoner_name']}"
            )
            return False

        # Item processed so we can return true
        self.log.info(
            f"processed game: {current_matches_sha256[:8]} | {item['summoner_name']}"
        )
        return True

    def last_match_cron(self):
        """
        Last match function on a schedule! Posts league stats
        """
        db_items = dynamo.scan("league")
        for item in db_items:
            try:
                self.last_match_cron_main(item)
            except requests.exceptions.HTTPError as e:
                self.log.error(f"HTTPError: {e}")
                continue
            except requests.exceptions.ConnectionError as e:
                self.log.error(f"ConnectionError: {e}")
                continue
            except HTTPError as e:
                self.log.error(f"ConnectionError: {e}")
                continue
            except Exception as e:
                if "503 server error" in str(e).lower():
                    self.log.error(f"503 server error: {e}")
                    continue
                else:
                    ErrHelper().capture(e)
                    self.log.error(f"error: {e}")
                    continue

    @arg_botcmd("summoner_name", type=str)
    def add_me_to_league_watcher(self, msg, summoner_name=None):
        """
        Adds a summoner to the league watcher

        Usage: .add me to league watcher <summoner_name>
        Example: .add me to league watcher birki
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        discord_handle = chatutils.handle(msg)
        guild_id = chatutils.guild_id(msg)

        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        get_result = dynamo.get(LeagueTable, guild_id, discord_handle)
        if get_result:
            return f"ℹ️ {chatutils.mention_user(msg)} already has an entry in the league watcher!"
        elif get_result is False:
            return f"❌ Failed to check the league watcher for {chatutils.mention_user(msg)}"

        # Runs a quick check against the Riot API to see if the summoner_name entered is valid
        puuid = self.get_summoner_puuid(summoner_name)
        if not puuid:
            return f"❌ Summoner `{summoner_name}` not found in the Riot API! Check your spelling and try again.."

        write_result = dynamo.write(
            LeagueTable(
                discord_server_id=guild_id,
                discord_handle=discord_handle,
                summoner_name=summoner_name,
                puuid=puuid,
            )
        )

        if write_result:
            return f"✅ Added {chatutils.mention_user(msg)} to the league watcher!"
        else:
            return (
                f"❌ Failed to add {chatutils.mention_user(msg)} to the league watcher!"
            )

    @botcmd
    def league_streak(self, msg, args):
        """
        Display's your summoner's win/loss streak
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        if args.strip() != "" and args != "me":
            return "What you are trying to do is not implemented yet"

        discord_handle = chatutils.handle(msg)
        guild_id = chatutils.guild_id(msg)

        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        record = dynamo.get(LeagueTable, guild_id, discord_handle)
        if record is False:
            return f"❌ Failed to check the league watcher for {chatutils.mention_user(msg)}"
        elif record is None:
            return f"❌ {chatutils.mention_user(msg)} is not in the league watcher!"

        if record.win_streak is None or record.loss_streak is None:
            return f"❌ {chatutils.mention_user(msg)} has no win/loss streak data yet! Go play a game!"

        match_data = {
            "win_streak": record.win_streak,
            "loss_streak": record.loss_streak,
        }

        return f"{chatutils.mention_user(msg)} {self.get_streak(match_data)}"

    @arg_botcmd("--summoner", dest="summoner", type=str, admin_only=True)
    @arg_botcmd("--discord", dest="discord", type=str, admin_only=True)
    @arg_botcmd("--guild", dest="guild", type=int, admin_only=True)
    def add_to_league_watcher(self, msg, summoner=None, discord=None, guild=None):
        """
        Adds a summoner to the league watcher - Admin command
        Run from the channel you wish to use the league watcher in

        Usage: .add to league watcher <summoner> <discord> <guild>
        Example: .add to league watcher --summoner birki --discord birki#0001 --guild 12345
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        guild_id = int(guild)

        get_result = dynamo.get(LeagueTable, guild_id, discord)
        if get_result:
            return f"ℹ️ `{discord}` already has an entry in the league watcher!"
        elif get_result is False:
            return f"❌ Failed to check the league watcher for `{discord}`"

        # Runs a quick check against the Riot API to see if the summoner_name entered is valid
        puuid = self.get_summoner_puuid(summoner)
        if not puuid:
            return f"❌ Summoner `{summoner}` not found in the Riot API! Check your spelling and try again.."

        write_result = dynamo.write(
            LeagueTable(
                discord_server_id=guild_id,
                discord_handle=discord,
                summoner_name=summoner,
                puuid=puuid,
            )
        )

        if write_result:
            return f"✅ Added `{discord}` to the league watcher!"
        else:
            return f"❌ Failed to add `{discord}` to the league watcher!"

    @arg_botcmd("--guild", dest="guild", type=int, admin_only=True)
    @arg_botcmd("--discord", dest="discord", type=str, admin_only=True)
    def remove_from_league_watcher(self, msg, guild=None, discord=None):
        """
        Removes a summoner from the league watcher - Admin command

        Usage: .remove from league watcher <guild> <discord>
        Example: .remove from league watcher --guild 12345 --discord birki#0001
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        guild_id = int(guild)

        get_result = dynamo.get(LeagueTable, guild_id, discord)
        if get_result is None:
            return f"ℹ️ `{discord}` is not in the league watcher!"

        result = dynamo.delete(get_result)

        if result:
            return f"✅ Removed `{discord}` from the league watcher!"
        else:
            return f"❌ Failed to remove `{discord}` to the league watcher!"

    @botcmd
    def remove_me_from_league_watcher(self, msg, args):
        """
        Removes a summoner from the league watcher

        Usage: .remove me from league watcher
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        discord_handle = chatutils.handle(msg)
        guild_id = chatutils.guild_id(msg)

        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        get_result = dynamo.get(LeagueTable, guild_id, discord_handle)
        if get_result is None:
            return f"ℹ️ {chatutils.mention_user(msg)} is not in the league watcher!"

        result = dynamo.delete(get_result)

        if result:
            return f"✅ Removed {chatutils.mention_user(msg)} from the league watcher!"
        else:
            return f"❌ Faile to remove {chatutils.mention_user(msg)} to the league watcher!"

    @botcmd
    def view_my_league_watcher_data(self, msg, args):
        """
        Views your data for the League Watcher

        This is mostly for debugging
        """
        ErrHelper().user(msg)
        if chatutils.locked(msg, self):
            return

        discord_handle = chatutils.handle(msg)
        guild_id = chatutils.guild_id(msg)

        if not guild_id:
            return "Please run this command in a Discord channel, not a DM"

        response = dynamo.get(LeagueTable, guild_id, discord_handle)

        if response:

            if not response.last_match_sha256:
                last_match_sha256 = "Waiting for auto update..."
            else:
                last_match_sha256 = response.last_match_sha256[:8]

            # Get win/loss streak data
            match_data = {
                "win_streak": response.win_streak,
                "loss_streak": response.loss_streak,
            }

            message = f"**League Watcher Data**:\n"
            message += f"• Discord Handle: `{response.discord_handle}`\n"
            message += f"• Summoner Name: `{response.summoner_name}`\n"
            message += f"• Account ID: `{response.puuid[:8]}...`\n"
            message += f"• Win/Loss Streak: `{self.get_streak(match_data)}`\n"
            message += f"• Last Match SHA: `{last_match_sha256}`\n"
            message += f"• Can I fucking @you?: `{response.bot_can_at_me}`\n"
            message += f"• Last Updated: `{response.updated_at}`"

            return message
        else:
            message = f"ℹ️ {chatutils.mention_user(msg)} is not in the league watcher for this Discord server!\n"
            message += "Use `.add me to league watcher <summoner_name>` to add yourself"
            return message

    @arg_botcmd("summoner_name", type=str)
    def lmf(self, msg, summoner_name=None):
        """
        Get the last match for a user (LoL)
        Shortcut for "last_match_for"
        """
        ErrHelper().user(msg)

        # TODO This code is all duplicated of the last_match_for command. No bueno

        if type(summoner_name) is str:
            summoner_list = summoner_name.split(",")

        messages = self.last_match_main(summoner_list)

        for message in messages:
            if message["win"] == True:
                color = chatutils.color("green")
            else:
                color = chatutils.color("red")

            chatutils.send_card_helper(
                bot_self=self,
                title=f"Last Match For: `{message['summoner']}`",
                body=message["message"],
                color=color,
                in_reply_to=msg,
            )

    @arg_botcmd("summoner_name", type=str)
    def last_match_for(self, msg, summoner_name=None):
        """Get the last match for a user (LoL)"""
        ErrHelper().user(msg)

        if type(summoner_name) is str:
            summoner_list = summoner_name.split(",")

        messages = self.last_match_main(summoner_list)

        for message in messages:
            if message["win"] == True:
                color = chatutils.color("green")
            else:
                color = chatutils.color("red")
            chatutils.send_card_helper(
                bot_self=self,
                title=f"Last Match For: `{message['summoner']}`",
                body=message["message"],
                color=color,
                in_reply_to=msg,
            )

    def last_match_main(self, summoner_list):
        """
        Main last match function
        :returns: A string of the messages for a summoner or a list of summoners
        """
        messages = []
        for summoner in summoner_list:
            match_data = self.get_last_match_data(summoner)
            if not match_data["summoner"]:
                messages.append(
                    f"ℹ️ A {summoner} with that ridiculous name was not found!"
                )
            else:
                message = self.league_message(match_data)
                message["summoner"] = summoner
                messages.append(message)

        return messages

    def get_summoner_puuid(self, summoner_name):
        """
        Tries to get a summoner puuid from the Riot API
        [i] API CALL
        """
        try:
            summoner = LOL_WATCHER.summoner.by_name(REGION, summoner_name)
            return summoner["puuid"]
        except ApiError as err:
            if err.response.status_code == 404:
                return None
            else:
                ErrHelper().capture(err)
                raise

    def get_summoner_match_list(self, summoner_puuid):
        """
        Gets a summoners list of previous matches
        [i] API CALL
        """
        try:
            return LOL_WATCHER.match.matchlist_by_puuid(RIOT_REGION_V5, summoner_puuid)
        except Exception as err:
            ErrHelper().capture(err)
            raise

    def get_match_data(self, match_id):
        """
        Gets the exact match data for a summoner given a match ID
        [i] API CALL
        """
        try:
            return LOL_WATCHER.match.by_id(RIOT_REGION_V5, match_id)
        except Exception as err:
            ErrHelper().capture(err)
            raise

    def find_summoner_specific_match_data(self, full_match_data, puuid):
        """
        Parses match data and returns the exact data for a specific summoner

        :param match_details: Full match_data object from self.get_match_data()
        :param puuid: The puuid of the summoner
        """

        # Do some wild list comprehensions to find the summoner's match data
        summoner_specific_match_data = [
            player
            for player in full_match_data["info"]["participants"]
            if player["puuid"] == puuid
        ][0]
        return summoner_specific_match_data

    def get_last_match_data(self, summoner_name):
        """
        Gets the last match data for a summoner
        :returns: a dictionary, with two items: one for the last match data (summoner specific) and one for the full match data (all data)
        """
        # Query the RIOT API for the puuid of the summoner
        puuid = self.get_summoner_puuid(summoner_name)

        # Return None if the account was not found
        if not puuid:
            return None

        # Query the RIOT API for a list of all matchs for the summoner
        match_list = self.get_summoner_match_list(puuid)

        # Grab only the most recent match [0]
        last_match = match_list[0]

        # Query the RIOT API for the full match data for a given gameId
        match_data_full = self.get_match_data(last_match)

        # Parse the output of the last match and use the puuid to get exact summoner data for the match (no API call)
        match_data_summoner = self.find_summoner_specific_match_data(
            match_data_full, puuid
        )

        # Return the summoner specific data and the full match data
        return {"summoner": match_data_summoner, "full": match_data_full}

    def league_message(self, match_data):
        """
        Creates the formatted league message to be displayed in discord
        :param match_data: The last match data ('summoner') or the full match data ('full')
        """
        # Match result (win or loss)
        if match_data["summoner"]["win"] == True:
            message = "• Match Result: `win` 🏆\n"
        else:
            message = "• Match Result: `loss` ❌\n"
        # Match length (##m:##s)
        message += f"• Game Length: `{self.get_league_game_duration(match_data['full']['info']['gameDuration'])}`\n"
        # Match type (Solo, Blind Pick, etc.)
        message += f"• Game Type: `{self.get_queue_type(match_data['full']['info']['queueId'])}`\n"
        # Lane
        message += f"• Lane: `{match_data['summoner']['lane'].lower()}`\n"
        # Champion
        message += (
            f"• Champion: `{self.get_champion(match_data['summoner']['championId'])}`\n"
        )
        # Creep Score (CS)
        message += f"• Creep Score: `{match_data['summoner']['totalMinionsKilled']}`\n"
        # KDA
        kills, deaths, assists = self.get_kda(match_data)
        message += f"• KDA: `{kills}/{deaths}/{assists}`\n"
        # Largest MultiKill
        message += f"• Largest MultiKill: {self.get_largest_multi_kill(match_data)}\n"
        # Win/Loss Streak
        message += f"• Win/Loss Streak: `{self.get_streak(match_data)}`\n"
        # Computed Performance
        perf = self.performance(kills, deaths, assists)
        message += (
            f"• Performance Evaluation: `{perf}` {self.performance_emote(perf)}\n"
        )
        # Random Response Based on Performance
        message += f"> *{self.get_random_response(perf)}*"
        # Return the message and the match result (win/loss)
        return {"message": message, "win": match_data["summoner"]["win"]}

    def get_largest_multi_kill(self, match_data):
        largest_multi_kill = match_data["summoner"]["largestMultiKill"]
        return "⚔️" * largest_multi_kill

    def get_random_response(self, perf):
        """
        Returns a random response from the RESPONSES dictionary
        :param perf: The performance evaluation
        """
        return RESPONSES[perf][random.randrange(0, len(RESPONSES[perf]))]

    def get_kda(self, match_data):
        """
        Gets the KDA for a summoner
        """
        kills = match_data["summoner"]["kills"]
        deaths = match_data["summoner"]["deaths"]
        assists = match_data["summoner"]["assists"]
        return kills, deaths, assists

    def performance(self, kills, deaths, assists):
        """
        Calcualtes the performance of a summoner
        """

        kda_calc = kills - deaths + assists / 2

        if kda_calc >= 8:
            return "excellent"
        elif kda_calc >= 4 and kda_calc < 8:
            return "good"
        elif kda_calc >= 0 and kda_calc < 4:
            return "average"
        elif kda_calc <= 0 and kda_calc > -4:
            return "poor"
        elif kda_calc <= -4:
            return "terrible"

    def performance_emote(self, performance):
        """
        Adds emotes based on summoner performance
        """
        if performance == "excellent":
            return "🌟"
        elif performance == "good":
            return "👍"
        elif performance == "average":
            return "😐"
        elif performance == "poor":
            return "👎"
        elif performance == "terrible":
            return "💀"

    def get_champion(self, champion_id):
        """
        Gets the champion name from the champion ID
        """
        for item in CHAMPION_DATA:
            if int(CHAMPION_DATA[item]["key"]) == int(champion_id):
                return item.lower()
        return None

    def get_streak(self, match_data):
        """
        Get win and loss streak data
        """
        win_streak = match_data.get("win_streak", None)
        loss_streak = match_data.get("loss_streak", None)
        if win_streak is None and loss_streak is None:
            return "unknown"

        if win_streak == None or loss_streak == None:
            return "No Data"
        elif win_streak == 0 and loss_streak == 0:
            return "No Data"
        elif win_streak >= 1 and loss_streak == 0:
            return "🏆" * win_streak
        else:
            return "❌" * loss_streak

    def get_league_game_duration(self, game_duration):
        """
        Calculates the game duration
        """
        timings = util.hours_minutes_seconds(game_duration)

        if timings["hours"] == 0:
            return "{:02d}m:{:02d}s".format(timings["minutes"], timings["seconds"])

        return "{:02d}h:{:02d}m:{:02d}s".format(
            timings["hours"], timings["minutes"], timings["seconds"]
        )

    def get_queue_type(self, queue_id):
        """
        Gets the queue type from the queue id.

        :param queue_id: The queue id (int)
        """
        for item in QUEUE_ID_CACHE:
            if item["queueId"] == queue_id:

                # If the game is a custom game, return the custom game name
                if item["description"] == None:
                    try:
                        return item["map"]
                    except KeyError:
                        return "unknown"

                # If the game is not a custom game, return the game name
                return item["description"].replace("games", "").strip()
