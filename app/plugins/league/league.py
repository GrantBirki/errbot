import os

from errbot import BotPlugin, arg_botcmd, botcmd
from lib.database.cosmos import Cosmos
from lib.chat.discord import Discord
from riotwatcher import ApiError, LolWatcher
import random
import json

LOL_WATCHER = LolWatcher(os.environ['RIOT_TOKEN'])
REGION = os.environ['RIOT_REGION']
cosmos = Cosmos(cosmos_container='league') # using the specific league container
discord = Discord()

class League(BotPlugin):
    """League plugin for Errbot"""

    # Temp disabled
    # def last_match_cron(self):
    #     summoner_list = os.environ['SUMMONER_LIST'].split(' ')
    #     return self.last_match_main(summoner_list)

    # def activate(self):
    #     super().activate()
    #     self.start_poller(500, self.last_match_cron)

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

        result = cosmos.create_items(
            id = discord_handle,
            data = {
                'discord_handle': discord_handle,
                'summoner_name': summoner_name,
                'discord_server_id': guild_id
            }
        )

        if result:
            return f"✅ Added {discord.mention_user(msg)} to the league watcher!"
        else:
            return f"ℹ️ {discord.mention_user(msg)} is already in the league watcher!"

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

        result = cosmos.delete_item(
            id = discord_handle,
            partition_key = guild_id
        )

        if result:
            return f"✅ Removed {discord.mention_user(msg)} from the league watcher!"
        else:
            return f"ℹ️ {discord.mention_user(msg)} is not in the league watcher!"

    @botcmd
    def view_league_watcher_data(self, msg, args):
        """Views your data for the League Watcher"""

        discord_handle = discord.handle(msg)
        guild_id, guild_msg = discord.guild_id(msg)

        if not guild_id:
            return guild_msg

        response = cosmos.read_item(discord_handle, partition_key=guild_id)

        if response:

            message = f"**League Watcher Data**:\n"
            message += f"• Discord Handle: `{response['data']['discord_handle']}`\n"
            message += f"• Summoner Name: `{response['data']['summoner_name']}`\n"

            return message
        else:
            message = f"ℹ️ {discord.mention_user(msg)} is not in the league watcher!\n"
            message += "Use `.add me to league watcher <summoner_name>` to add yourself"
            return message

    @arg_botcmd('summoner_name', type=str)
    def last_match(self, msg, summoner_name=None):
        """Get the last match for a user (LoL)"""

        if type(summoner_name) is str:
            summoner_list = summoner_name.split(',')

        return self.last_match_main(msg, summoner_list)

    def last_match_main(self, msg, summoner_list):

        messages = []
        for summoner in summoner_list:
            player_game_stats = self.get_last_match_data(summoner)
            messages.append(self.message(msg, player_game_stats))

        message = '\n'.join(messages)

        return message

    def get_summoner_account_id(self, summoner_name):
            summoner = LOL_WATCHER.summoner.by_name(REGION, summoner_name)
            return summoner['accountId']
    
    def get_summoner_match_list(self, summoner_account_id):
        return LOL_WATCHER.match.matchlist_by_account(REGION, summoner_account_id)

    def get_match_data(self, match_id):
        return LOL_WATCHER.match.by_id(REGION, match_id)

    def get_last_match_data(self, summoner_name):
        
        account_id = self.get_summoner_account_id(summoner_name)
        match_list = self.get_summoner_match_list(account_id)

        last_match = match_list['matches'][0]
        match_details = self.get_match_data(last_match['gameId'])

        participant_identities = match_details['participantIdentities']
        participant_id = [p_id for p_id in participant_identities if p_id['player']['accountId'] == account_id][0]['participantId']

        return [player for player in match_details['participants'] if player['participantId'] == participant_id][0]['stats']

    def message(self, msg, player_game_stats):

        message = f'{discord.mention_user(msg)} - '

        if player_game_stats['win'] == True:
            message += 'You **won** the game!\n'
        else:
            message += 'You **lost** the game!\n'

        deaths = player_game_stats['deaths']
        kills = player_game_stats['kills']
        assists = player_game_stats['assists']

        perf = self.performance(kills, deaths, assists)

        with open('responses.json', 'r') as raw:
            responses = json.loads(raw.read())

        rand_response = random.randrange(0, len(responses[perf]))

        message += f'Performance Evaluation: {responses[perf][rand_response]}\n'

        message += f'KDA: `{kills}/{deaths}/{assists}`'
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
