import discord
from discord import channel

# Here we init the client and pass in a channel_id
class Client(discord.Client):
    def __init__(self, *, loop=None, **options):
        self.channel_id = options.pop("channel_id")
        super().__init__(loop=loop, **options)

    async def on_ready(self):
        print("ready")
        channel = client.get_channel(self.channel_id)
        member_ids = channel.voice_states.keys()
        print("members_ids:", list(member_ids))

        await self.close()


client = Client(channel_id=1234567890)  # pass in the channel id to get the members of
client.run("<token>")
