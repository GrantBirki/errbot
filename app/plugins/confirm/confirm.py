from errbot import BotPlugin, botcmd


class Confirm(BotPlugin):  
    """Confirm plugin for Errbot"""

    @botcmd
    def confirm(self, msg, args):
        """
        Confirm a command
        Usage: .confirm yes or .confirm no
        Note: This command is mainly a helper for the flow plugin.
        """

        if "yes" in args.lower():
            msg.ctx['confirmed'] = True
            return "✅ Confirmed"
        else:
            msg.ctx['confirmed'] = False
            return "❌ Not Confirmed"
