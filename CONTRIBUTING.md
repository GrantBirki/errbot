# Contributing 🖥️

Looking to add a feature, enchance an existing one, or contribute to this bot? You have come to the right place!

The first step to contributing to this bot is getting your environment setup. This is covered on the main [README.md](README.md) document so make sure you have the `Prerequisites` section checked off before continuing.

> Note: This guide focuses around writing new tests and using a local environment. You will not be connecting to a chat service like Discord in this guide.. However, when you merge your changes to `main` they will be deployed and usable in Discord!

## Running the Bot Locally 🤖

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

You can now interact with `Errbot` from the command line!

Type a command like `.help` to get an output of all the commands that are available

So what *exactly* does `make local` do?

1. `docker-compose rm -fs`

    Removes and destroys any `errbot_chatbot` Docker containers (if running)

1. `docker-compose build`

    Rebuilds the `errbot_chatbot` Docker container and bakes in any new changes you have made

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

`.help`, `.uptime`, `.whoami`, `.example` are all examples of chatop commands

The first three commands listed above (`.help`, `.uptime`, `.whoami`) are **builtin** commands. This means that they come with the [errbot](https://github.com/errbotio/errbot) framework.

The last command listed above (`.example`) is a **plugin** command. This means that it is a chatop command which *we* created for our own use! This guide will focus on **plugins** which are chatops commands that we write and bake into our chatbot

</details>

<details>

<summary>Where are chatop commands stored?</summary>

They are stored in the `app/plugins` folder. Each chatop command is then stored in its own subfolder:

`app/plugins/example`

</details>

<details>

<summary>What is the <b>app/plugins/lib</b> folder?</summary>

Good thing you asked! This is a special folder for storing shared/common libraries between chatop commands.

For example, let's say you had two chatop functions `.send cat meme` and `.send dog meme`. People were spamming memes too fast so you needed to rate limit both commands. You could add a shared `rate_limit_memes()` function in `app/plugins/lib/common` and then import that function into both your **cat** and **dog** chatops. Check out the `app/plugins/lib` folder to see examples in action

</details>

Okay cool beans, now that we know a bit more about chatops commands, let's create a brand new one

### Creating a command

At the root of this repo you will notice a `template` folder. This folder contains the bare minimum code to create a brand new chatop command. Since copying this file from the `template` folder to the `app/plugins/template` folder takes about 1 brain cell too much, there is a script to do it for you.

Run the following command to copy the `template` folder into the plugin directory:

```bash
make command-template
```

Now enter the `app/plugins/template` folder and poke around the two files you see in there for a bit.

In order to make a new chatop command you just need to change a few lines to the new name of you function / functions.
