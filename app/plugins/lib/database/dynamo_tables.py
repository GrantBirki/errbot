import os

from pynamodb.attributes import (
    NumberAttribute,
    UnicodeAttribute,
    UnicodeSetAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.models import Model


class LeagueTable(Model):
    class Meta:
        table_name = "league"
        region = "us-west-2"
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    summoner_name = UnicodeAttribute()
    puuid = UnicodeAttribute()
    created_at = UnicodeAttribute()
    updated_at = UnicodeAttribute()
    last_match_sha256 = UnicodeAttribute(default_for_new=None, null=True)
    bot_can_at_me = UnicodeAttribute(default_for_new="True")
    win_streak = NumberAttribute(default_for_new=0)
    loss_streak = NumberAttribute(default_for_new=0)


class RememberTable(Model):
    class Meta:
        table_name = "remember"
        region = "us-west-2"
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    discord_server_id = NumberAttribute(hash_key=True)
    rem_key = UnicodeAttribute(range_key=True)
    rem_value = UnicodeAttribute()


class LoudTable(Model):
    class Meta:
        table_name = "loud"
        region = "us-west-2"
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    updated_at = UnicodeAttribute()


class PlayTable(Model):
    class Meta:
        table_name = "play"
        region = "us-west-2"
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    updated_at = UnicodeAttribute()

class TtsTable(Model):
    class Meta:
        table_name = "tts"
        region = "us-west-2"
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    updated_at = UnicodeAttribute()
