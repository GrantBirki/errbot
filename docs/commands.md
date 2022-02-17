# Commands

The following commands are all available via the chatbot:

**Table Key:**

- **Command**: Self explanatory, the command to be executed by the chatbot
- **Example**: An example of the command and how to use it
- **Admin Only**: True/False - If the command is only available to bot admins
- **Description**: A brief description of the command
- **Availability**: Where the command is available. Possible options include:
    - 🌎 - Globally available everywhere the bot is present
    - 🔒 - Locked to certain servers / chatrooms (not publically available)
    - 🔒👨‍💻 - Locked to the bot admins
    - ❌ - Disabled

|  Command  |  Example   |  Description  |  Availability  |
|    :----:   |     :----:    |        :----:       |        :----:       |
| `.help`      | -         | The help command to view all available commands | 🌎 |
| `.docs` | - | View the public documenation link for the bot | 🌎 |
| `.about` | - | View information data about the chatbot | 🌎 |
| `.crypto`   | `.crypto btc` | Get the current price of a crypto currency | 🌎 |
| `.load` | - | Get the system load | 🌎 |
| `.ping` | -| Check if the bot is online | 🌎 |
| `.version`| - | See what version of the bot is running | 🌎 |
| `.random fact` | - | Get a random fun fact | 🌎 |
| `.status` | - | View the status of the bot | 🌎 |
| `.status gc` | - | View the garbage collection status of the bot | 🌎 |
| `.status plugins` | - | View the status of the bot plugins | 🌎 |
| `.stats` | - | Get the total stats for all the bot commands that have been used | 🌎 |
| `.uptime` | - | View the bots "uptime" | 🌎 |
| `.insult` | `.insult @errbot` | Insult a given user. Great with friends! | 🌎 |
| `.add me to league watcher` | `.add me to league watcher <summoner_name>` | Add a summoner to the League watcher to "watch" for their games and post messages in the #league channel | 🔒 |
| `.remove me from league watcher` | - | Remove your summoner from the League watcher | 🔒 |
| `.last match for` | `.last match for <summoner_name>` | Get the last League match data for a given summoner | 🌎 |
| `.lmf` | `.lmf <summoner_name>` | Get the last League match data for a given summoner (An alias for `.last match for`) | 🌎 |
| `.league disable` | - | Disable the League watcher | 🔒👨‍💻 |
| `.league enable` | - | Enable the League watcher | 🔒👨‍💻 |
| `.league streak` | - | View your current league win/loss streak | 🔒 |
| `.add to league watcher` | `.add to league watcher --summoner birki --discord birki#0001 --guild 12345` | Admin command to add a summoner + Discord handle combo to a given guild for the League watcher | 🔒👨‍💻 |
| `.remove from league watcher` | `.remove from league watcher --discord <discord_guild_id> --summoner <summoner_name>` | Admin command to remove a summoner in a specific discord guild from the league watcher | 🔒👨‍💻 |
| `.view my league watcher data` | `.view my league watcher data` | View your league watcher data | 🔒 |
| `.loud` | `.loud rickroll.mp3` | Play a very loud sound from the sounds folder on the bot | 🔒 |
| `.loud list` | - | List all the mp3 sound files which can be used by the `.loud` command | 🌎 |
| `.loud random` | - | Play a random sound from the sounds folder on the bot | 🌎 |
| `.play` | `.play <youtube_url>` | Play a song, or sound from YouTube - Optionally use `--queue <number>` to select the queue position to play the song | 🔒 |
| `.play help` | - | View a detailed and pretty help command for `.play` | 🔒 |
| `.play queue` | - | See what is in the `.play` queue | 🔒 |
| `.play stats` | - | See the all time stats for the `.play` command in your server | 🔒 |
| `.skip` | - | Skip the current song playing / at the top of the queue | 🔒 |
| `.stop` | - | Stop the current song and nuke the whole `.play` queue | 🔒 |
| `.rem` | `.rem <key> is <value>` | Have the bot remember something - Inspired by [hubot](https://github.com/github/hubot-scripts/blob/master/src/scripts/remember.coffee) under the MIT license | 🌎 |
| `.forget` | `.forget <key>` | Make the bot forget something that is being remembered | 🌎 |
| `.remember` | `.rememeber <key> is <value>` | The "longform" version of the `.rem` command | 🌎 |
| `.tts` | `.tts hello world! I will be read over text to speech` | Read a text message over text to speech in a voice channel (that you are connected to) | 🔒 |
| `.echo` | `.echo hello` | A simple command to echo back a message (Like the Linux "echo" binary) | 🌎 |
| `.history` | - | View the past few commands (history) that have been used by the bot | 🌎 |
| `.log tail` | - | Tail / View the bots latest log messages that have been written | 🔒👨‍💻 |
| `.users` | - | See a total count of all the users that 'could' interact with the bot in all servers | 🔒👨‍💻 |
| `.servers` | - | See a list of all active servers the bot is in | 🔒👨‍💻 |
| `.ban` | `.ban user#1234` | Ban a user from interacting with the bot | 🔒👨‍💻 |
| `.banned users` | - | View all the users that have been banned | 🔒👨‍💻 |
| `.unban` | `.unban user#1234` | Remove a ban for a given user | 🔒👨‍💻 |
| `.ban` | `.ban server 1234567890` | Ban an entire server from interacting with the bot | 🔒👨‍💻 |
| `.banned servers` | - | View all the servers that have been banned | 🔒👨‍💻 |
| `.unban server` | `.unban server 1234567890` | Remove a ban for a given server | 🔒👨‍💻 |
| `.render test` | - | Render a sample message with errbot to see how the chat service handles it | 🌎 |
| `.whoami` | - | Return a block of data about who the bot thinks you are | 🌎 |
| `.wallstreetbets` | - | View the top trending stonks from /r/wallstreetbets | 🌎 |
| `.sparkle` | `.sparkle @username for being awesome` | Sparkle a user to show your appreciation! (optionally provide a reason for the sparkling) - Inspired by [pwn](https://github.com/pmn/sparkles/blob/master/LICENSE.md) | 🌎 |
| `.show sparkles` | `.show sparkes` - `.show sparkles for @username` | View the sparkles (and their reasons) for yourself or another user - Inspired by [pwn](https://github.com/pmn/sparkles/blob/master/LICENSE.md)| 🌎 |
| `.down` | `.down twitter` | Get a DownDetector graph and the status for a given service | 🌎 |
| `.eft` | `.eft clock` | Get an Escape from Tarkov item and its value | 🌎 |
| `.eft ammo` | `.eft ammo 7.62x39mm` | Get information about an ammo type | 🌎 |
| `.eft ammo help` | - | Get information about the ammo types that can be used with the `.eft ammo` command | 🌎 |
| `.eft status` | `.eft status` - `.eft status --messages` | Get the current status of the Escape from Tarkov servers | 🌎 |
| `.eft map` | `.eft map shoreline` | Get an image of a map for a given Tarkov location | 🌎 |
| `.eft map help` | - | Get information about the maps that can be used with the `.eft map` command | 🌎 |
| `.eft time` | - | Get the current time in Tarkov | 🌎 |

> Note: `.` is the bot prefix to invoke the bot in production and `!` is often used for development
