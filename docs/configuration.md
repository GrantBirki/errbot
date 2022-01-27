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

You may have noticed some plugins fail to load in the logs when you started your bot after the setup step. This is likely due to the fact that some plugins included in this base project require API keys to work correctly. If you don't intend on using these plugins that need APIs, you don't want to deal with making the keys, or you just hate the plugin, you can disable or delete the plugin entirely. An example of a plugin that will fail to load is the `src/errbot/plugins/league` plugin. This plugin attempts to create a RIOT API client on boot and will fail if the token is missing. The good news is that if one plugin fails, all the rest will proceed. That one plugin that failed will just not be usable until the error is resolved. In the case of the `.league` command, all you need to do is A) generate an API token for the RIOT API or B) delete the `league/` directory from the `plugins/` folder.

Other tokens such as `SPOTIFY_*` actually have handling built in that will just not use their feature if the tokens are not present.

## What's next?

Continue on to the [development](development.md) section to learn more about how to build your bot, add new commands, and more!
