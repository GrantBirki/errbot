# Persistence

> This is a more advanced topic. This article will not fully show you how to setup persistence but rather plant some seeds for how you can do it on your own 🌱 (and hopefully help you get there)

The very nature of containers is ephemeral and persistence is always a valid question when it comes to containers.

For this project I chose to lean pretty hard into AWS DynamoDB to save small bits of state where needed.

The bot itself is fairly stateless and all its configuration is baked in via environement variables. However, certain bot commands have statistics tied into them, they can remember things, and have leader boards. In order to retain this data, nosql records are stored in various DynamoDB tables.

## Walkthrough

This section will walk through an example of a bot commad that has persistence and I will do the best I can to explain how this is stored in DynamoDB:

1. A user invokes the `.remember` command to remember something simple:

   ```text
   .remember meeting is tomorrow
   ```

   > This will write a record to DynamoDB with `meeting` as the key and `tomorrow` as the value

1. 