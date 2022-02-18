from errbot import BotPlugin, botcmd
from lib.common.errhelper import ErrHelper


class Template(BotPlugin):  # Change me!
    """Template plugin for Errbot"""

    @botcmd
    def template(self, msg, args):  # Change me!
        """
        The most basic example of a chatbot command/function
        Tip: The name of the function above is literally how you invoke the chatop: .template
        Pro Tip: "_" in function names render as spaces so you can do 'def send_template(...)' -> .send template
        """
        ErrHelper().user(msg)

        # Implement code here

        # Return a message / output below
        return "Hello world, I am a template!"
