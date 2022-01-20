# Setup

This guide will walk you through setting up errbot for local development 🔨

## Project Components

**Key concepts**:

There are three main components to errbot:

- The **chatbot** itself - This is `errbot`, the python app running in a docker container which processes requests - `src/errbot/`
- The **chat-service** - This is what you are _connecting_ your chatbot to. This could be Discord, Slack, etc.. I will be using Discord for this guide but Slack is also tested and works fine.
- The **database** - This could be literally anything to store state since the nature of containers is ephimeral. For this project I have chosen AWS DynamoDB for state storage. When testing locally I use [LocalStack](https://github.com/localstack/localstack) to mock AWS DynamoDB.

## Prerequisites

If you got all the items below downloaded and are familiar with setting up a bot account for your chat service (Slack, Discord, etc), you can skip right to the usage section.

- [Docker](https://www.docker.com/)
- [Docker-compose](https://docs.docker.com/compose/)
- [Make](https://www.gnu.org/software/make/)
- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) if you are using Windows

Depending on which "backend" or "chat-service" you plan on using, you will need an authentication token to start your bot.

- [Slack](https://my.slack.com/services/new/bot) - Extra errbot [documentation](https://errbot.readthedocs.io/en/latest/user_guide/configuration/slack.html?highlight=slack)
- [Discord](https://discord.com/developers/docs/intro) - Extra errbot [documentation](https://github.com/gbin/err-backend-discord)

Lastly, you will need to be familiar with how to add your bot to your chat service.

Adding your bot to a chat service examples:

### Slack

In the case of Slack, this can be done by mentioning your bot in any channel and you will be prompted to invite the bot right there.

> Note, this particular repo leans towards Discord for most things. However, as of this writing, all features of this bot work in Slack as well with the exception of having the bot join a voice channel as that is not a feature of Slack.. yet

### Discord

> This bot has already been provisioned to Discord. It is included as a reference should the bot ever need to be rebuilt

With Discord, things are a little different. You will need to first enable `SERVER MEMBERS INTENT` for your bot application. After that, you need to go into the Oauth2 page for your bot and select the `bot` scope. This will expand more options. You may go as crazy or as restrictive as you want with the chat permissions. That part is totally up to you.

Once your permissiosn are scoped out, you will need to copy the oauth2 link that is generated.

It could look something like this: `https://discord.com/api/oauth2/authorize?client_id=<number>&permissions=<number>&scope=bot`

> Note: You can find an example invite link farther below

Enter that link into your web browser and it should give you a list of servers to invite your bot to. Add it to your favorite server!

To setup your bot, you will need to modify your `config.env` file. To make things easier, there is a `config.example.env` file in the root of this repo.

1. Rename `config.example.env` to `config.env` *required
1. Set `BACKEND=<backend>` *required
1. Set `CHAT_SERVICE_TOKEN='<token>'` *required
1. Change `BOT_PREFIX='!'` if you want *optional

---

## Usage - Locally

**Important**: Make sure you followed the setup instructions above first

For plugin testing and running the bot locally, you may run the following command to launch a local instance of your bot and interact with it over the command line:

```console
$ make local
[#] Starting local bot test environment
[#] Killing old docker processes
docker-compose rm -fs
Stopping chatbot ... done
Going to remove chatbot
Removing chatbot ... done
[#] Building docker containers
docker-compose build
Building chatbot
[+] Building 1.3s (22/22) FINISHED
...
..
.
[#] TEST Container is now running!
[#] Interact with me over the CLI prompt below
...
..
.
[@local_admin ➡ @errbot] >>>
```

**Note**: You may notice some errors in your output. This is expected if you do not have all the proper credentials setup in your `creds.env` file. For example, if you have an API token that is needed for a plugin, and that token is not present in the environment, that plugin will fail to load. All others should load fine and you can test normally.

> Read more about the errbot local dev environment [here](https://errbot.readthedocs.io/en/latest/user_guide/plugin_development/development_environment.html#local-test-mode)

### Windows Tips for Local Usage

If for some reason you are using Windows and not WSL, you can build a local image using the following commands:

```console
$ docker-compose build
$ docker run -it --rm --env-file config.env --env-file creds.env -e LOCAL_TESTING=True errbot_chatbot:latest
```

This will result in a CLI prompt to `errbot` locally so you can test. Simply press `CTRL+C` to exit when you are done

## Usage - Connected to a Chat Service

Completed the simple setup locally? Awesome! Let's start the bot connected to a live chat service:

> Note: `make run` will start the bot and attach it to Discord (or another chat service) for usage. If you are looking to start a local instance of the bot, see the `Usage - Locally` section earlier in this guide

```console
$ make run
[#] Killing old docker processes
docker-compose rm -fs
No stopped containers
[#] Building docker containers
docker-compose up --build -d
Building chatbot
[+] Building 1.3s (23/23) FINISHED
Creating chatbot ... done
[#] Container is now running!
```

> Note: for security reasons the `creds.env` file is not committed to this repo and NEVER should be.

If you followed the steps above and everything succeeded, you should get a DM from the bot stating that it is "Now Online". You should note that you will only get this message if `BOT_ADMINS='@username'` is set to your username in the `config.env` file.

> Note x2: Running `make run` will start the `errbot-dev` bot and can be invoked with `!` rather than the usual `.`

---

## What's next?

Continue on to the [development](development.md) section to learn more about how to build your bot, add new commands, and more!
