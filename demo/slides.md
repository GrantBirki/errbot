---
# try also 'default' to start simple
theme: geist
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://source.unsplash.com/collection/94734566/1920x1080
# apply any windi css classes to the current slide
class: 'text-center'
# https://sli.dev/custom/highlighters.html
highlighter: shiki
# show line numbers in code blocks
lineNumbers: false
# some information about the slides, markdown enabled
info: |
  ## Intro to DevOps with Errbot
  An introduction to the world of DevOps

# persist drawings in exports and build
drawings:
  persist: false
---

# Intro to DevOps with <span>Errbot</span>

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    Press Space to begin the journey <carbon:arrow-right class="inline"/>
  </span>
</div>

<div class="abs-br m-6 flex gap-2">
  <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="text-xl icon-btn opacity-50 !border-none !hover:text-white">
    <carbon:edit />
  </button>
  <a href="https://github.com/slidevjs/slidev" target="_blank" alt="GitHub"
    class="text-xl icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

<style>
span {
  background-color: #2B90B6;
  background-image: linear-gradient(45deg, #4EC5D4 10%, #146b8c 20%);
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---

# What is DevOps?

DevOps is a set of combined practices that merge development (Dev) and operations (Ops) together

- 💡 Continuous planning
- ⚡ Rapid application development
- 👯 Sharable development environments
- 🤖 Automated and repeatable builds & tests
- 🚀 CI/CD pipelines
- 🔭 Obervability
- 🔒 Security

<br>
<br>

Read more about [what is DevOps](https://en.wikipedia.org/wiki/DevOps)

<!--
You can have `style` tag in markdown to override the style for the current page.
Learn more: https://sli.dev/guide/syntax#embedded-styles
-->

<style>
h1 {
  background-color: #2B90B6;
  background-image: linear-gradient(45deg, #4EC5D4 10%, #146b8c 20%);
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

---

# DevOps Visualized

![DevOps Visualized](assets/devops-loop.svg)

---

# Plan 💡

The planning phase of DevOps is often [agile software development](https://en.wikipedia.org/wiki/Agile_software_development)

- • Iterative
- • Continuous
- • Can (and will) change frequently
- • No "big bang" launch, an iterative approach

> For this demo we will be planning the launch of a new chat bot command `.devops`

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Code 💻

The coding phase of DevOps is where ideas come to life... and where nightmares are born

```python
if production == "down":
  print("This does not bring joy")
```

- 👯 Develop in sharable and automated environments
- 🖌️ Adopt a common code style (use a linter)
- ⚙️ Use a version control system
- 💾 Commit and push often
- 👀 Work in the open, get feedback, request reviews

> For the DevOpsDaysLA demo, we will be writting code in [GitHub codespaces](https://github.com/features/codespaces)

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Build 📦

The build phase of DevOps is where the code is compiled and often saved as an artifact for later deployment

- 🛠️ Build your application / binaries in a repeatable environment (CI/CD)
- 🐳 Containerize applications and services where you can
- 🔒 Secure your software supply chain when building applications
- 🔑 Seperate packages, containers, and binaries from configurations and secrets

> For the DevOpsDaysLA demo, we will be using Docker to containerize and build our application

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Test 🧪

The test phase of DevOps is where the application is... tested!

- 👯 Repeatable test environment (CI/CD + Docker)
- 👨‍🔬 Unit tests
- 🌐 Integration tests
- 🔬 Container scanning
- 🔎 SAST & DAST - Code scanning

> For the DevOpsDaysLA demo, you will get exposure to unit tests, container scanning, and static analysis

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Release 🏷️

TODO

---

# Deploy 🚀

TODO

---

# Operate 🧰

TODO

---

# Monitor 🔎

TODO

---

# What is Errbot? 🤖

[Errbot](https://github.com/GrantBirki/errbot) is an implementation of the [errbotio/errbot](https://github.com/errbotio/errbot) framework.

My version of errbot differs from the original in the following ways:

- • Containerized
- • Comes with pre-built features and chat commands
- • Custom helper functions
- • Altered base plugins and code
- • Custom configuration

> My version of errbot is specifically built around Discord, but many features natively support Slack as well. Check out the upstream source for [errbotio/errbot](https://github.com/errbotio/errbot) to learn more about supported backends, configuration, and bot development

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# What can Errbot do?

Errbot can do **literally** anything you can write Python code to do!

> [Errbot Video Demo](https://giant.gfycat.com/UnripeReasonableErmine.mp4)

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Errbot for Fun

- • Get the [DownDetector](https://downdetector.com/) status of a service
- • Complement or Insult your friends
- • Remember a string of text for later
- • Get a random fact
- • Get the weather
- • Find the value of an item in a game
- • Join a Discord channel and play some music
- • Get the price of a stonk or crypto currency
- • Read a message over text to speech

---

# Errbot for Work

- • Get the status of a deployed service
- • DNS lookups
- • Update a firewall rule
- • Start a Kubernetes deployment
- • Trigger a deployment
- • Merge a pull request
- • Create a GitHub issue
- • Add a comment to a servicenow ticket
- • Create a Jira issue
- • Page an on-call engineer
- • Post your daily standup status
- • Get a post service metrics to a channel

---

# Hands-on Workshop Time 👐

In this workshop, we will be doing the following:

- 📚 Build our documentation page - [GitHub Pages](https://pages.github.com/)
- 💻 Implement our new `.devops` chatbot command
- 📦 Building the bot using [skaffold](https://skaffold.dev/) with our new command (Thanks [@murriel](https://github.com/murriel)!)
- 🧪 Ensure our test suite is passing
- 🔒 Run SAST on our code and container scanning on our container image
- 🤹 Interact and use our new chat command
- 🔭 Observe our bot's usage with Grafana & Loki
- 🚀 Run a real world CI/CD pipeline and deployment

---

# Getting Started 💡

- 1: Go to [github.com/DevOpsDaysLA/workshop-1](https://github.com/DevOpsDaysLA/workshop-1) and click "Fork" in the upper right corner
- 2: Ensure you fork the repo into the [DevOpsDaysLA](https://github.com/DevOpsDaysLA) organization. Note: If you are not part of the DevOpsDaysLA workshop, you can fork the repo to your personal GitHub account instead
- 3: Upon the successful fork, you will notice a GitHub action workflow has started for your documentation page
- 4: Go to your repo settings and ensure your GitHub pages site is accessible to view your documentation

![GitHub Pages](assets/pages.png)

---

# GitHub Pages 📄

[GitHub Pages](https://pages.github.com/) is a free service for hosting static website content on GitHub.com

Commits / Pushes to the `main` branch automatically update our documentation site

```yaml
name: pages
on:
  push:
    branches:
      - main
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@ec3a7ce113134d7a93b817d10a8272cb61118579 # pin@v2
      - uses: actions/setup-python@f38219332975fe8f9c04cca981d674bf22aea1d3 # pin@v2
        with:
          python-version: 3.x
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

---

# Pages GitHub Actions Workflow ⏩

![Pages Workflow](assets/pages-workflow.png)

Hooray! We not have all the nitty gritty documentation for our bot publically hosted on GitHub Pages!

---

# Setup

To begin implementing our `.devops` bot command, we need to first start our dev environment:

**DevOpsDaysLA Workshop:**

Simply create a new GitHub Codespace

![GitHub Codespace](assets/codespaces-launch.png)

**Non-DevOpsDaysLA Workshop:**

[Public setup documentation](https://errbot.birki.io/)

---

# Codespaces 💻

If you are apart of the DevOpsDaysLA workshop, you will be able to create a new GitHub Codespace for development

**What is GitHub Codespaces?**

- ☁️ Cloud hosted development environment
- 👯 Consistent, repeatable, and shareable
- 🚧 Removes the "it works on my machine" barrier
- 🔥 Saves us from dependency hell
- ⭐ Allows developers to deploy a dev environement in one-click and begin working on a project

You can read more about GitHub Codespaces [here](https://github.com/features/codespaces)

> Note: If you are not apart of the DevOpsDaysLA workshop, you will **not** have free access to GitHub codespaces and will need to setup errbot [locally for development](https://errbot.birki.io/setup/)

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Connect to Codespace

![Connect to Codespace](assets/codespaces-connect.png)

You will now connect to Codespaces through your browser. If you have [Visual Studio Code](https://code.visualstudio.com/) installed, you can optionally attach there as well.

Our Codespace environment comes pre-installed with all the dependencies we need to run errbot locally and develop new features.

> Note: If you are **not** apart of the DevOpsDaysLA workshop, you will be doing all the following steps from here on locally and not in GitHub Codespaces

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Generating a Bot Token 🔑

The first step to build our bot locally is to generate a bot token. This workshop uses Discord but you can also use Slack or [other chat services](https://errbot.readthedocs.io/en/latest/user_guide/setup.html#id1) as well.

**Discord:**

- 1: Navigate to the [Discord App Dashboard](https://discord.com/developers/applications)
- 2: Click the "New Application" button - Name your bot `firstname-errbot-dev`
- 3: Click the "Bot" tab -> "Add Bot"
- 4: Copy down your bot token
- 5: Under the "General Information" tab, copy down your bot's `application id`

![Discord Bot Token Copy](assets/discord-bot-token-copy.png)

---

# Configure the Bot 🔧

For this step, all you need to do is "check the box" for "Server Members Intent":

![Server Members Intent](assets/discord-bot-server-members-intent.png)

---

# Invite the Bot 🔗

The next step is to invite your newly created bot to your Discord server.

Use the `application id` from the previous step to invite your bot to your server and paste it into the link below:

```text
https://discord.com/api/oauth2/authorize?client_id=<application_id>&permissions=36734976&scope=bot
```

Paste the formatted link above link into your browser and add the bot to your desired server!

> For the DevOpsDaysLA workshop you can join the following Discord server for testing and bot invites: [Server Invite Link](https://discord.gg/76q9Ca4RzW)

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Setup Bot Token 🔑

From your codespace (or local) console, execute the following commands:

Create the `secret.yaml` file for your local k8s deployment:

```text
cp script/k8s/errbot/secret.yaml.example script/k8s/errbot/secret.yaml
```

[base64](https://kubernetes.io/docs/concepts/configuration/secret/#overview-of-secrets) encode your bot token (from the previous slide):

```text
python3 script/base64string.py --string <bot_token>
```

Add your base64 encoded bot token to the `script/k8s/errbot/secret.yaml` file:

`"${CHAT_SERVICE_TOKEN}"` -> `"your-bot-token-here"`

---

# Bot Admin 👨‍🔬

Before you start your bot, set yourself as the bot admin:

Edit the `script/k8s/errbot/deployment.yaml` file like so:

`value: "Birki#0001" # change to your own handle` -> `value: "yourname#0001"`

> Note: You can find your `name#id` in the bottom left of your Discord client or on your profile page

![Discord Name + ID](assets/discord-profile-id.png)

---

# Start the Bot with Skaffold ☸️

We will be using [Skaffold](https://skaffold.dev/) to run our bot for development (either in Codespaces or locally)

Start our [minikube](https://minikube.sigs.k8s.io/docs/start/), cluster:

> Note: You may need to run `sudo chown -R $USER $HOME/.minikube; chmod -R u+wrx $HOME/.minikube` to start your minikube cluster in Codespaces

```text
minikube start --profile custom

skaffold config set --global local-cluster true

eval $(minikube -p custom docker-env)
```

Run the bot with Skaffold (and tail the logs):

```text
skaffold dev --tail=true
```

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Development Environment 1,000 Foot Overview 🦅

While the Skaffold command is running, let's look at our dev env ([source](https://errbot.birki.io/deployment/)):

![Project Directories](assets/project-directories.png)

---

# Kubernetes Files 📂

The `script/k8s/` directory contains all the files we need to deploy our bot to Kubernetes locally (using Skaffold)

**Benefits of using Skaffold:**

- • Live reload (changes to source files or k8s manifests)
- • Handles all `kubectl` commands for us
- • Faster dev cycles
- • Very close to our production environment (if not identical)

**Alternative dev building options:**

- 🐳 Docker-compose - The `make run` command from the root of this repo is a wrapper command for building locally with Docker-compose
- ☸️ Minikube - The `make kube` command from the root of this repo is a wrapper command for building locally with minikube using `kubectl`

---

# Back to the Terminal 💻

Going back to our terminal, we should see live output from our bot running in k8s via skaffold.

Additionally, the following has happened:

- • 🟢 The configured bot owner got a ping that the bot is now online
- • 💬 The bot can now been as online on our Discord server
- • ⌨️ We can now type a command and our bot will respond -> `!uptime`

Let's go ahead and press `ctrl+c` in our terminal running skaffold to stop the bot

> Note: You can also test out other commands that are available. Try `!help`

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Creating our very own chat command!

> 💡 Plan Stage of DevOps

We want a new command that returns a link to the DevOps life-cycle

Discord will conveniently render this link as an image for us.

This will be a brand new chat command so we will need to implement it and add the associated tests for our new code

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Code for the Chat Command 📝

> 💻 Code Stage of DevOps

Another engineer has already written most of the code for our new command.

Let's copy that code into our `src/errbot/plugins/` directory:

```text
mkdir src/errbot/plugins/devops

cp demo/code/devops/* src/errbot/plugins/devops/
```

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Build with Skaffold ☸️

> 📦 Build Stage of DevOps

Now that we have our new command, we need to build our bot with Skaffold:

```text
skaffold dev --tail=true
```

Once the container starts up, run the new command: `!devops`

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Fix our Command 🚨

> 💻 Code Stage of DevOps

Oh no! Our command is borked! Back to our editor to fix the bad code:

```python
# Delete these lines
if self.chaos():
  return "CHAOS"
...
# Delete this function
def chaos(self):
  """
  This does not bring joy
  """
  if random() > 0.5:
    return True
  else:
    return False
```

Redeploy and test with `skaffold dev --tail=true` -> `!devops`

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Run our Test Suite 🔬

> 🧪 Test Stage of DevOps

The other engineer also wrote some tests for us, let's copy those over as well:

```text
cp demo/code/tests/devops_test_example.py tests/plugins/test_devops.py
```

Run the test suite using [pytest](https://docs.pytest.org/en/latest/):

```text
script/test
```

> Note: Tests like to live in CI/CD pipelines

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Fix our Test 🚨

> 🧪 Test Stage of DevOps

Checking our test output, we expect that a a url with a `.jpg` extension is returned. However, the actual image we are returning is a `.png`. Let's fix that:

```python
# tests/plugins/test_devops.py
assert "demo/assets/devops.png" in testbot.pop_message()
```

🎉

![Tests Passing](assets/tests-passing.png)

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# SAST 🔎

> 🔒 Security Stage of DevOps - Shift Left!

[SAST](https://en.wikipedia.org/wiki/Static_application_security_testing) is a testing methodology for detecting security vulnerabilities in software.

It generally takes place by scanning files and looking for misconfigurations, bad practices, and other security issues.

> Note: SAST likes to live in CI/CD pipelines

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# TFSEC 🔒

> 🔒 Security Stage of DevOps - Shift Left!

[TFSEC](https://github.com/aquasecurity/tfsec) is a SAST testing tool that scans Terraform files for security issues.

Let's run it and check the output:

```text
tfsec terraform/
```

We won't make any changes here but it is good to get familiar with the tool

> Note: TFSEC likes to live in CI/CD pipelines

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# KUBESEC 🔒

> 🔒 Security Stage of DevOps - Shift Left!

[KUBESEC](https://github.com/controlplaneio/kubesec) is another SAST tool for scanning kubernetes manifests.

**Example Usage:**

```text
kubesec scan script/k8s/errbot/deployment.yaml | jq
```

**Make a check fail and then fix it again:**

1. 1: Edit: `script\k8s\errbot\deployment.yaml` -> comment out: `runAsUser: 10001`
2. 2: Run: `kubesec scan script/k8s/errbot/deployment.yaml | jq`
3. 3: Observe the output warning that the `runAsUser` check is now failing
4. 4: Fix it back by uncommenting the `runAsUser` field in the k8s manifest

> Note: KUBESEC likes to live in CI/CD pipelines

<style>
blockquote {
  color: #A9A9A9;
}
</style>

---

# Learn More

[Documentations](https://sli.dev) · [GitHub](https://github.com/slidevjs/slidev) · [Showcases](https://sli.dev/showcases.html)
