from errbot import BotPlugin, botcmd

class Template(BotPlugin): # Change me!
    """Template plugin for Errbot"""

    @botcmd
    def template(self, msg, args): # Change me! (function name)
        """
        The most basic example of a chatbot command/function
        Tip: The name of the function above is literally how you invoke the chatop: .template
        Pro Tip: "_" in function names render as spaces so you can do 'def send_template(...)' -> .send template
        """

        # Implement code here

        # Return a message / output below
        return 'Hello world, I am a template!'

    