from errbot import BotPlugin, botcmd
from time import sleep

class HelloWorld(BotPlugin):
    """Example 'Hello, world!' plugin for Errbot"""

    @botcmd
    def hello(self, msg, args):
        """Say hello to the world"""

        # Slack
        # self.send_card(
        #     title='Hey!',
        #     body='body',
        #     # image='https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png',
        #     # link='http://www.google.com',
        #     color='red',
        #     in_reply_to=msg
        # )

        return "hello world!"

    @botcmd
    def longcompute(self, msg, args):
        """Slowly return responses over time with Python Yield"""

        # Slack
        # yield self.send_card(
        #     title='Sleep',
        #     color='red',
        #     in_reply_to=msg
        # )

        yield 'Sleep'

        sleep(5)
        
        # Slack
        # yield self.send_card(
        #     title='Wake',
        #     color='green',
        #     in_reply_to=msg
        # )

        yield 'Wake'

    @botcmd
    def yield_test(self, msg, args):
        """Returns messages in a yield"""

        messages = ["hey1", "hey2", "hey3"]

        # Slack
        # for hey in messages:
        #     yield self.send_card(
        #     title="Incoming Hey!",
        #     color='blue',
        #     in_reply_to=msg
        # )

        # Standard
        for hey in messages:
            yield hey

    @botcmd
    def usertest(self, msg, args):
        """Send a message directly to a user"""

        # Slack
        # self.send_card(
        #     title='Sending private message',
        #     body=f'Recipient {msg.frm.person}',
        #     color='green',
        #     in_reply_to=msg
        # )

        yield f"Sending private message to: {msg.frm.person}"

        self.send(
            self.build_identifier(msg.frm.person),
            "Boo! Bet you weren't expecting me, were you?",
        )
