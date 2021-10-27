import json
import time
from threading import Thread
import websocket
import requests

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

from token_file import TOKEN


class DiscordWebSocket:
    def __init__(self):
        self.websocket = websocket
        self.interval = None
        self.sequence = None
        self.session_id = None
        self.closed = False # call self.close = True to close the websocket
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
        self.main()

    def close(self):
        self.closed = True
        self.websocket.close()

    def join_voice(self, guild_id: int, channel_id: int):
        """
        Public method for joining a Discord voice channel
        :param guild_id: The guild ID where the channel resides (int)
        :param channel_id: The voice channel ID to join (int)
        """
        self.__join_voice_websocket(guild_id, channel_id)

    def main(self):
        """
        Creates a websocket and connects to the Discord gateway. Heart beats start automatically.
        """
        headers = {"Authorization": "Bot " + TOKEN}
        # Get the gateway URL
        gateway = requests.get(
            "https://discord.com/api/gateway/bot", headers=headers
        ).json()
        
        # Connect to the gateway
        self.websocket = websocket.create_connection(f"{gateway['url']}/?v=9&encoding=json")

        # Run the gateway hello
        self.hello()
        if self.interval is None:
            return

        # Start the heartbeat thread
        heartbeat_thread = Thread(target=self.heartbeat)
        heartbeat_thread.start()

        # Return the heartbeat thread object (useful if you need to force close the thread)
        return heartbeat_thread

    def send(self, opcode, payload):
        """
        Send a payload to the Discord websocket gateway
        :param opcode: The opcode to send (int)
        :param payload: The payload to send (dict)
        """
        data = self.opcode(opcode, payload)
        print(">", data)
        self.websocket.send(data)

    def __join_voice_websocket(self, guild_id, channel_id):
        """
        Private method to join a voice channel
        :param guild_id: The guild ID to join
        :param channel_id: The voice channel ID to join
        """
        payload = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "self_mute": False,
            "self_deaf": False,
        }
        self.send(4, payload)

    def heartbeat(self):
        """
        Method to continuously send heartbeats to the Discord gateway
        Only stops if the self.close() is called
        """
        while self.interval is not None and not self.closed:
            self.send(HEARTBEAT, self.sequence)
            time.sleep(self.interval)

    def hello(self):
        """
        Send the gateway hello
        """
        self.send(IDENTIFY, self.auth)
        ret = self.websocket.recv()
        print(f"hello < {ret}")

        data = json.loads(ret)
        opcode = data["op"]
        if opcode != 10:
            print("Unexpected reply")
            print(ret)
            return
        self.interval = (data["d"]["heartbeat_interval"] - 2000) / 1000

    def opcode(self, opcode: int, payload: dict) -> str:
        data = {"op": opcode, "d": payload}
        return json.dumps(data)

    def receive(self):
        print("Entering receive")
        while not self.closed:
            try:
                message = self.websocket.recv()
                if message is None or message.strip() == "":
                    continue
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
            except:
                continue


bot = DiscordWebSocket()

bot.join_voice(GUILD_ID, VOICE_CHANNEL)
print("Joined voice")
time.sleep(5)
bot.close()
print("Closed")
