from random import choice, randint
from typing import Optional
from aiohttp import request
from functools import reduce
import json
import requests

from discord.ext.commands import Cog, command
from discord import Member, Embed

COG_ID = "xivsearch"

class XIVSearch(Cog):
    def __init__(self, bot):
        self.bot=bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COG_ID)


def setup(bot):
    bot.add_cog(XIVSearch(bot))
