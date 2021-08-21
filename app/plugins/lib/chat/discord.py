class Discord:
    def guild_id(self, msg):
        try:
            return msg.frm.room.__dict__['_guild_id'], None
        except AttributeError:
            return False, 'Please run this command in a Discord channel, not a DM'

    def handle(self, msg):
        discord_handle = msg.frm.person.split('@')[0]
        return discord_handle