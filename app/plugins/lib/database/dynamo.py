import os
from lib.common.utilities import Util
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute
)

util = Util()

class LeagueTable(Model):

    class Meta:
        table_name = 'league'
        region = 'us-west-2'
        aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
  
    discord_server_id = UnicodeAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    summoner_name = UnicodeAttribute()
    created_at = UnicodeAttribute(default_for_new=util.iso_timestamp())
    updated_at = UnicodeAttribute()
    last_match_sha256 = UnicodeAttribute(default_for_new=None, null=True)
    bot_can_at_me = UnicodeAttribute(default_for_new='True')

class Dynamo():
    def write(self, object):
        """
        Write a new (and replace) a database record
        """
        try:
            setattr(object, 'updated_at', util.iso_timestamp())
            object.save()
            return True
        except:
            return False

    def update(self, object, records):
        """
        Input an existing database upject and update it in place

        Example [records]:
        [SomeTable.hello_world.set("i am a message")]
        """
        try:
            object.update(
                actions = records 
            )
            return True
        except:
            return False

    def get(self, object, partition_key, sort_key):
        """
        Get an existing database object
        Note: Useful for passing this object into the update method
        """
        try:
            result = object.get(partition_key, sort_key)
            return result
        except:
            return False

    def delete(self, object):
        """
        Deletes a database object

        Note: You need to run a get() and pass the object in to use this method
        """
        try:
            object.delete()
            return True
        except:
            return False