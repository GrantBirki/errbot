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

**config.env**:

|   ENV VAR   |  Value  |  Required / Optional         |  Description     |
|    :----:   |     :----:    |   :----:      |        :----:       |
| `BACKEND` | Discord / Slack / etc | Required | Set the desired chat backend for the bot |
| `BOT_PREFIX` | Any alpha-numeric character | Required | Set the character prefix used to invoke the bot (`.` is suggested) |
| `BOT_HOME_CHANNEL` | Any string related to a text channel name | Optional | Set a home channel for the bot as a default. Example, posting messages to a channel on a schedule like weather updates |
| `IMAGE_TAG` | String | Optional | An image tag / version number to use to identify the version of the bot that is running |
| `BOT_ADMINS` | String (ex: `Username#0001`) | Optional | The username in the chat-service provided format. Examples: `Username#0001` for Discord and `@user.name` for Slack |
| `BOT_EXTRA_BACKEND_DIR` | `/app/backend/err-backend-discord` | Depends | This variable is optional if you are not using a backend that requires it. If you are using a backend like Discord, then this is required |
| `BOT_STATUS_MESSAGE` | String | Optional | Certain chat services like Discord allow you to have a status message next to your bot's name. This variable allows you to provide that |
| `DISABLE_LEAGUE_CRON` | `True` | Optional | A variable used to disable or enable the "cron" like functionality for the `.league` plugin which posts match results at a set interval (like a cron job) |
| `DOCS_URL` | String | Optional | A link that will be provided to users when the `.docs` command is invoked |
| `LOCALSTACK` | `http://localstack:4566` | Required (locally) | If you are using LocalStack (you are by default) then this variable provides the URL to the localstack endpoint when testing locally with docker-compose |
| `SENTRY_DISABLED` | `True` | Optional | An optional variable that can be provided to manually disable the Sentry.io extension |

**creds.env**:

|   ENV VAR   |  Value  |  Required / Optional         |  Description     |
|    :----:   |     :----:    |   :----:      |        :----:       |
| `CHAT_SERVICE_TOKEN` | String | Required | The token used to authenticate to your desired chat service |
| `AWS_ACCESS_KEY_ID` | String | Optional | If you are using AWS DynamoDB for persistence, then you can provide this for authentication |
| `AWS_SECRET_ACCESS_KEY` | String | Optional | If you are using AWS DynamoDB for persistence, then you can provide this for authentication |
| `RIOT_TOKEN` | String | Optional | Add your RIOT API token to enable the `.league` chat commands and features |
| `SPOTIFY_CLIENT_ID` | String | Optional | Add your Spotify API credentials to enable Spotify song detail lookups and URLs for the `.play` command |
| `SPOTIFY_CLIENT_SECRET` | String | Optional | Add your Spotify API credentials to enable Spotify song detail lookups and URLs for the `.play` command |
| `SENTRY` | Sentry DSN in the following format: `https://<id>@<id>.ingest.sentry.io/<id>` | Optional | Add your Sentry.io DSN in the URL format to enable logging exceptions to Sentry.io |

**Table Key Details:**

- `ENV VAR` - The variable name to be provided
- `Value` - An example of the value(s) that can be provided
- `Required / Optional` - Whether or not the variable is required or optional
- `Description` - A description of what the variable is used for

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
