# Deployment

> Note: This section is mostly for my own docs for this repo and its contributors. You can use it as a guide for your own fork of this project

Deploying your changes to the prod instance of `errbot` is *really* easy.

We will use the `.cat meow` example from the [development](development.md) section

All you need to do is the following:

1. Create a new branch `cat-meow-feature`
1. Commit your changes to the `cat-meow-feature` branch
1. Push your changes
1. Open up [github.com/GrantBirki/errbot/pulls](https://github.com/GrantBirki/errbot/pulls) and create a new pull request
1. Wait for [CI](https://en.wikipedia.org/wiki/Continuous_integration) to finish and for all checks to pass
1. View your Terraform output and ensure it looks like it is doing what you want it to (ie: not destroying resources)
1. Request review on your pull request and obtain an approval (@grantbirki or any other member)
1. Merge your pull request and your change will be automatically deployed! 🚀✨
1. Run `.cat meow` in Discord to see your command in action 🐈

## Tagging a Release 🏷

Once you have deployed your changes via a merge, it is recommended to create a new release via a Git tag

This can be easily accomplished by using the following helper script:

```text
script/release
```

This will create a tag with the following format (**vX.X.X**) and push it to the remote repo

If you changes are minor and do not require a release, you may skip this step

> Create release tags from the main branch

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

## What's next?

Continue on to the [observability](observability.md) section to learn more about how to observe and monitor your bot's performance 🔭
