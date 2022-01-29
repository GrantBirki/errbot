# Configuration

This section will walk you through configuring your bot to make it uniquely yours!

## The mighty .env files

All configuration to the bot is done through environment variables. This is done to make local dev easily mirror production and be configured in the same way.

There are two kinds of variables:

- Sensitive environment variables
- Everything else

These variables are split out into their own respective `.env` files

- `config.env` - Environment variables related to the overall configuration of the bot. This file can and **should** be committed
- `creds.env` - Sensitive environement variables containing secrets, API keys, tokens, etc. This file **should absolutely not** be committed ever

### config.env

This file has a lot of comments describing each option so I won't go into too many details here. In this file you can make general configuration changes to the bot to alter how it behaves. Below are a few examples:

- `BOT_PREFIX='!'` - This allows you to change the character that you invoke your bot with. For example, you could have it be `.` instead of a `!` (I like the `.`) -> `.uptime`
- `BOT_HOME_CHANNEL` - The "home channel" of the bot. Can be useful to have this set if you have a cron that posts messages at a certain time to a certain channel, like weather updates
- `BOT_ADMINS` - Set the "admin" users of the bot. Can be used in combination with the `@botcmd(admin_only=True)` decorator to prevent non-admins from using a certain command

### creds.env

⚠️ Once again do not ever commit this file to your version control system!

This file contains secrets and credentials that your bot needs to run. The only credential that is needed to run the bot is the `CHAT_SERVICE_TOKEN` which is what you use to connect to your desired chat service (Discord, Slack, etc). All the rest are optional! Examples below:

Required:

- `CHAT_SERVICE_TOKEN='<token>'` - The token to connect your bot to its chat service

Optional Examples:

- `AWS_ACCESS_KEY_ID='<token>'` & `AWS_SECRET_ACCESS_KEY='<token>'` - AWS tokens if you are using DynamoDB for state persistence
- `RIOT_TOKEN` - An API token from RIOT to enable the League of Legends gameplay watcher plugin
- `SPOTIFY_CLIENT_ID='<token>'` & `SPOTIFY_CLIENT_SECRET='<token>'` - Spotify tokens to enable extra Spotify lookups on songs played with the `.play` command
- `SENTRY='https://<id>@<id>.ingest.sentry.io/<id>'` - Sentry.io url endpoint for sending exception events for your bot (I love this personally)

> Check out the `creds.env.example` file to see more examples of this file's contents

**A note on optional credentials as seen above:**

A few of the tokens listed above are optional and enable extra features to the bot when provided as environment variables. You can see more information on these in the configuration table below.

## Configuration Table

Now that you have a general understanding about how environment variables are used to configure the bot, let's look at a table of the configuration options that are available:

**Key**:

- `ENV VAR` - The variable name to be provided
- `Value` - An example of the value(s) that can be provided
- `Required / Optional` - Whether or not the variable is required or optional
- `Description` - A description of what the variable is used for

|   ENV VAR   |  Value  |  Required / Optional         |  Description     |
|    :----:   |     :----:    |   :----:      |        :----:       |
| `BACKEND` | Discord / Slack / etc | Required | Set the desired chat backend for the bot |
| `BOT_PREFIX` | Any alpha-numeric character | Required | Set the character prefix used to invoke the bot (`.` is suggested) |
| `BOT_HOME_CHANNEL` | Any string related to a text channel name | Optional | Set a home channel for the bot as a default. Example, posting messages to a channel on a schedule like weather updates |
|TODO | TODO | TODO | TODO |

## What About Production?

> Related to this section is the [deployment](deployment.md) page

How do we get these environment variables into our container when deploying to production you ask? Well that really depends on how **you** are deploying your container to production. I will provide a few options below to give you some ideas:

For `config.env`:

- Apply your environment variables in your container definintion if you are using Kubernetes
- Bake your environment variables into your container when building the image (meh)
- Load the `config.env` file into the container or mount a volume with this file that the container has access to. Then read the file and populate the environment variables
- Store the variables in a remote config store and read them from there

For `creds.env`:

- Use k8s secrets for when deploying to Kubernetes -> `terraform/k8s/modules/containers/errbot/secret.yaml`
- Use Hashicorp Vault to inject secrets from `creds.env`
- Use an external service like AWS Secrets Manager and read from there

## What's next?

Continue on to the [development](development.md) section to learn more about how to build your bot, add new commands, and more!
