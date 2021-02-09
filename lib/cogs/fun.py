from random import choice, randint
from typing import Optional
from discord.ext.commands import Cog, command, BadArgument
from discord import Member

class Fun(Cog):
    def __init__(self, bot):
        self.bot=bot

    @command(name="hello", aliases=["hi","welcome"]) #name="insertname", aliases=["cmd","ins","more"], hidden=True
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Sup'))} {ctx.author.mention}!")

    @command(name="dice", aliases=["roll"])
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d")) #input command would be like 5d5 (roll a 6 die 5 times)
        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.send(" + ".join(str(r) for r in rolls) + f" = {sum(rolls)}")
        else:
            await ctx.send("too many dice to be rolled, try a lower number")

    @command(name="hug", aliases=["love","comfort"])
    async def give_hug(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
        #await ctx.message.delete()
            #delete the message the user sent
        await ctx.send(f"{ctx.author.display_name} hugs {member.mention} for {reason}!")

    @give_hug.error
    async def give_hug_error(self,ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("that member cannot be found")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")

def setup(bot):
    bot.add_cog(Fun(bot))
