from random import random

from errbot import BotPlugin, botcmd
from lib.common.errhelper import ErrHelper


class Devops(BotPlugin):
    """Devops plugin for Errbot"""

    @botcmd
    def devops(self, msg, args):
        """
        devops chat command for returning a visual of the DevOps life-cycle
        """
        ErrHelper().user(msg)

        if self.chaos():
            return "CHAOS"

        return "https://raw.githubusercontent.com/GrantBirki/errbot/ed6eddf583d39980fcfcff0a6cc60267b8db921c/demo/assets/devops.png"

    def chaos(self):
        """
        This does not bring joy
        """
        if random() > 0.5:
            return True
        else:
            return False
