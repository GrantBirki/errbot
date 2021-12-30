<h2 align="center"><img src="docs/assets/errbot.png" alt="errbot" align="center" width="200px" /></h1>

<!--
<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
-->

<h2 align="center">errbot</h1>
<p align="center">
  A Dicord chatbot that is easy to deploy and build upon
</p>

<p align="center">
  <a href="https://github.com/GrantBirki/errbot/actions/workflows/ci-deploy.yml"><img src="https://github.com/GrantBirki/errbot/actions/workflows/ci-deploy.yml/badge.svg?event=push" alt="ci-deploy" height="18"></a>
  <a href="https://github.com/GrantBirki/errbot/actions/workflows/review.yml"><img src="https://github.com/GrantBirki/errbot/actions/workflows/review.yml/badge.svg?event=push" alt="review"/></a>
  <a href="https://github.com/GrantBirki/errbot/actions/workflows/tfsec.yml"><img src="https://github.com/GrantBirki/errbot/actions/workflows/tfsec.yml/badge.svg?event=push" alt="tfsec"/></a>
</p>

<p align="center">
  <img src="docs/assets/code-style-black.svg" alt="code style black"/>
  <img src="docs/assets/language-python-blue.svg" alt="language python"/>
  <img src="docs/assets/framework-errbot-blue.svg" alt="framework errbot"/>
  <img src="docs/assets/backend-discord-blue.svg" alt="backend discord"/>
</p>

<p align="center">
  <img src="docs/assets/terraform.svg" alt="terraform"/>
  <img src="docs/assets/aws.svg" alt="aws"/>
  <img src="docs/assets/azure.svg" alt="azure"/>
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

> Note, this particular repo leans towards Discord for most things. However, as of this writing, all features of this bot work in Slack as well with the exception of having the bot join a voice channel as that is not a feature of Slack.. yet

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

### Project Components 🧰

**Key concepts**:

There are three main components to errbot:

- The chatbot itself - This is `errbot`, the python app running in a docker container which processes requests - `src/errbot/`
- The status page - This is the uptime-kuma docker app which accepts push events from the chatbot to display its health - `src/status_page/` - *add on service to the core chatbot*
- The NGINX reverse proxy - This is a simple NGINX server which proxies HTTP requests to the status page - `src/nginx/` - *add on service to the core chatbot*

The **status_page** and **NGINX** server are mainly just additions to the observability of **errbot**. The do not affect the functionality of the chatbot in any meaningful way.

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

> Note: for security reasons the `creds.env` file is not committed to this repo and NEVER should be. Reach out to @grantbirki to obtain the credz

If you followed the steps above and everything succeeded, you should get a DM from the bot stating that it is "Now Online". You should note that you will only get this message if `BOT_ADMINS='@username'` is set to your username in the `config.env` file.

> Note x2: Running `make run` will start the `errbot-dev` bot and can be invoked with `!` rather than the usual `.`

Remember to read the **Project Components** section above to get a feel for the components of the bot that are created with this command.

---

## Making your own plugin / function 🔌

Check out the [CONTRIBUTING.md](CONTRIBUTING.md) file in this repo for all the info you will need to develop, test, and deploy!

> Note: The `make command` function exists to easily populate all the file you need to make a new plugin

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
  - `terraform/aws` - AWS related resources
  - `terraform/k8s-cluster` - The core components of the `errbot` k8s cluster
  - `terraform/k8s` - The k8s resources, services, manifests, secrets, etc to get deployed on the `k8s-cluster`
- `src/` - All the files, data, and configuration for `errbot` and its related services

  - `src/errbot/backend/` - Folder containing extra backend modules (Discord)
  - `src/errbot/` - Folder containing all the extra / custom plugins for our chatop commands
  - `src/errbot/lib/` - Folder containing shared libraries for plugins
  - `src/status_page/` - Folder containing the code for building the errbot status page (uptime-kuma)
  - `src/nginx/` - Folder containing the docker components for building the NGINX reverse proxy to handle HTTP requests for the status page

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

Core:

- This project uses [errbot](https://github.com/errbotio/errbot) which is a Python based chatop/chatbot framework
- `errbot` and all of its components are built using Docker to create a deployable image
- We use Terraform and GitHub actions to deploy the Docker image (from our CI/CD pipeline) to Azure AKS (Kubernetes)
- The Docker image runs in a container in Azure AKS and connects to Discord
- The bot then listens for commands and responds to them
- For any commands that require some form of "state" we use AWS DynamoDB to store information since containers are ephemeral by design
- We store any configuration as environment variables and secrets as k8s secrets which get injected into the container on boot

Status Page:

In addition to the core `errbot` container, we also deploy a **status page** to k8s which accepts HTTP requests that are interpreted as healthchecks from `errbot`. The project that is used is [uptime-kuma](https://github.com/louislam/uptime-kuma). The **status page** consists of two components: the "app" (kuma-uptime) and the NGINX reverse proxy.

- The status page source code is built via Docker in CI/CD (`src/status_page`)
- The NGINX reverse proxy source code is built via Docker in CI/CD (`src/nginx`)
- The status page and NGINX images are deployed with Terraform and GitHub actions to our k8s cluster
- `errbot` will make HTTP GET requests to the `src/status_page` app at a set interval which gets registered as a healthcheck if it is successful (configured via the `STATUS_PUSH_ENDPOINT` environment variable)
- End users can view the status page which is accessible from the NGINX reverse proxy (kong ingress gateway is configured to forward requets to it)

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

## Bot Invite 🔗

Use the link below to invite the bot to a Discord server. This link includes pre-made permissions:

PROD:

`https://discord.com/api/oauth2/authorize?client_id=742592739975233577&permissions=259912104770&scope=bot`

DEV:

`https://discord.com/api/oauth2/authorize?client_id=880643531503448085&permissions=257764621120&scope=bot`
