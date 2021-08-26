import os
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute
)

class LeagueTable(Model):

    class Meta:
        table_name = 'league'
        region = 'us-west-2'
        aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
  
    discord_server_id = UnicodeAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    summoner_name = UnicodeAttribute()
    last_updated = UnicodeAttribute()
    last_match_sha256 = UnicodeAttribute(default_for_new=None, null=True)
    bot_can_at_me = UnicodeAttribute(default_for_new='True')
