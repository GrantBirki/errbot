import os

from pynamodb.attributes import (
    NumberAttribute,
    UnicodeAttribute,
    UnicodeSetAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.models import Model

LOCALSTACK = os.environ.get("LOCALSTACK", False)
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "no-aws")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "no-aws")
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")


class LeagueTable(Model):
    class Meta:
        table_name = "league"
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        if LOCALSTACK:
            host = LOCALSTACK

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
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        if LOCALSTACK:
            host = LOCALSTACK

    discord_server_id = NumberAttribute(hash_key=True)
    rem_key = UnicodeAttribute(range_key=True)
    rem_value = UnicodeAttribute()


class LoudTable(Model):
    class Meta:
        table_name = "loud"
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        if LOCALSTACK:
            host = LOCALSTACK

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    updated_at = UnicodeAttribute()


class PlayTable(Model):
    class Meta:
        table_name = "play"
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        if LOCALSTACK:
            host = LOCALSTACK

    discord_server_id = NumberAttribute(hash_key=True)
    stats = UnicodeAttribute()
    updated_at = UnicodeAttribute()


class TtsTable(Model):
    class Meta:
        table_name = "tts"
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        if LOCALSTACK:
            host = LOCALSTACK

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    updated_at = UnicodeAttribute()


class SparkleTable(Model):
    class Meta:
        table_name = "sparkle"
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        if LOCALSTACK:
            host = LOCALSTACK

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    total_sparkles = NumberAttribute()
    sparkle_reasons = UnicodeAttribute()
    updated_at = UnicodeAttribute()


class BotDataTable(Model):
    class Meta:
        table_name = "botdata"
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        if LOCALSTACK:
            host = LOCALSTACK

    bot = UnicodeAttribute(hash_key=True)
    command_usage_data = UnicodeAttribute()
    updated_at = UnicodeAttribute()
