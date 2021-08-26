class Discord:
    def guild_id(self, msg):
        """
        Returns the guild_id as a an int
        """
        try:
            return msg.frm.room.__dict__['_guild_id'], None
        except AttributeError:
            return False, 'Please run this command in a Discord channel, not a DM'

    def fmt_guild_id(self, guild_raw):
        """
        Formats the guild_raw to a proper guild_id

        Mainly used for formatting when reading from the database
        """
        return int(guild_raw)

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

    def get_user_id(self, msg):
        """
        Gets the user's raw Discord ID and returns it
        The user ID is an integer
        Example: 12345678909876543
        """

        return msg.frm.__dict__['_user_id']
