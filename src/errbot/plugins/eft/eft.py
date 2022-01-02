from errbot import BotPlugin, botcmd


class Eft(BotPlugin):  
    """Eft plugin for Errbot"""

    @botcmd
    def eft(self, msg, args):  
        """
        The most basic example of a chatbot command/function
        Tip: The name of the function above is literally how you invoke the chatop: .eft
        Pro Tip: "_" in function names render as spaces so you can do 'def send_eft(...)' -> .send eft
        """

        # Implement code here

        # Return a message / output below
        return "Hello world, I am a eft!"
