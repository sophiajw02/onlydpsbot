from discord.ext.commands import Cog, command
from discord import Member, Embed

COG_ID = "greeting"

class Greeting(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COG_ID)

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO user (UserID) VALUES (?)", member.id)
        await self.bot.get_channel(758769744362340376).send(f"Welcome to **{member.guild.name}**, {member.mention}!")
        # assign role automatically upon joining
        # await member.add_roles(*(member.guild_get_role(id_) for id_ in (ID1, ID2, ID3)))

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM user WHERE UserID = ?", member.id)
        await self.bot.get_channel(758769744362340376).send(f"{member.display_name} has left the server.") #general: 758769744362340376


def setup(bot):
    bot.add_cog(Greeting(bot))