import asyncio
import discord


class DiscordCustom:
    def __init__(self, bot):
        self.bot = bot

    def play_audio_file(self, channel, file):

        asyncio.run_coroutine_threadsafe(
            self.__play_audio_file_runner(channel, file),
            loop=self.bot.client.loop,
        )

    async def __play_audio_file_runner(self, channel, file):

        channel = self.bot.client.get_channel(channel)
        vc = await channel.connect()
        await vc.play(discord.FFmpegPCMAudio(file))
        await channel.disconnect()
