import os
from lib.common.utilities import Util
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    UnicodeSetAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.exceptions import DoesNotExist

import boto3

session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-west-2",
)

dynamo = session.resource("dynamodb")

util = Util()


class LeagueTable(Model):
    class Meta:
        table_name = "league"
        region = "us-west-2"
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    discord_server_id = NumberAttribute(hash_key=True)
    discord_handle = UnicodeAttribute(range_key=True)
    summoner_name = UnicodeAttribute()
    account_id = UnicodeAttribute()
    created_at = UnicodeAttribute()
    updated_at = UnicodeAttribute()
    last_match_sha256 = UnicodeAttribute(default_for_new=None, null=True)
    bot_can_at_me = UnicodeAttribute(default_for_new="True")
    win_streak = NumberAttribute(default_for_new=0)
    loss_streak = NumberAttribute(default_for_new=0)


class Dynamo:
    def write(self, object):
        """
        Write a new (and replace) a database record
        """
        try:
            iso_timestamp = util.iso_timestamp()
            setattr(object, "created_at", iso_timestamp)
            setattr(object, "updated_at", iso_timestamp)
            object.save()
            return True
        except:
            return False

    def update(self, table: object, record: object, records_to_update: list):
        """
        Input an existing database upject and update it in place

        Example [records_to_update]:
        [SomeTable.hello_world.set("i am a message")]
        """
        try:

            # Update the timestamp

            records_to_update.append(table.updated_at.set(util.iso_timestamp()))

            record.update(actions=records_to_update)
            return True
        except DoesNotExist:
            return None
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
        except DoesNotExist:
            return None
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

    def scan(self, table_name, **kwargs):
        """
        A scan means to get ALL records in a table

        NOTE: Anytime you are filtering by a specific equivalency attribute such as id, name
        or date equal to ... etc., you should consider using a query not scan

        kwargs are any parameters you want to pass to the scan operation
        """
        try:
            dbTable = dynamo.Table(table_name)
            response = dbTable.scan(**kwargs)
            if kwargs.get("Select") == "COUNT":
                return response.get("Count")
            data = response.get("Items")
            while "LastEvaluatedKey" in response:
                response = kwargs.get("table").scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"], **kwargs
                )
                data.extend(response["Items"])
            return data
        except:
            False
