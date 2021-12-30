import json
import time
from threading import Thread
import websocket
import requests
import os

TOKEN = os.environ["CHAT_SERVICE_TOKEN"]


class DiscordWebSocket:
    """
    This class is not used currently but it is here should you choose to work with it
    """
    def __init__(self):
        self.websocket = websocket
        self.interval = None
        self.sequence = None
        self.session_id = None
        self.default_intent = 32460
        self.dispatch = 0
        self.heartbeat_op = 1
        self.identify = 2
        self.status_update = 3
        self.voice_update = 4
        self.resume = 6
        self.reconnect = 7
        self.request_members = 8
        self.invalid_session = 9
        self.hello_op = 10
        self.heartbeat_ack = 11
        self.closed = False  # call self.close = True to close the websocket
        self.auth = {
            "token": TOKEN,
            "properties": {"$os": "linux", "$browser": "python", "$device": "errbot"},
            "intents": self.default_intent,
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
        self.websocket = websocket.create_connection(
            f"{gateway['url']}/?v=9&encoding=json"
        )

        # Run the gateway hello
        self.hello()
        if self.interval is None:
            return

        # Start the heartbeat thread
        heartbeat_thread = Thread(target=self.heartbeat)
        heartbeat_thread.start()

        # Return the heartbeat thread object (useful if you need to force close the thread)
        return heartbeat_thread

    def send(self, opcode, data):
        """
        Send a payload to the Discord websocket gateway
        :param opcode: The opcode to send (int)
        :param payload: The payload to send (dict)
        """
        payload = self.create_payload(opcode, data)
        print(">", payload)
        self.websocket.send(payload)

    def __join_voice_websocket(self, guild_id, channel_id):
        """
        Private method to join a voice channel
        :param guild_id: The guild ID to join
        :param channel_id: The voice channel ID to join
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "self_mute": False,
            "self_deaf": False,
        }
        self.send(4, data)

    def heartbeat(self):
        """
        Method to continuously send heartbeats to the Discord gateway
        Only stops if the self.close() is called
        """
        # Set the start time to now
        start_time = time.time()
        while self.interval is not None:
            # If self.closed is True we break the heartbeat loop
            if self.closed:
                break

            # Use rapid sleeps to rip through the loop checking for self.closed
            time.sleep(0.25)
            end_time = time.time()

            # If the elapsed time is greater than the interval we send a heartbeat
            if (end_time - start_time) > self.interval:
                self.send(self.heartbeat_op, self.sequence)
                start_time = time.time()
                continue

    def hello(self):
        """
        Send the gateway hello
        """
        self.send(self.identify, self.auth)
        ret = self.websocket.recv()
        print(f"hello < {ret}")

        data = json.loads(ret)
        opcode = data["op"]
        if opcode != 10:
            print("Unexpected reply")
            print(ret)
            return
        self.interval = (data["d"]["heartbeat_interval"] - 2000) / 1000

    def create_payload(self, opcode: int, data: dict) -> str:
        payload = {"op": opcode, "d": data}
        return json.dumps(payload)

    def receive(self):
        print("Entering receive")
        while not self.closed:
            try:
                message = self.websocket.recv()
                if message is None or message.strip() == "":
                    continue
                print("<", message)
                data = json.loads(message)
                if data["op"] == self.dispatch:
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
