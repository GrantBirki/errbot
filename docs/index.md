# Errbot 🤖

**A Dicord chatbot that is easy to deploy and build upon!**

This project uses [errbot](https://github.com/errbotio/errbot) and [Docker](https://www.docker.com/) to quickly launch your own chatbot in a container.

The goal of this project is to make it as easy as possible to launch a minimal, working chatbot.

> Note: This repo is a fork of my other project [errbot-launchpad](https://github.com/GrantBirki/errbot-launchpad) - errbot-launchpad is a way more basic version of this project

**Looking for the bot commands documentation?**

Check it out [here](commands.md)!

## Quickstart ⭐

Want to get going quick? Run the following commands to bring up a CLI to interact with `errbot` locally:

1. `git clone git@github.com:GrantBirki/errbot.git`
2. `cd errbot`
3. `make local`

Didn't work quite right? See the setup section below..

---

## Setup

### Prerequisites

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

> Note, this particular repo leans towards Discord for most things. However, as of this writing, all features of this bot work in Slack as well with the exception of having the bot join a voice channel as that is not a feature of Slack.. yet

#### Discord

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

### Project Components

**Key concepts**:

There are three main components to errbot:

- The chatbot itself - This is `errbot`, the python app running in a docker container which processes requests - `src/errbot/`

### Testing and Building Locally

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

### Testing and Building Connected to Discord

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

> Note: for security reasons the `creds.env` file is not committed to this repo and NEVER should be. Reach out to @grantbirki to obtain the credz

If you followed the steps above and everything succeeded, you should get a DM from the bot stating that it is "Now Online". You should note that you will only get this message if `BOT_ADMINS='@username'` is set to your username in the `config.env` file.

> Note x2: Running `make run` will start the `errbot-dev` bot and can be invoked with `!` rather than the usual `.`

Remember to read the **Project Components** section above to get a feel for the components of the bot that are created with this command.

---

## Making your own plugin / function

Check out the [CONTRIBUTING.md](CONTRIBUTING.md) file in this repo for all the info you will need to develop, test, and deploy!

> Note: The `make command` function exists to easily populate all the file you need to make a new plugin

---

## Project Folder/File Information

What is in each folder?

- `.github/` - Mainly GitHub workflows for actions
- `script/` - Maintenance and automation scripts for working with this project
- `script/localstack/` - Files and Dockerfiles related to building the localstack container for development
- `template/` - Template / boilerplate code for new chatops commands
- `terraform/` - Terraform code for deploying `errbot` resources
  - `terraform/aws` - AWS related resources
  - `terraform/k8s-cluster` - The core components of the `errbot` k8s cluster
  - `terraform/k8s` - The k8s resources, services, manifests, secrets, etc to get deployed on the `k8s-cluster`
- `src/` - All the files, data, and configuration for `errbot` and its related services

  - `src/errbot/backend/` - Folder containing extra backend modules (Discord)
  - `src/errbot/` - Folder containing all the extra / custom plugins for our chatop commands
  - `src/errbot/lib/` - Folder containing shared libraries for plugins

What are these files?

- `.gitignore` - Used for ignoring files from Git
- `config.env` - Used for adding non-sensitive environment variables to your local instance of `errbot`
- `creds.env` - Used for adding sensitive environment variables to your local instance of `errbot`
- `docker-compose.yml` - Used for starting `errbot` locally with Docker-Compose
- `Makefile` - Used to easily invoke scripts in this repo
- `*.md` - Documentation!

---

## About the Infrastructure

Here is a high level overview of this project and the software/infrastruce that run this bot:

Core:

- This project uses [errbot](https://github.com/errbotio/errbot) which is a Python based chatop/chatbot framework
- `errbot` and all of its components are built using Docker to create a deployable image
- We use Terraform and GitHub actions to deploy the Docker image (from our CI/CD pipeline) to Azure AKS (Kubernetes)
- The Docker image runs in a container in Azure AKS and connects to Discord
- The bot then listens for commands and responds to them
- For any commands that require some form of "state" we use AWS DynamoDB to store information since containers are ephemeral by design - We use [LocalStack](https://github.com/localstack/localstack) to mock AWS when developing locally 😉
- We store any configuration as environment variables and secrets as k8s secrets which get injected into the container on boot

---

## Mkdocs Documentation 📚

To view and serve a local version of the [Mkdocs](https://mkdocs.org/) documentation for this project, run the following command:

```console
$ mkdocs serve
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.17 seconds
INFO     -  [22:56:00] Serving on http://127.0.0.1:8000/
```

---

## Deploying from Scratch to Azure with GitHub Actions

> This sections is mostly my own notes and for those who are deploying this project with GitHub Actions to Azure AKS

If there are currently **no** resources deployed for this project you will need to follow the steps below to "deploy from scratch":

1. Run the `make build` command from the root of this repo
1. Once the local deploy is complete, login to your Azure account and go to the errbot ACR registry that was created
1. Copy the ACR `username` and `password` and add it to GitHub Actions secrets
1. Copy your `~/.kube/config` file and add it to GitHub Actions secrets
1. You may now deploy the pipeline through GitHub Actions

---
