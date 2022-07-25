import os
import time
import uuid

from errbot import BotPlugin, botcmd
from lib.chat.chatutils import ChatUtils
from lib.chat.discord_custom import DiscordCustom
from lib.common.errhelper import ErrHelper

import qrcode

chatutils = ChatUtils()

IMAGE_DIR = "plugins/qrcode/images"

qr = qrcode.QRCode(
    version=None,
    box_size=30,
    border=1
)

class Qrcode(BotPlugin):  
    """Qrcode plugin for Errbot"""

    @botcmd
    def qrcode(self, msg, args):  
        """
        The most basic example of a chatbot command/function
        Tip: The name of the function above is literally how you invoke the chatop: .qrcode
        Pro Tip: "_" in function names render as spaces so you can do 'def send_qrcode(...)' -> .send qrcode
        """
        ErrHelper().user(msg)

        # Check to ensure the user provided some form of arguments
        if len(args) == 0:
            return "⚠ No arguments provided! Please provide some text to encode as a QR code"

        # Construct the filename
        filename = f"{IMAGE_DIR}/{uuid.uuid4()}.png"

        # Generate the qrcode and save it
        qr.add_data(args)
        img = qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        
        # Init the DiscordCustom object
        dc = DiscordCustom(self._bot)

        # Get the channel ID from the message to send the file to
        channel_id = chatutils.channel_id(msg)

        # Send the file
        dc.send_file(channel_id, filename)

        # Delete the file
        time.sleep(5)
        if os.path.isfile(filename):
            os.remove(filename)
