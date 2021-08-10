from errbot import BotPlugin, botcmd

class League(BotPlugin):
    """League plugin for Errbot"""

    @botcmd
    def last_match(self, msg, args):
        """Get the last match for a user (LoL)"""

        # Add code here

        # Return a message / output below
        return 'Hello, World!'