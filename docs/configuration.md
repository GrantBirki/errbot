# Configuration

Now that your bot is all setup, you may notice some plugins fail to load in the logs. This is likely due to the fact that some plugins included in this base project require API keys to work correctly. If you don't intend on using these plugins that need APIs, you don't want to deal with making the keys, or you just hate the plugin, you can disable or delete the plugin entirely. This guide will assume you actually want them and show you how to configure them (or your own) correctly.

## The mighty .env files

All configuration to the bot is done through environment variables. This is done to make local dev easily mirror production and be configured in the same way.

There are two kinds of variables:

- Sensitive environment variables
- Everything else

These variables are split out into their own respective `.env` files

- `config.env` - Environment variables related to the overall configuration of the bot. This file can and **should** be committed
- `creds.env` - Sensitive environement variables containing secrets, API keys, tokens, etc. This file **should absolutely not** be committed ever

## What's next?

Continue on to the [development](development.md) section to learn more about how to build your bot, add new commands, and more!