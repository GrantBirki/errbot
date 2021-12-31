# Slack

The main [errbot](https://github.com/errbotio/errbot) chatbot framework supports many different backends. Since this is a modified version of that framework, certain features work a little differently. Especially since it has been bundled as a Docker container for ease of deployments.

To date I have not tested any other backends besides Discord and Slack. The good news is that both of these backends are supported with this version of [errbot](https://github.com/errbotio/errbot).

There are slight differences between the two services so certain features will not work. For example, if you ask the bot to join a voice channel via the Discord backend it will work. However, Slack does not have voice channels at this time of writting so that feature will not work.

## Enabling the Slack Backend

Backends and their configurion are setup mostly with environment variables. The steps below will walk you through what needs to be done to setup your bot to use Slack instead of Discord.

1. Follow the [official errbot docs](https://errbot.readthedocs.io/en/latest/user_guide/configuration/slack.html) to create a Slack bot and the corresponding token (save this token for the next step)
1. Paste the token you get from Slack into your `creds.env` file

    ```ini
    CHAT_SERVICE_TOKEN='xoxb-token-here' # Slack
    ```

1. Edit the `config.env` file to set your backend to Slack

    ```ini
    BACKEND='Discord'
    ```

1. Edit the `config.env` file to set the bot admin(s)

    ```ini
    BOT_ADMINS='@grant.birkinbine' # Slack example (your true Slack username)
    ```

1. Disable the following lines as you will not be using the Discord backend and Slack does not support an option for a "bot status"

    ```ini
    # BOT_EXTRA_BACKEND_DIR='/app/backend/err-backend-discord'
    # BOT_STATUS_MESSAGE='errbot | .help'
    ```

1. Lastly, edit the `src/errbot/requirements.txt` file to enable Slack related pip packages. Look for the line that is a comment related to Slack and simply uncomment all the lines (packages) below it

    ```python
    # errbot[slack] # Uncomment all the lines below this one to enable Slack support
    ...
    ..
    .
    ```

1. 🎉

Now when you start your bot with `make run` it will automatically connect to Slack and use that as its backend
