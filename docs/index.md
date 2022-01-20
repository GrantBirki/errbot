# Errbot 🤖

**A Dicord chatbot that is easy to deploy and build upon!**

This project uses [errbot](https://github.com/errbotio/errbot) and [Docker](https://www.docker.com/) to quickly launch your own chatbot in a container.

The goal of this project is to make it as easy as possible to launch a minimal, working chatbot.

> Note: This repo is a fork of my other project [errbot-launchpad](https://github.com/GrantBirki/errbot-launchpad) - errbot-launchpad is a way more basic version of this project. This project that you are currently reading about 👀 is packed full of features and chatbot command that are ready to use out of the box! It is a work in progress though so beware of bugs!

**Looking for the bot commands documentation?**

Check it out [here](commands.md)!

## Quickstart ⭐

Want to get going quick? Run the following commands to bring up a CLI to interact with `errbot` locally:

1. `git clone git@github.com:GrantBirki/errbot.git`
2. `cd errbot`
3. `make local`

---

## Development Guide

Check out the [development](development.md) guide in this repo for all the info you will need to develop, test, and build your bot!

In this guide you will find details about how the bot works, and how you can create your own new chatbot commands.

> Just make sure to walk through the [setup](setup.md) section before you start!

---

## Mkdocs Documentation 📚

> _Docs about docs? WhOa sO mEtA_

Do you want to build and read the documentation locally? Perhaps you have a suggestion and want to visualize how it will look when deployed with GitHub Pages?

To view and serve a local version of the [Mkdocs](https://mkdocs.org/) documentation for this project, run the following command:

```console
$ mkdocs serve
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.17 seconds
INFO     -  [12:61:00] Serving on http://127.0.0.1:8000/
```

## What's next?

Continue on to the [setup](setup.md) section to get your environment setup and ready to build!
