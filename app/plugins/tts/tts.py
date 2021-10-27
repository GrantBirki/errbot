from errbot import BotPlugin, botcmd
import asyncio
import websockets
import json
import os

DEFAULT_INTENT = 32460

DISPATCH = 0
HEARTBEAT = 1
IDENTIFY = 2
STATUS_UPDATE = 3
VOICE_UPDATE = 4
RESUME = 6
RECONNECT = 7
REQUEST_MEMBERS = 8
INVALID_SESSION = 9
HELLO = 10
HEARTBEAT_ACK = 11

VOICE_CHANNEL = 873463331917299726
GUILD_ID = 873463331917299722

TOKEN = os.environ['CHAT_SERVICE_TOKEN']

class Tts(BotPlugin):
    """Tts plugin for Errbot"""

    @botcmd
    def tts(self, msg, args):
        """
        The most basic example of a chatbot command/function
        Tip: The name of the function above is literally how you invoke the chatop: .tts
        Pro Tip: "_" in function names render as spaces so you can do 'def send_tts(...)' -> .send tts
        """

        dws = DiscordWebSocket()
        dws.join_voice()

        # Return a message / output below
        return "test"

class DiscordWebSocket:
    def __init__(self):
        self.interval = None
        self.sequence = None
        self.session_id = None

        self.auth = {
            "token": TOKEN,
            "properties": {"$os": "linux", "$browser": "python", "$device": "errbot"},
            "intents": DEFAULT_INTENT,
            "presence": {
                "game": {"name": "testing", "type": 0},
                "status": "online",
                "afk": False,
            },
        }


    def join_voice(self):
        asyncio.run(self.main(self.join_voice_task(GUILD_ID, VOICE_CHANNEL)))

    async def main(self, task):
        async with websockets.connect(
            "wss://gateway.discord.gg/?v=9&encoding=json"
        ) as self.websocket:
            await self.hello()
            if self.interval is None:
                print("Hello failed, exiting")
                return

            await asyncio.gather(
                self.heartbeat(), self.receive(), task
            )


    async def receive(self):
        print("Entering receive")
        async for message in self.websocket:
            print("<", message)
            data = json.loads(message)
            if data["op"] == DISPATCH:
                self.sequence = int(data["s"])
                event_type = data["t"]
                if event_type == "READY":
                    self.session_id = data["d"]["session_id"]
                    print("Got session ID:", self.session_id)
                elif event_type == "MESSAGE_CREATE":
                    message = data["d"]["content"]
                    if message.startswith("!edit"):
                        print("Edit")
                        parts = message.split()
                        if len(parts) != 2:
                            print("Command error")
                        else:
                            id = parts[1]
                            print("id", id)

    async def send(self, opcode, payload):
        data = self.opcode(opcode, payload)
        print(">", data)
        await self.websocket.send(data)

    async def join_voice_task(self, guild_id, channel_id):

        payload = {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": False,
                "self_deaf": False,
            }
        await self.send(4, payload)

    async def heartbeat(self):
        print("Entering heartbeat")
        while self.interval is not None:
            print("Sending a heartbeat")
            await self.send(HEARTBEAT, self.sequence)
            await asyncio.sleep(self.interval)

    async def hello(self):
        await self.send(IDENTIFY, self.auth)
        print(f"hello > auth")

        ret = await self.websocket.recv()
        print(f"hello < {ret}")

        data = json.loads(ret)
        opcode = data["op"]
        if opcode != 10:
            print("Unexpected reply")
            print(ret)
            return
        self.interval = (data["d"]["heartbeat_interval"] - 2000) / 1000
        print("interval:", self.interval)

    def opcode(self, opcode: int, payload) -> str:
        data = {"op": opcode, "d": payload}
        return json.dumps(data)
