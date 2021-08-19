import os

from errbot import BotPlugin, arg_botcmd, botcmd
from lib.database.database import Database
from lib.discord.discord import Discord
from riotwatcher import ApiError, LolWatcher

LOL_WATCHER = LolWatcher(os.environ['RIOT_TOKEN'])
REGION = os.environ['RIOT_REGION']
db = Database()
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
        """Adds a summoner to the league watcher"""

        discord_handle = discord.handle(msg)

        result = db.create_items(
            id = discord_handle,
            data = {
                'discord_handle': discord_handle,
                'summoner_name': summoner_name,
                'discord_server_id': discord.guild_id(msg)
            }
        )

        if result:
            return f"Added @{discord_handle} to the league watcher!"
        else:
            return f"@{discord_handle} is already in the league watcher!"

    @botcmd
    def view_me(self, msg, args):
        """Views your data"""

        discord_handle = discord.handle(msg)
        response = db.read_item(discord_handle, partition_key=discord.guild_id(msg))

        if response:

            message = f"Discord Handle: {response['data']['discord_handle']}\n"
            message += f"Summoner Name: {response['data']['summoner_name']}\n"

            return message
        else:
            message = f"@{discord_handle} is not in the league watcher!\n"
            message += "Use `.add me to league watcher <summoner_name>` to add yourself"
            return message

    @arg_botcmd('summoner_name', type=str)
    def last_match(self, msg, summoner_name=None):
        """Get the last match for a user (LoL)"""

        if type(summoner_name) is str:
            summoner_list = summoner_name.split(',')

        return self.last_match_main(summoner_list)

    def last_match_main(self, summoner_list):

        messages = []
        for summoner in summoner_list:
            player_game_stats = self.get_last_match_data(summoner)
            messages.append(self.message(player_game_stats))

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

    def message(self, player_game_stats):

        if player_game_stats['win'] == True:
            message = 'You won the game'
        else:
            message = 'You lost the game'

        deaths = player_game_stats['deaths']
        kills = player_game_stats['kills']
        assists = player_game_stats['assists']

        if deaths > kills:
            message += ' and you fed your ass off!'

        message += f' | KDA: {kills}/{deaths}/{assists}'
        return message
