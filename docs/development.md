# Development

Looking to add a feature, enchance an existing one, or contribute to this bot? You have come to the right place!

The first step to contributing to this bot is getting your environment setup. This is covered on the main document under the [setup](setup.md) section so make sure you have the `prerequisites` section checked off before continuing.

## Understanding the Bot

Let's understand all the parts of the this repo so we are familiar before we begin

### About the Infrastructure

Here is a high level overview of this project and the software/infrastruce that run this bot:

Core:

- This project uses [errbot](https://github.com/errbotio/errbot) which is a Python based chatop/chatbot framework
- `errbot` and all of its components are built using Docker to create a deployable image
- We use Terraform and GitHub actions to deploy the Docker image (from our CI/CD pipeline) to Azure AKS (Kubernetes)
- The Docker image runs in a container in Azure AKS and connects to Discord
- The bot then listens for commands and responds to them
- For any commands that require some form of "state" we use AWS DynamoDB to store information since containers are ephemeral by design - We use [LocalStack](https://github.com/localstack/localstack) to mock AWS when developing locally 😉
- We store any configuration as environment variables and secrets as k8s secrets which get injected into the container on boot

### Project Folder/File Information

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

Okay, now let's get started!

---

## Running the Bot Locally 🤖

> This should look familiar from the [setup](setup.md) section

Let's create a local instance of `Errbot`:

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
[#] TEST Container is now running!
[#] Interact with me over the CLI prompt below

[@local_admin ➡ @errbot] >>>
```

You can now interact with `Errbot` from the command line!

Type a command like `.help` to get an output of all the commands that are available

So what *exactly* does `make local` do?

1. `docker-compose rm -fs`

    Removes and destroys any `errbot_chatbot` Docker containers (if running)

1. `docker-compose build`

    Rebuilds the `errbot_chatbot` Docker container and bakes in any new changes you have made. The Docker build packages up components from the `src/errbot` directory

1. Runs `docker run -it --rm --env-file config.env --env-file creds.env -e LOCAL_TESTING=True errbot_chatbot:latest` - Let's break this one down..

    1. This starts the `errbot_chatbot:latest` container in interactive mode (`-it`)
    1. Removes the container once you exit the CLI (`--rm`)
    1. Uses the `config.env` file to load **non-sensitive** environment variables (`--env-file config.env`)
    1. Uses the `creds.env` file to load **sensitive** environment variables (`--env-file creds.env`)
    1. Specifies the `LOCAL_TESTING=True` environment variable (`-e LOCAL_TESTING=True`) - Used in `app/config.py`
    1. Pops open a CLI prompt when complete for you to interact and issues commands to test and develop `errbot`

Okay, so we started up the bot, hooray! Now lets go over how to create a chatop command

## Creating a new ChatOp Command 🛠️

Before we create a new chatop command, let's go over it a bit.

### About ChatOp Commands

Click to expand each section and learn more about chatops

<details>

<summary>What is a chatop command?</summary>

<b>.help</b>, <b>.uptime</b>, <b>.whoami</b>, <b>.example</b> are all examples of chatop commands

The first three commands listed above (<b>.help</b>, <b>.uptime</b>, <b>.whoami</b>) are <b>builtin</b> commands. This means that they come with the <a href="https://github.com/errbotio/errbot">errbot framework</a>.

The last command listed above (<b>.example</b>) is a <b>plugin</b> command. This means that it is a chatop command which <i>we</i> created for our own use! This guide will focus on <b>plugins</b> which are chatops commands that we write and bake into our chatbot.

</details>

<details>

<summary>Where are chatop commands stored?</summary>

They are stored in the <b>src/errbot/plugins</b> folder. Each chatop command is then stored in its own subfolder:

<b>src/errbot/example</b>

</details>

<details>

<summary>What is the <b>src/errbot/lib</b> folder?</summary>

Good thing you asked! This is a special folder for storing shared/common libraries between chatop commands.

For example, let's say you had two chatop functions <b>.send cat meme</b> and <b>.send dog meme</b>. People were spamming memes too fast so you needed to rate limit both commands. You could add a shared <b>rate_limit_memes()</b> function in <b>src/errbot/lib/common</b> and then import that function into both your <b>cat</b> and <b>dog</b> chatops. Check out the <b>src/errbot/lib</b> folder to see examples in action

</details>

Okay cool beans, now that we know a bit more about chatops commands, let's create a brand new one

### Creating a command

At the root of this repo you will notice a `template` folder. This folder contains the bare minimum code to create a brand new chatop command. Since copying this file from the `template` folder to the `src/errbot/template` folder takes about 1 brain cell too many, there is a script to do it for you.

Run the following command to copy the `template` folder into the plugin directory:

```bash
make command
```

> Follow the prompts from this script and create a new command (maybe something like `.cat meme`)

<details>

<summary>Making a new command by hand (eww)</summary>

Enter the `src/errbot/template` folder and poke around the two files you see in there for a bit.

In order to make a new chatop command you just need to change a few lines to the new name of you function / functions.

Let's say we want to make a new chatop command that displays a cat meme and it is invoked by typing `.cat meme`. To do so, make the following changes:

1. Change the name of the `src/errbot/template` folder:

    `src/errbot/template` -> `src/errbot/catmeme`

1. Change the name of the `src/errbot/template/template.plug` file:

    `src/errbot/template/template.plug` -> `src/errbot/template/catmeme.plug`

1. Change the name of the `src/errbot/template/template.py` file:

    `src/errbot/template/template.py` -> `src/errbot/template/catmeme.py`

1. Inside of the `src/errbot/template/template.plug` file change all occurrences of `Template` or `template` to `Catmeme` or `catmeme`:

    Example: `Name = Template # Change me!` -> `Name = Catmeme`

    Example: `Module = template # Change me!` -> `Module = catmeme`

    > Note the cases of T/t and C/c above

1. Inside of the `src/errbot/template/template.py` file change the class name:

    `class Template(BotPlugin): # Change me!` -> `class Catmeme(BotPlugin):`

1. Inside of the `src/errbot/template/template.py` file change the function name:

    `def template(self, msg, args): # Change me! (function name)` -> `def cat_meme(self, msg, args):`

    > Note: We use `_` (underscores) in function names to represent spaces in our command. `def cat_meme(...)` becomes `.cat meme` via the chatop

1. To make the `.cat meme` command return something, edit the return message:

    `return 'Hello world, I am a template!'` -> `return 'meow!'`

</details>

That's it! 🎉

To test, `cd` to the root of this repo and run `make local`.

Your new plugin should be loaded and you can interact with it via the CLI:

```console
[@local_admin ➡ @errbot] >>> .cat meme

meow!
```

## Linting your code

In order for CI to pass, you must have properly linted code. Luckily, this is extremely easy to do and can be performed in a single command:

```console
$ script/lint

All done! ✨ 🍰 ✨
1 file reformatted, 14 files left unchanged.
```

That's it! This will lint all `*.py` files in the repo to ensure they conform to the [Black](https://black.readthedocs.io/en/stable/) linting guidelines

> Linting is just the formatting of your code to a certain standard (ie: no trailing whitespaces, "" quotes instead of '', etc)

---

## What's next?

Continue on to the [deployment](deployment.md) section to learn more about how to deploy your bot to production 🚀