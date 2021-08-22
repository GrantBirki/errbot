class Discord:
    def guild_id(self, msg):
        try:
            return msg.frm.room.__dict__['_guild_id'], None
        except AttributeError:
            return False, 'Please run this command in a Discord channel, not a DM'

    def handle(self, msg):
        """
        Gets the Discord handle of a user
        This does not support mentions but is useful for getting the handle of a user

        Example: Birki#0001@bots -> Birki#0001
        Use mention_user to get the ID to mention a user
        """
        discord_handle = msg.frm.person.split('@')[0]
        return discord_handle

    def mention_user(self, msg):
        """
        Gets the user's mention_id which can be used to directly mention a Discord user in chat
        Returns the the 'mention_id' with proper formatting for a mention
        """
        return f"<@{msg.frm.__dict__['_user_id']}>"
