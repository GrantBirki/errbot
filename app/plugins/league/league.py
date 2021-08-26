import json
import os
import random
import traceback

import requests
from errbot import BotPlugin, arg_botcmd, botcmd
from lib.chat.discord import Discord
from lib.common.utilities import Util
from lib.database.dynamo import Dynamo, LeagueTable
from riotwatcher import ApiError, LolWatcher

LOL_WATCHER = LolWatcher(os.environ['RIOT_TOKEN'])
REGION = os.environ['RIOT_REGION']
discord = Discord()
util = Util()
dynamo = Dynamo()

with open('plugins/league/responses.json', 'r') as raw:
    RESPONSES = json.loads(raw.read())

LEAGUE_VERSION = json.loads(requests.get('https://ddragon.leagueoflegends.com/realms/na.json').text)['n']['champion']
CHAMPION_DATA = json.loads(requests.get(f'https://ddragon.leagueoflegends.com/cdn/{LEAGUE_VERSION}/data/en_US/champion.json').text)['data']
LEAGUE_CHANNEL = "#league"

class League(BotPlugin):
    """League plugin for Errbot"""

    def last_match_cron(self):
        """
        Last match function on a schedule! Posts league stats
        """
        db_items = dynamo.scan('league')
        for item in db_items:
            try:
                # Gets the last match data
                last_match_data = self.get_last_match_data(item['summoner_name'])
                if not last_match_data:
                    # summoner_name was not found so we skip it
                    continue
                # Calcutes a unique hash of the match
                current_match_sha256 = util.sha256(json.dumps(last_match_data))
                # Checks if the last match data is already in the database
                if item.get('last_match_sha256', None) == current_match_sha256:
                    continue

                # Get the Discord Server guild_id
                guild_id = discord.fmt_guild_id(item['discord_server_id'])

                # Updates the match sha so results for a match are never posted twice
                get_result = dynamo.get(LeagueTable, guild_id, item['discord_handle'])
                update_result = dynamo.update(
                    table = LeagueTable,
                    record = get_result,
                    records_to_update = [
                        LeagueTable.last_match_sha256.set(current_match_sha256)
                    ]
                )

                if get_result:
                    # Sends a message to the user's discord channel which they registered with
                    self.send(
                        self.build_identifier(f'{LEAGUE_CHANNEL}@{guild_id}'),
                        self.league_message(item['summoner_name'], last_match_data)
                    )
                else:
                    self.send(
                        self.build_identifier(f'{LEAGUE_CHANNEL}@{guild_id}'),
                        f"❌ Something went wrong posting a league game for `{item['summoner_name']}`"
                    )
            except:
                self.warn_admins(traceback.format_exc())
                continue

    def activate(self):
        """
        Runs the last_match_cron() function every 30 seconds
        """
        super().activate()
        self.start_poller(30, self.last_match_cron)

    @arg_botcmd('summoner_name', type=str)
    def add_me_to_league_watcher(self, msg, summoner_name=None):
        """
        Adds a summoner to the league watcher
        
        Usage: .add me to league watcher <summoner_name>
        Example: .add me to league watcher birki
        """

        discord_handle = discord.handle(msg)
        guild_id, guild_msg = discord.guild_id(msg)

        if not guild_id:
            return guild_msg

        get_result = dynamo.get(LeagueTable, guild_id, discord_handle)
        if get_result:
            return f"ℹ️ {discord.mention_user(msg)} already has an entry in the league watcher!"
        elif get_result is False:
            return f"❌ Failed to check the league watcher for {discord.mention_user(msg)}"

        # Runs a quick check against the Riot API to see if the summoner_name entered is valid
        if not self.get_summoner_account_id(summoner_name):
            return f"❌ Summoner `{summoner_name}` not found in the Riot API! Check your spelling and try again.."

        write_result = dynamo.write(
            LeagueTable(
                discord_server_id=guild_id,
                discord_handle=discord_handle,
                summoner_name=summoner_name
            )
        )

        if write_result:
            return f"✅ Added {discord.mention_user(msg)} to the league watcher!"
        else:
            return f"❌ Failed to add {discord.mention_user(msg)} to the league watcher!"

    @arg_botcmd('--summoner_name', dest='summoner_name', type=str, admin_only=True)
    @arg_botcmd('--discord_handle', dest='discord_handle', type=str, admin_only=True)
    @arg_botcmd('--guild', dest='guild', type=int, admin_only=True)
    def add_to_league_watcher(self, msg, summoner_name=None, discord_handle=None, guild=None):
        """
        Adds a summoner to the league watcher - Admin command
        Run from the channel you wish to use the league watcher in
        
        Usage: .add to league watcher <summoner_name> <discord_handle>
        Example: .add to league watcher --summoner_name birki --discord_handle birki#0001
        """
        guild_id = int(guild)

        get_result = dynamo.get(LeagueTable, guild_id, discord_handle)
        if get_result:
            return f"ℹ️ {discord.mention_user(msg)} already has an entry in the league watcher!"
        elif get_result is False:
            return f"❌ Failed to check the league watcher for {discord.mention_user(msg)}"
        
        # Runs a quick check against the Riot API to see if the summoner_name entered is valid
        if not self.get_summoner_account_id(summoner_name):
            return f"❌ Summoner `{summoner_name}` not found in the Riot API! Check your spelling and try again.."

        write_result = dynamo.write(
            LeagueTable(
                discord_server_id=guild_id,
                discord_handle=discord_handle,
                summoner_name=summoner_name
            )
        )

        if write_result:
            return f"✅ Added {discord.mention_user(msg)} to the league watcher!"
        else:
            return f"❌ Faile to add {discord.mention_user(msg)} to the league watcher!"

    @botcmd
    def remove_me_from_league_watcher(self, msg, args):
        """
        Removes a summoner from the league watcher

        Usage: .remove me from league watcher
        """

        discord_handle = discord.handle(msg)
        guild_id, guild_msg = discord.guild_id(msg)

        if not guild_id:
            return guild_msg

        get_result = dynamo.get(LeagueTable, guild_id, discord_handle)
        if get_result is None:
            return f"ℹ️ {discord.mention_user(msg)} is not in the league watcher!"

        result = dynamo.delete(get_result)

        if result:
            return f"✅ Removed {discord.mention_user(msg)} from the league watcher!"
        else:
            return f"❌ Faile to remove {discord.mention_user(msg)} to the league watcher!"

    @botcmd
    def view_my_league_watcher_data(self, msg, args):
        """
        Views your data for the League Watcher
        
        This is mostly for debugging
        """
        discord_handle = discord.handle(msg)
        guild_id, guild_msg = discord.guild_id(msg)

        if not guild_id:
            return guild_msg

        response = dynamo.get(LeagueTable, guild_id, discord_handle)

        if response:

            if not response.last_match_sha256:
                last_match_sha256 = 'Waiting for auto update...'

            message = f"**League Watcher Data**:\n"
            message += f"• Discord Handle: `{response.discord_handle}`\n"
            message += f"• Summoner Name: `{response.summoner_name}`\n"
            message += f"• Last Match SHA: `{last_match_sha256}`\n"
            message += f"• Can I fucking @you?: `{response.bot_can_at_me}`\n"
            message += f"• Last Updated: `{response.updated_at}`"

            return message
        else:
            message = f"ℹ️ {discord.mention_user(msg)} is not in the league watcher for this Discord server!\n"
            message += "Use `.add me to league watcher <summoner_name>` to add yourself"
            return message

    @arg_botcmd('summoner_name', type=str)
    def last_match_for(self, msg, summoner_name=None):
        """Get the last match for a user (LoL)"""

        if type(summoner_name) is str:
            summoner_list = summoner_name.split(',')

        return self.last_match_main(summoner_list)

    def last_match_main(self, summoner_list):

        messages = []
        for summoner in summoner_list:
            last_match_data = self.get_last_match_data(summoner)
            if not last_match_data:
                messages.append(f"ℹ️ A {summoner} with that ridiculous name was not found!")
            else:
                messages.append(self.league_message(summoner, last_match_data))

        message = '\n\n'.join(messages)

        return message

    def get_summoner_account_id(self, summoner_name):
            try:
                summoner = LOL_WATCHER.summoner.by_name(REGION, summoner_name)
                return summoner['accountId']
            except ApiError as err:
                if err.response.status_code == 404:
                    return None
                else:
                    raise
    
    def get_summoner_match_list(self, summoner_account_id):
        return LOL_WATCHER.match.matchlist_by_account(REGION, summoner_account_id)

    def get_match_data(self, match_id):
        return LOL_WATCHER.match.by_id(REGION, match_id)

    def get_last_match_data(self, summoner_name):
        
        account_id = self.get_summoner_account_id(summoner_name)
        if not account_id:
            return None
        match_list = self.get_summoner_match_list(account_id)

        last_match = match_list['matches'][0]
        match_details = self.get_match_data(last_match['gameId'])

        participant_identities = match_details['participantIdentities']
        participant_id = [p_id for p_id in participant_identities if p_id['player']['accountId'] == account_id][0]['participantId']

        return [player for player in match_details['participants'] if player['participantId'] == participant_id][0]

    def league_message(self, summoner, match_data):

        message = f'Last Match For: **{summoner}**\n'

        if match_data['stats']['win'] == True:
            message += '• Match Result: `win` 🏆\n'
        else:
            message += '• Match Result: `loss` ❌\n'

        message += f"• Lane: `{match_data['timeline']['lane'].lower()}`\n"
        message += f"• Champion: `{self.get_champion(match_data['championId'])}`\n"

        deaths = match_data['stats']['deaths']
        kills = match_data['stats']['kills']
        assists = match_data['stats']['assists']

        perf = self.performance(kills, deaths, assists)

        rand_response = random.randrange(0, len(RESPONSES[perf]))

        message += f'• KDA: `{kills}/{deaths}/{assists}`\n'
        message += f'• Performance Evaluation: `{perf}` {self.performance_emote(perf)}\n'
        message += f"> *{RESPONSES[perf][rand_response]}*"
        return message

    def performance(self, kills, deaths, assists):

        kda_calc = kills - deaths + assists / 2

        if kda_calc >= 8:
            return 'excellent'
        elif kda_calc >= 4 and kda_calc < 8:
            return 'good'
        elif kda_calc >= 0 and kda_calc < 4:
            return 'average'
        elif kda_calc <= 0 and kda_calc > -4:
            return 'poor'
        elif kda_calc <= -4:
            return 'terrible'

    def performance_emote(self, performance):

        if performance == 'excellent':
            return '🌟'
        elif performance == 'good':
            return '👍'
        elif performance == 'average':
            return '😐'
        elif performance == 'poor':
            return '👎'
        elif performance == 'terrible':
            return '💀'
    
    def get_champion(self, champion_id):
        for item in CHAMPION_DATA:
            if int(CHAMPION_DATA[item]['key']) == int(champion_id):
                return item.lower()
        return None
