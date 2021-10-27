from errbot import BotPlugin, botcmd
import websocket
import requests
from threading import Thread
import json
import os
import time

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
        dws.main()

        # Return a message / output below
        return "test"

class DiscordWebSocket:
    def __init__(self):
        self.interval = None
        self.sequence = None
        self.session_id = None
        self.action_complete = False
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
        self.run(self.join_voice_websocket(GUILD_ID, VOICE_CHANNEL))


    def run(self, task):
        self.main(task)

    def run_tasks(self):
        self.join_voice_websocket(GUILD_ID, VOICE_CHANNEL)


    def main(self): #task):
        headers = {"Authorization": "Bot " + TOKEN}
        gateway = requests.get(
            "https://discord.com/api/gateway/bot", headers=headers
        ).json()
        
        self.websocket = websocket.create_connection(f"{gateway['url']}/?v=9&encoding=json")
        print("Connected")

        self.hello()
        if self.interval is None:
            print("Hello failed, exiting")
            return

        heartbeat_thread = Thread(target=self.heartbeat)
        task_thread = Thread(target=self.run_tasks)
        
        heartbeat_thread.start()
        task_thread.start()

    def receive(self):
        print("Entering receive")
        while not self.action_complete:
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

    def send(self, opcode, payload):
        data = self.opcode(opcode, payload)
        print(">", data)
        self.websocket.send(data)

    def join_voice_websocket(self, guild_id, channel_id):
        print("Entering join_voice_websocket")
        payload = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "self_mute": False,
            "self_deaf": False,
        }
        self.send(4, payload)
        self.action_complete = True

    def heartbeat(self):
        print("Entering heartbeat")
        while self.interval is not None and not self.action_complete:
            print("Sending a heartbeat")
            self.send(HEARTBEAT, self.sequence)
            time.sleep(self.interval)

    def hello(self):
        self.send(IDENTIFY, self.auth)
        print(f"hello > auth")

        ret = self.websocket.recv()
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
