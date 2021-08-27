<h2 align="center"><img src="docs/assets/errbot.png" alt="errbot" align="center" width="200px" /></h1>

<h2 align="center">errbot</h1>
<p align="center">
  A Dicord chatbot that is easy to deploy and build upon
</p>

<p align="center">
  <a href="https://github.com/GrantBirki/errbot/actions/workflows/deployment.yml"><img src="https://github.com/GrantBirki/errbot/actions/workflows/deployment.yml/badge.svg?event=push" alt="deployment" height="18"></a>
  <a href="https://github.com/GrantBirki/errbot/actions/workflows/review.yml"><img src="https://github.com/GrantBirki/errbot/actions/workflows/review.yml/badge.svg?event=push" alt="review" /></a>
  <a href="https://github.com/GrantBirki/errbot/actions/workflows/tfsec.yml"><img src="https://github.com/GrantBirki/errbot/actions/workflows/tfsec.yml/badge.svg?event=push" alt="tfsec"/></a>
</p>

<hr>

## About 💡

This project uses [errbot](https://github.com/errbotio/errbot) and [Docker](https://www.docker.com/) to quickly launch your own chatbot in a container.

The goal of this project is to make it as easy as possible to launch a minimal, working chatbot.

> Note: This repo is a fork of my other project [errbot-launchpad](https://github.com/GrantBirki/errbot-launchpad)

## Quickstart ⭐

Want to get going quick? Run the following commands to bring up a CLI to interact with `errbot` locally:

1. `git clone git@github.com:GrantBirki/errbot.git`
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

> Note, this particular repo does not use Slack. It is a Discord app!

#### Discord

> This bot has already been provisioned to Discord. It is included as a reference should the bot ever need to be rebuilt

With Discord, things are a little different. You will need to first enable `SERVER MEMBERS INTENT` for your bot application. After that, you need to go into the Oauth2 page for your bot and select the `bot` scope. This will expand more options. You may go as crazy or as restrictive as you want with the chat permissions. That part is totally up to you.

Once your permissiosn are scoped out, you will need to copy the oauth2 link that is generated.

It could look something like this: `https://discord.com/api/oauth2/authorize?client_id=<number>&permissions=<number>&scope=bot`

> Note: You can find an example invite link farther below

Enter that link into your web browser and it should give you a list of servers to invtire your bot to. Add it to your favorite server!

To setup your bot, you will need to modify your `config.env` file. To make things easier, there is a `config.example.env` file in the root of this repo.

1. Rename `config.example.env` to `config.env` *required
1. Set `BACKEND=<backend>` *required
1. Set `CHAT_SERVICE_TOKEN='<token>'` *required
1. Change `BOT_PREFIX='!'` if you want *optional

---

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

### Testing and Building Connected to Discord ⌨️

Completed the simple setup? Awesome! Let's start the bot:

> Note: `make run` will start the bot and attach it to Discord for usage. If you are looking to start a local instance of the bot, see the `Testing and Building Locally` section below

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

> Note: for security reasons the `creds.env` file is not commited to this repo and NEVER should be. Reach out to @grantbirki to obtain the credz

If you followed the steps above and everything succeeded, you should get a DM from the bot stating that it is "Now Online". You should note that you will only get this message if `BOT_ADMINS='@username'` is set to your username in the `config.env` file.

> Note x2: Running `make run` will start the `errbot-dev` bot and can be invoked with `!` rather than the usual `.`

---

## Making your own plugin / function 🔌

Check out the [CONTRIBUTING.md](CONTRIBUTING.md) file in this repo for all the info you will need to develop, test, and deploy!

---

## Fork Notice 🍴

> Note: You probably won't need to worry about this ever. Mostly just notes for @grantbirki

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

---

## Project Folder/File Information 📂

What is in each folder?

- `.github/` - Mainly GitHub workflows for actions
- `script/` - Maintenance and automation scripts for working with this project
- `template/` - Template / boilerplate code for new chatops commands
- `terraform/` - Terraform code for deploying `errbot` resources
- `app/` - All the files, data, and configuration for `errbot`

  - `app/backend/` - Folder containing extra backend modules (Discord)
  - `app/plugins/` - Folder containing all the extra / custom plugins for our chatop commands

What are these files?

- `.gitignore` - Used for ignoring files from Git
- `config.env` - Used for adding non-sensitive environment variables to your local instance of `errbot`
- `creds.env` - Used for adding sensitive environment variables to your local instance of `errbot`
- `docker-compose.yml` - Used for starting `errbot` locally with Docker-Compose
- `Makefile` - Used to easily invoke scripts in this repo
- `*.md` - Documentation!

---

## About the Infrastructure 🧱

Here is a high level overview of this project and the software/infrastruce that run this bot:

- This project uses [errbot](https://github.com/errbotio/errbot) which is a Python based chatop/chatbot framework
- `errbot` and all of its components are built using Docker to create a deployable image
- We use Terraform and GitHub actions to deploy the Docker image (from our CI/CD pipeline) to Azure
- The Docker image runs in a container in Azure and connects to Discord
- The bot then listens for commands and responds to them
- For any commands that require some form of "state" we use Azure Cosmos DB to store information since containers are ephemeral by design
- We store any configuration or credentials as environment variables which get injected into the container in our CI/CD builds

---

## Bot Invite 🔗

Use the link below to invite the bot to a Discord server. This link includes pre-made permissions:

PROD:

`https://discord.com/api/oauth2/authorize?client_id=742592739975233577&permissions=259912104770&scope=bot`

DEV:

`https://discord.com/api/oauth2/authorize?client_id=880643531503448085&permissions=257764621120&scope=bot`
