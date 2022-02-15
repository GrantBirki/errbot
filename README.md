<h2 align="center"><img src="docs/assets/errbot.png" alt="errbot" align="center" width="200px" /></h1>

<!--
<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
-->

<h2 align="center">errbot</h1>
<p align="center">
  A chatbot that is easy to deploy and build upon - It can do literally anything
</p>

<p align="center">
  <a href="https://github.com/GrantBirki/errbot/actions/workflows/deploy-ci.yml"><img src="https://github.com/GrantBirki/errbot/actions/workflows/deploy-ci.yml/badge.svg?event=push" alt="deploy-ci" height="18"></a>
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

This project uses [errbot](https://github.com/errbotio/errbot) (hence the name) and [Docker](https://www.docker.com/) to quickly launch your own chatbot in a container which is highly extensible! Use this dockerized version of Errbot to self-host your very own chatbot for popular services like Slack / Discord. Anything you can write Python 🐍 code to do, you can do with Errbot!

There are two ways you can use this bot:

1. Invite the bot to your own Discord server - You can even contribute to this repo to add your own commands!
2. Self-host the bot yourself to build upon it

> Check out [errbot-launchpad](https://github.com/GrantBirki/errbot-launchpad) if you don't want all the bells and whistles of this project.

## Quickstart ⭐

Want to get going quick? Run the following commands to bring up a CLI to interact with `errbot` locally:

1. `git clone git@github.com:GrantBirki/errbot.git`
2. `cd errbot`
3. `make local`

Didn't work quite right? Want to actually connect to a chat service? Check out the [docs](https://errbot.birki.io)

> Want to jump to the `Turbo Quickstart` for Discord guide? Check it out [here](https://errbot.birki.io/discord-turbo-quickstart/)

## Writing Plugins 🧰

Writing and creating your own plugins is extremely easy! The snippet below shows you how to create your own chatbot function in just a few lines of code:

```python

from errbot import BotPlugin, botcmd

class Hello(BotPlugin):
    """Example 'Hello, world!' plugin for Errbot"""

    @botcmd
    def hello(self, msg, args):
        """Return the phrase "Hello, world!" in chat"""
        return "Hello, world!"
```

> Tip: Running `make command` from the root of this repo will give you some prompts to follow and will drop the above snippet in the correct folder

The result of the plugin code above is a new chatop command:

![Hello, World Example](docs/assets/hello-world-example.png)

To learn more about plugin development, please check out the [development guide](https://errbot.birki.io/development)!

### Deployment and Hosting 🚀

If you do not wish to use this public version of errbot, you can clone this repo and self-host it anywhere you wish (yay opensource!).

This project builds a Docker container which you can deploy anywhere to bring your chatbot to life. Below are just a few example of all the many places you could deploy your chatbot container:

- Raspberry Pi
- Your own desktop
- Any virtual machine running Docker
- Public cloud container instances: ECS / Cloud Run / ACI
- Public cloud Kubernetes services: EKS / GKE / **AKS** ⭐

You may have noticed a "star" next to the **AKS** option. This is because it is the method I use to host my own instance of this project.

I have committed all my Terraform files which create and deploy my Azure Kubernetes Service (AKS) to this repo for reference. You will even notice GitHub actions running my pipeline publically for deployments. Feel free to use what I do as a guide, adapt it, and even improve upon it!

> Note: It is entirely up to you how you build, host, and deploy your container. There are tons of options and everyone has their own preferences.

For more details on deployment, you can check out my notes in the [deployment guide](https://errbot.birki.io/deployment)

### Documentation 📖

All the documentation for this project is available at [errbot.birki.io](https://errbot.birki.io).

You can also view the docs by browsing to the `docs/` directory in the root of this repository.

- [About](https://errbot.birki.io)
- [Setup](https://errbot.birki.io/setup)
- [Development](https://errbot.birki.io/development)
- [Commands](https://errbot.birki.io/commands)
