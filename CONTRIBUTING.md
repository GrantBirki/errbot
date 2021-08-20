# Contributing 🖥️

Looking to add a feature, enchance an existing one, or contribute to this bot? You have come to the right place!

The first step to contributing to this bot is getting your environment setup. This is covered on the main [README.md](README.md) document so make sure you have the `Prerequisites` section checked off before continuing.

> Note: This guide focuses around writing new tests and using a local environment. You will not be connecting to a chat service like Discord in this guide.. However, when you merge your changes to `main` they will be deployed and usable in Discord!

## Running the Bot Locally

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
