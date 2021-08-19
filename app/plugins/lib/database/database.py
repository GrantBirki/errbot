import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from datetime import datetime
from uuid import uuid4
import os

class Database:

    def __init__(self):
        self.container = self.init_container(
            os.environ['ACCOUNT_HOST'],
            os.environ['ACCOUNT_KEY'],
            os.environ['COSMOS_DATABASE'],
            os.environ["COSMOS_CONTAINER"]
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

    def create_items(self, data=None, id=None):
        """
        Creates an item in Azure Cosmos DB
        Where 'data' is a dict containing the data you wish to store 
        """
        try:
            iso_timestamp = datetime.now().replace(microsecond=0).isoformat()

            if id is None:
                id = str(uuid4())

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


    def read_item(self, item_id, partition_key=None):
        try:
            if partition_key:
                response = self.container.read_item(item=item_id, partition_key=partition_key)
            else:
                response = self.container.read_item(item=item_id, partition_key='unknown')

            return response
        except exceptions.CosmosResourceNotFoundError:
            return False

    def read_items(self):
        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        item_list = list(self.container.read_all_items(max_item_count=100))
        return item_list

        # print("Found {0} items".format(item_list.__len__()))

        # for doc in item_list:
        #     print("Item Id: {0}".format(doc.get("id")))


    def query_items(self, container, partition_key):
        print("\nQuerying for an  Item by Partition Key\n")

        # Including the partition key value of account_number in the WHERE filter results in a more efficient query
        items = list(
            container.query_items(
                query=f"SELECT * FROM r WHERE r.partitionKey=@{partition_key}",
                parameters=[{"name": f"@{partition_key}", "value": partition_key}]
            )
        )

        print("Item queried by Partition Key {0}".format(items[0].get("id")))


    def replace_item(self, container, doc_id, account_number):
        print("\nReplace an Item\n")

        read_item = container.read_item(item=doc_id, partition_key=account_number)
        read_item["subtotal"] = read_item["subtotal"] + 1
        response = container.replace_item(item=read_item, body=read_item)

        print(
            "Replaced Item's Id is {0}, new subtotal={1}".format(
                response["id"], response["subtotal"]
            )
        )


    def upsert_item(self, container, doc_id, account_number):
        print("\nUpserting an item\n")

        read_item = container.read_item(item=doc_id, partition_key=account_number)
        read_item["subtotal"] = read_item["subtotal"] + 1
        response = container.upsert_item(body=read_item)

        print(
            "Upserted Item's Id is {0}, new subtotal={1}".format(
                response["id"], response["subtotal"]
            )
        )


    def delete_item(self, container, doc_id, account_number):
        print("\nDeleting Item by Id\n")

        response = container.delete_item(item=doc_id, partition_key=account_number)

        print("Deleted item's Id is {0}".format(doc_id))


    def run_sample(self):
        client = cosmos_client.CosmosClient(
            HOST,
            {"masterKey": ACCOUNT_KEY},
            user_agent="CosmosDBPythonQuickstart",
            user_agent_overwrite=True,
        )
        try:

            db = client.get_database_client(DATABASE_ID)
            container = db.get_container_client(CONTAINER_ID)


            data = {
                "discord_server_id": 123456789,
                "discord_server_name": "Test Server",
                "discord_user_name": "Test User"
            }
            
            self.create_items(container, data=data)
            # read_item(container, 'SalesOrder1', 'Account1')
            self.read_items(container)
            # query_items(container, 'Account1')
            # replace_item(container, 'SalesOrder1', 'Account1')
            # upsert_item(container, 'SalesOrder1', 'Account1')
            # delete_item(container, 'SalesOrder1', 'Account1')

        except exceptions.CosmosHttpResponseError as e:
            print("\nrun_sample has caught an error. {0}".format(e.message))

        finally:
            print("\nrun_sample done")


if __name__ == "__main__":
    run_sample()
