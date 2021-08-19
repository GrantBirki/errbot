from errbot import BotPlugin, botcmd
from time import sleep

class Example(BotPlugin):
    """Example 'Hello, world!' plugin for Errbot"""

    @botcmd
    def example(self, msg, args):
        """The most basic example of a chatbot command/function"""

        # Add code here

        # Return a message / output below
        return 'Hello, World!'

    @botcmd
    def show_args(self, msg, args):
        # How the heck do I parse args?? -> https://errbot.readthedocs.io/en/latest/user_guide/plugin_development/botcommands.html
        return f'{type(args)} | args: {args}'

    @botcmd
    def show_msg(self, msg, args):
        # Displays msg attributes

        yield f"• `msg.frm`: {msg.frm}"
        yield f"• `msg.frm.__dict__`: {msg.frm.__dict__}"
        yield f'• Type of msg: {type(msg)} | `msg.__dict__`: {msg.__dict__}'

        try:
            yield f"__Checking Room / Channel info from `msg`__"
            yield f"• `msg.frm.room`: {msg.frm.room}"
            yield f"• `msg.frm.room.__dict__`: {msg.frm.room.__dict__}"
            yield f"• `guild_id`: {msg.frm.room.__dict__['_guild_id']}"
            #yield f"• `occupants`: {msg.frm.room.occupants}" # noisy
            yield f"• `msg.frm.room.name`: {msg.frm.room.name}"
            yield f"• `msg.frm.room.id`: {msg.frm.room.id}" # same as _channel_id
            yield "Room checks passed"
        except:
            yield "Room checks failed. Are you in a room / channel?"

        yield f"__Checking Person info from `msg`__"
        yield f"• `msg.frm.person`: {msg.frm.person}"
        yield "Person checks passed"   

        yield f'Done! 🎉'

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
