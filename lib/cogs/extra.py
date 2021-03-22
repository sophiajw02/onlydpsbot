from random import choice, randint
from typing import Optional
from aiohttp import request

from discord.ext.commands import Cog, BadArgument, command, cooldown, BucketType, has_permissions, bot_has_permissions
from discord import Member, Embed

COG_ID = "extra"

class Extra(Cog):
    def __init__(self, bot):
        self.bot=bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COG_ID)

    # @command(name="hello", aliases=["hi","welcome"]) #name="insertname", aliases=["cmd","ins","more"], hidden=True
    # async def say_hello(self, ctx):
    #     await ctx.send(f"{choice(('Hello', 'Hi', 'Sup'))} {ctx.author.mention}!")

    @command(name="dice", aliases=["roll"], help="Roll a x sided die y amount of times. Ex: 2d5.", brief="Roll a x sided die y amount of times. Ex: 2d5.")
    @cooldown(1, 10, BucketType.user) #times before cd triggered, cd in sec, type of cd (user, member, server based)
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d")) #input command would be like 5d5 (roll a 6 die 5 times)
        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.send(" + ".join(str(r) for r in rolls) + f" = **{sum(rolls)}**")
        else:
            await ctx.send("Too many dice. Try again with a lower number!")

    @command(name="clear", help="Delete up to 100 messages from the channel.", brief="Delete messages.")
    @cooldown(1, 10, BucketType.user)
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, limit: Optional[int] = 1):
        if 0 < limit < 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit)
                await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)
        else:
            await ctx.send("Limit provided is not within acceptable bounds. Please retry.", delete_after=5)

    # @command(name="hug", aliases=["love","comfort"])
    # @cooldown(1, 10, BucketType.user)
    # async def give_hug(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
    #     #await ctx.message.delete()
    #         #delete the message the user sent
    #     await ctx.send(f"{ctx.author.display_name} hugs {member.mention} for {reason}!")

    # @give_hug.error
    # async def give_hug_error(self,ctx, exc):
    #     if isinstance(exc, BadArgument):
    #         await ctx.send("Please retry. That member cannot be found.")


def setup(bot):
    bot.add_cog(Extra(bot))
