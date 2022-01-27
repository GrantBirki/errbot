# Persistence

> This is a more advanced topic. This article will not fully show you how to setup persistence but rather plant some seeds for how you can do it on your own 🌱 (and hopefully help you get there)

The very nature of containers is ephemeral and persistence is always a valid question when it comes to containers.

For this project I chose to lean pretty hard into AWS DynamoDB to save small bits of state where needed.

The bot itself is fairly stateless and all its configuration is baked in via environement variables. However, certain bot commands have statistics tied into them, they can remember things, and have leader boards. In order to retain this data, nosql records are stored in various DynamoDB tables.

## Walkthrough

This section will walk through an example of a bot commad that has persistence and I will do the best I can to explain how this is stored in DynamoDB:

> Note: This examples uses a "top down approach". You will first "see" a chat command being run and then run through all the pieces it interacts with and you will end with the initial table creation via Terraform

1. A user invokes the `.remember` command to remember something simple:

   ```text
   .remember meeting is tomorrow
   ```

   > This will write a record to DynamoDB with `meeting` as the key and `tomorrow` as the value

1. Here is an example of some code that could write these values to DynamoDB:

    ```python
    from lib.database.dynamo_tables import RememberTable
    dynamo = Dynamo()
    dynamo.write(
        RememberTable(
            discord_server_id=guild_id,
            rem_key=result["key"],
            rem_value=result["value"],
        )
    )
    ```

1. Check out the `src/errbot/plugins/database/dynamo_tables.py` file to see where the structure for tables can be defined
1. Check out the `src/errbot/plugins/database/dynamo.py` file to see where I implemented a helper class for interacting with DynamoDB (as used above in the snippet)
1. Check out the `terraform/aws/dynamoDB_tables.tf` file to see how DynamoDB tables are created in AWS via Terraform

## Testing Persistence Locally

The `docker-compose.yml` files comes with a side car container running `localstack` which is a growing project that does a good job at "mocking" many core AWS services. One of these services is DynamoDB and works quite well for testing locally.

When you run `make run` it automatically launches a `localstack` container with DynamoDB enabled. When the `localstack` container starts up, it will run the `script\localstack\localstack-startup` script which will pre-populate many DynamoDB tables for local testing. This is rather helpful because you can test out your persistence features locally to determine if it is worth the effort to setup something like AWS DynamoDB to hold state records for your bot.

> Note: By using the `localstack` side car container, you will be able to test out chat commands that need persistence like `.remember`, `.play stats`, etc. Whoot!

## Summary

The main take-aways from this section is that this bot comes with some built in commands that have a level of persistence to them. If you want these command to function properly or if you want to develop your own commands in the future that are stateful, you will need to enable a form of persistence for your bot.

I have shown you one method of doing so with AWS DynamoDB but there are many more options so chose what works best for you 😃
