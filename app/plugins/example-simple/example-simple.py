from errbot import BotPlugin, botcmd

class Example(BotPlugin):
    """Example plugin for Errbot / chatbot"""

    @botcmd
    def example(self, msg, args):
        """The most basic example of a chatbot command/function"""

        # Add code here

        # Return a message / output below
        return 'Hello, World!'