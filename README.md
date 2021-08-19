# errbot 🤖

[![deployment](https://github.com/GrantBirki/errbot/actions/workflows/deployment.yml/badge.svg?event=push)](https://github.com/GrantBirki/errbot/actions/workflows/deployment.yml) [![basic-checks](https://github.com/GrantBirki/errbot/actions/workflows/review.yml/badge.svg?event=push)](https://github.com/GrantBirki/errbot/actions/workflows/review.yml) [![tfsec](https://github.com/GrantBirki/errbot/actions/workflows/tfsec.yml/badge.svg?event=push)](https://github.com/GrantBirki/errbot/actions/workflows/tfsec.yml)

> Note: This repo is a fork of [errbot-launchpad](https://github.com/GrantBirki/errbot-launchpad)
> See the *fork notice* at the bottom of this readme

Quickly deploy a chatbot with Errbot, Dockerized! 🐳

## About 💡

This project uses [errbot](https://github.com/errbotio/errbot) and [Docker](https://www.docker.com/) to quickly launch your own chatbot in a container.

The goal of this project is to make it as easy as possible to launch a minimal, working chatbot.

## Quickstart ⭐

Want to get going quick? Run the following commands to bring up a CLI to interact with `errbot` locally:

1. `git clone git@github.com:GrantBirki/errbot-launchpad.git`
2. `cd errbot-launchpad`
3. `make local`

Didn't work quite right? See the setup section below..

---

## Setup 🛠️

### Prerequisites ✔️

If you got all the items below downloaded and are familiar with setting up a bot account for chat service, you can skip right to the setup section.

- [Docker](https://www.docker.com/)
- [Docker-compose](https://docs.docker.com/compose/)
- [Make](https://www.gnu.org/software/make/)
- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) if you are using Windows

Depending on which "backend" or "chat-service" you plan on using, you will need an authentication token to start your bot.

- [Slack](https://my.slack.com/services/new/bot) - Extra errbot [documentation](https://errbot.readthedocs.io/en/latest/user_guide/configuration/slack.html?highlight=slack)
- [Discord](https://discord.com/developers/docs/intro) - Extra errbot [documentation](https://github.com/gbin/err-backend-discord)

Lastly, you will need to be familiar with how to add your bot to your chat service.

Adding your bot to a chat service examples:

#### Slack

In the case of Slack, this can be done by mentioning your bot in any channel and you will be prompted to invite the bot right there.

#### Discord

With Discord, things are a little different. You will need to first enable `SERVER MEMBERS INTENT` for your bot application. After that, you need to go into the Oauth2 page for your bot and select the `bot` scope. This will expand more options. You may go as crazy or as restrictive as you want with the chat permissions. That part is totally up to you.

Once your permissiosn are scoped out, you will need to copy the oauth2 link that is generated.

It could look something like this: `https://discord.com/api/oauth2/authorize?client_id=<number>&permissions=<number>&scope=bot`

Enter that link into your web browser and it should give you a list of servers to invtire your bot to. Add it to your favorite server!

To setup your bot, you will need to modify your `config.env` file. To make things easier, there is a `config.example.env` file in the root of this repo.

1. Rename `config.example.env` to `config.env` *required
1. Set `BACKEND=<backend>` *required
1. Set `CHAT_SERVICE_TOKEN='<token>'` *required
1. Change `BOT_PREFIX='!'` if you want *optional

---

## Usage ⌨️

Completed the simple setup? Awesome! Let's start the bot:

```text
make run
```

Output:

```console
$ make run
[#] Killing old docker processes
docker-compose rm -fs
No stopped containers
[#] Building docker containers
docker-compose up --build -d
Building chatbot
[+] Building 1.3s (23/23) FINISHED
...
..
.
Creating chatbot ... done
[#] Container is now running!
```

If you followed the steps above and everything succeeded, you should get a DM from the bot stating that it is "Now Online". You should note that you will only get this message if `BOT_ADMINS='@username'` is set to your username in the `config.env` file.

### Testing and Building Locally 🧪

**Important**: Make sure you followed the setup instructions above first

For plugin testing, you may run the following command to launch a local instance of your bot and interact with it over the command line:

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

#### Windows Tips for Local Testing

If for some reason you are using Windows and not WSL like a pleb, you can build a local image using the following commands:

```console
docker-compose build
docker run -it --rm --env-file config.env --env-file creds.env -e LOCAL_TESTING=True errbot_chatbot:latest
```

This will result in a CLI prompt to `errbot` locally so you can test. Simply press `CTRL+C` to exit when you are done

### Making your own plugin / function 🔌

Check out the `plugins/example` folder. It really is that easy! Just copy a new folder, and add the files from the `example` plugin folder. Write your code, test, and deploy!

## Fork Notice 🍴

This repo is a fork of [errbot-launchpad](https://github.com/GrantBirki/errbot-launchpad) and should be treated as such.

If significant improvements are made in this repo they should be contributed back to the source. If cool features are added to the source, they may be merged into this project as well.

### Important Fork Commands

#### Setting up this repo

```bash
git remote add upstream git@github.com:GrantBirki/errbot-launchpad.git
```

> We have to do this to tell git where our upstream repo is (aka the source)

#### Pulling changes from the upstream repo (source)

```bash
git pull --allow-unrelated-histories upstream main
```

> We need to use `--allow-unrelated-histories` to allow this type of pull command

If the command doesn't work as expected, try this one:

```bash
git fetch upstream
git merge upstream/main
```

#### Pushing changes to our branch (here)

```bash
git push origin <branch>
```

> This is standard

## Bot Invite

`https://discord.com/api/oauth2/authorize?client_id=742592739975233577&permissions=259912104770&scope=bot`
