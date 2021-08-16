import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from datetime import datetime
from uuid import uuid4
import os

HOST = os.environ['ACCOUNT_HOST']
ACCOUNT_KEY = os.environ['ACCOUNT_KEY']
DATABASE_ID = os.environ['COSMOS_DATABASE']
CONTAINER_ID = os.environ["COSMOS_CONTAINER"]


def create_items(container, data=None):
    """
    Creates an item in Azure Cosmos DB
    Where 'data' is a dict containing the data you wish to store 
    """
    iso_timestamp = datetime.now().replace(microsecond=0).isoformat()

    body = {
        "id": str(uuid4()),
        "created_at": iso_timestamp,
        "updated_at": iso_timestamp,
        "data": data
    }

    container.create_item(body=body)


def read_item(container, item_id, partition_key=None):

    if partition_key:
        response = container.read_item(item=item_id, partition_key=partition_key)
        print("Partition Key: {0}".format(response.get("partitionKey")))
    else:
        response = container.read_item(item=item_id)
        print("Item read by Id {0}".format(item_id))

    return response

def read_items(container):
    print("\nReading all items in a container\n")

    # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
    #       Important to handle throttles whenever you are doing operations such as this that might
    #       result in a 429 (throttled request)
    item_list = list(container.read_all_items(max_item_count=10))

    print("Found {0} items".format(item_list.__len__()))

    for doc in item_list:
        print("Item Id: {0}".format(doc.get("id")))


def query_items(container, partition_key):
    print("\nQuerying for an  Item by Partition Key\n")

    # Including the partition key value of account_number in the WHERE filter results in a more efficient query
    items = list(
        container.query_items(
            query=f"SELECT * FROM r WHERE r.partitionKey=@{partition_key}",
            parameters=[{"name": f"@{partition_key}", "value": partition_key}]
        )
    )

    print("Item queried by Partition Key {0}".format(items[0].get("id")))


def replace_item(container, doc_id, account_number):
    print("\nReplace an Item\n")

    read_item = container.read_item(item=doc_id, partition_key=account_number)
    read_item["subtotal"] = read_item["subtotal"] + 1
    response = container.replace_item(item=read_item, body=read_item)

    print(
        "Replaced Item's Id is {0}, new subtotal={1}".format(
            response["id"], response["subtotal"]
        )
    )


def upsert_item(container, doc_id, account_number):
    print("\nUpserting an item\n")

    read_item = container.read_item(item=doc_id, partition_key=account_number)
    read_item["subtotal"] = read_item["subtotal"] + 1
    response = container.upsert_item(body=read_item)

    print(
        "Upserted Item's Id is {0}, new subtotal={1}".format(
            response["id"], response["subtotal"]
        )
    )


def delete_item(container, doc_id, account_number):
    print("\nDeleting Item by Id\n")

    response = container.delete_item(item=doc_id, partition_key=account_number)

    print("Deleted item's Id is {0}".format(doc_id))


def run_sample():
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
        
        create_items(container, data=data)
        # read_item(container, 'SalesOrder1', 'Account1')
        read_items(container)
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
