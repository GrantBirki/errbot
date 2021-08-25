import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from lib.common.utilities import Util
from uuid import uuid4
import os

util = Util()

class Cosmos:

    def __init__(self, cosmos_container='discord'):
        self.container = self.init_container(
            os.environ['COSMOS_ACCOUNT_HOST'],
            os.environ['COSMOS_ACCOUNT_KEY'],
            os.environ['COSMOS_DATABASE'],
            cosmos_container
        )

    def init_container(self, host, account_key, database_id, container_id):
        client = cosmos_client.CosmosClient(
            host,
            {"masterKey": account_key},
            user_agent="CosmosDB",
            user_agent_overwrite=True,
        )

        db = client.get_database_client(database_id)
        container = db.get_container_client(container_id)

        return container

    def fmt_id(self, id):
        return id.replace("#", "-").replace("@", "_").strip()

    def create_items(self, data=None, id=None):
        """
        Creates an item in Azure Cosmos DB
        Where 'data' is a dict containing the data you wish to store 
        """
        try:
            iso_timestamp = util.iso_timestamp()

            if id is None:
                id = str(uuid4())
            else:
                id = self.fmt_id(id)

            try:
                data['discord_server_id']
            except KeyError:
                data['discord_server_id'] = 'unknown'

            body = {
                "id": id,
                "created_at": iso_timestamp,
                "updated_at": iso_timestamp,
                "data": data
            }

            self.container.create_item(body=body)
            return True
        except exceptions.CosmosResourceExistsError:
            return False


    def read_item(self, id, partition_key=None):
        """
        Reads an item from the Azure Cosmos DB
        :param: id - The "id" of the record to fetch (required)
        :param: partition_key - The "partition_key" of the record to fetch

        Note: in most cases, the partition_key is the Discord server guild id
        """
        try:
            id = self.fmt_id(id)

            if partition_key:
                response = self.container.read_item(item=id, partition_key=partition_key)
            else:
                response = self.container.read_item(item=id, partition_key='unknown')

            return response
        except exceptions.CosmosResourceNotFoundError:
            return False

    def read_items(self, max_item_count=100):
        """
        Reads all items from an Azure Cosmos database container
        :return: item_list - List of all Azure cosmos DB items
        """
        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        item_list = list(self.container.read_all_items(max_item_count=max_item_count))
        return item_list

        # print("Found {0} items".format(item_list.__len__()))

        # for doc in item_list:
        #     print("Item Id: {0}".format(doc.get("id")))


    def query_items(self, container, partition_key):
        # TODO test this magic
        # Including the partition key value of account_number in the WHERE filter results in a more efficient query
        items = list(
            container.query_items(
                query=f"SELECT * FROM r WHERE r.partitionKey=@{partition_key}",
                parameters=[{"name": f"@{partition_key}", "value": partition_key}]
            )
        )

        print("Item queried by Partition Key {0}".format(items[0].get("id")))


    def replace_item(self, id, data=None, partition_key=None):
        """
        Replace a record in the Azure Cosmos database container
        :param: id - The "id" of the record to fetch (required)
        :param: data - The data body of the record with new key:value pairs to update
        :param: partition_key - The "partition_key" of the record to fetch

        Note: in most cases, the partition_key is the Discord server guild id 
        """
        #TODO determine if this is truly a replace - ie: read and write
        try:
            id = self.fmt_id(id)

            if partition_key:
                response = self.container.read_item(item=id, partition_key=partition_key)
            else:
                response = self.container.read_item(item=id, partition_key='unknown')

            # Update values in place
            response['updated_at'] = util.iso_timestamp()
            response['data'] = data #TODO only changed key:values

            # Set the new values
            response = self.container.replace_item(item=response, body=response)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    def update_item(self, id, data=None, partition_key=None):
        """
        Updates an item from the Azure Cosmos DB
        :param: id - The "id" of the record to fetch (required)
        :param: data - The data body of the record with new key:value pairs to update
        :param: partition_key - The "partition_key" of the record to fetch

        Note: in most cases, the partition_key is the Discord server guild id
        """
        try:
            id = self.fmt_id(id)

            # Read the current record
            if partition_key:
                response = self.container.read_item(item=id, partition_key=partition_key)
            else:
                response = self.container.read_item(item=id, partition_key='unknown')

            # Update the record "updated_at" value to now
            response["updated_at"] = util.iso_timestamp()

            # Update the record "data" with our new data
            for i in data:
                response['data'][i] = data[i]

            # Write the record
            response = self.container.upsert_item(body=response)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False

    def delete_item(self, id, partition_key=None):
        try:
            id = self.fmt_id(id)

            if partition_key:
                self.container.read_item(item=id, partition_key=partition_key)
            else:
                self.container.read_item(item=id, partition_key='unknown')

            self.container.delete_item(item=id, partition_key=partition_key)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
