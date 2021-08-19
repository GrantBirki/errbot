class Discord:
    def guild_id(self, msg):
        return msg.frm.room.__dict__['_guild_id']

    def handle(self, msg):
        discord_handle = msg.frm.person.split('@')[0]
        return discord_handle