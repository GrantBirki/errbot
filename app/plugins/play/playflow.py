from errbot import botflow, FlowRoot, BotFlow

class PlayFlow(BotFlow):
    """PlayFlow for the .play command"""

    @botflow
    def play_flow(self, flow: FlowRoot):
        """
        Used for the .stop command to stop the entire .play queue
        """
        # Start the follow automatically if the .stop command is used
        first = flow.connect('stop', auto_trigger=True)
        # Get confirmation from the user for this command
        second = first.connect('confirm')
        # Make the user run the stop command again and check the confirmation via the ctx dict
        second.connect('stop')
