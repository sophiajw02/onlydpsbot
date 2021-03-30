from random import choice, randint
from typing import Optional
from functools import reduce

import logging
import json
import requests

import asyncio
import aiohttp
import pyxivapi
from pyxivapi.models import Filter,Sort

from discord.ext.commands import Cog, command
from discord import Member, Embed, File

COG_ID = "xivsearch"

ERROR_COLOR = 0xA11616
DATA_COLOR = 0x0C9C84

def get_token():
    with open("lib/cogs/privatekey.0", "r", encoding="utf-8") as tf:
        PRIVATE_KEY = tf.read()
    return(PRIVATE_KEY)

class XIVSearch(Cog):
    def __init__(self, bot):
        self.bot=bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COG_ID)

    @command(name="itemsearch", aliases=["isearch"], help="Search for an item on the Lodestone.", brief="Search up an item.")
    async def item_search(self, ctx, *, search):
        SESSION = aiohttp.ClientSession()
        PRIVATE_KEY=get_token()
        CLIENT = pyxivapi.client.XIVAPIClient(api_key=PRIVATE_KEY, session=SESSION)
        results = await CLIENT.index_search(
            name=f"{search}",
            indexes=["Item"],
            columns=["Name", 
            "Icon",
            "Description",
            "ItemKind.Name",
            "ItemUICategory.Name"] 
            )
        for each in results['Results']:
            embed = Embed(title=each['Name'], description=f"**{each['ItemUICategory']['Name']}**\n{each['Description']}", colour=DATA_COLOR)
            embed.set_thumbnail(url=f"https://xivapi.com/{each['Icon']}")
            await ctx.send(file=file, embed = embed)

    @command(name="charactersearch", aliases=["csearch", "charsearch"], help="Search for a character on the Lodestone.", brief="Search up a PC.")
    async def character_search(self, ctx, firstName, lastName, server):
        SESSION = aiohttp.ClientSession()
        PRIVATE_KEY=get_token()
        CLIENT = pyxivapi.client.XIVAPIClient(api_key=PRIVATE_KEY, session=SESSION)
        results = await CLIENT.character_search(
            world=f"{server}",
            forename=f"{firstName}",
            surname=f"{lastName}"
            )
        print(results)
        for each in results['Results']:
            characterResults = await CLIENT.character_by_id(
                lodestone_id=f"{each['ID']}",
                extended=True
            )
            embed = Embed(title=f"{characterResults['Character']['Name']}, {characterResults['Character']['Title']['Name']}", description=f"{characterResults['Character']['DC']}, {characterResults['Character']['Server']}", colour=DATA_COLOR)
            embed.add_field(name="Race/Clan",value=f"{characterResults['Character']['Race']['Name']}/{characterResults['Character']['Tribe']['Name']}")
            embed.add_field(name="Nameday", value=characterResults['Character']['Nameday'])
            embed.add_field(name="Guardian Deity", value=characterResults['Character']['GuardianDeity']['Name'])
            embed.add_field(name="Grand Company", value=characterResults['Character']['GrandCompany']['Company']['Name'])
            embed.add_field(name="GC Rank", value=characterResults['Character']['GrandCompany']['Rank']['Name'])
            embed.add_field(name="Free Company", value=characterResults['Character']['FreeCompanyName'])
            embed.add_field(name="Eureka Level",value=characterResults['Character']['ClassJobsElemental']['Level'])
            embed.add_field(name="Bozja Rank",value=characterResults['Character']['ClassJobsBozjan']['Level'])
            embed.add_field(name="Active Class", value=f"{characterResults['Character']['ActiveClassJob']['Job']['Abbreviation']}, Level {characterResults['Character']['ActiveClassJob']['Level']}")
            embed.set_thumbnail(url=characterResults['Character']['Avatar'])
            embed.set_image(url=characterResults['Character']['Portrait'])
            await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(XIVSearch(bot))
