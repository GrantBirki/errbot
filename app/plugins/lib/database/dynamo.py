import os
from lib.common.utilities import Util
from pynamodb.exceptions import DoesNotExist

import boto3

session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-west-2",
)

dynamo = session.resource("dynamodb")

util = Util()


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

    def update(self, table: object, record: object, fields_to_update: list):
        """
        Input an existing database upject and update it in place

        Example [records_to_update]:
        [SomeTable.hello_world.set("i am a message")]
        """
        try:

            # Update the timestamp

            fields_to_update.append(table.updated_at.set(util.iso_timestamp()))

            record.update(actions=fields_to_update)
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
