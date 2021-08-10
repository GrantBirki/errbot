from errbot import BotPlugin, botcmd, arg_botcmd
from riotwatcher import LolWatcher, ApiError

LOL_WATCHER = LolWatcher('api-key-here')
REGION = 'na1'

class League(BotPlugin):
    """League plugin for Errbot"""

    @arg_botcmd('summoner_name', type=str)
    def last_match(self, msg, summoner_name=None):
        """Get the last match for a user (LoL)"""

        player_game_stats = self.get_last_match_data(summoner_name)
        message = self.message(player_game_stats)

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
