from random import choice, randint
from typing import Optional
from aiohttp import request
from functools import reduce
import json
import requests

from discord.ext.commands import Cog, command
from discord import Member, Embed

COG_ID = "log"

DEF_REGION = "NA"
DEF_SERVER = "Coeurl"
ERROR_COLOR = 0xA11616 # if character and/or logs not found
DATA_COLOR = 0x0FB3DB # outputting data for found character logs


def update_encounters(encounters, encounterData):
    encID = encounterData['encounterID']
    report = encounterData['reportID']
    enc = encounterData['encounterName']
    job = encounterData['spec']
    dps = encounterData['total']
    perc = encounterData['percentile']
    rank = encounterData['rank']
    outOf = encounterData['outOf']
    time = encounterData['duration'] #returns in milliseconds
    diff = encounterData['difficulty'] # ignore if 100, savage is 101
 
    newResult = {enc: {'job': job, 'rank': rank, 'outOf': outOf, 'percentile': perc, 'dps': dps, 'time': time, 'id': encID, 'report': report}}

    #if diff == 100, if enc already exists in encounter check for percentile, if not
    if (diff == 101):
        if enc in encounters:
            # if new dps higher than previous, update encounter to those logs
            if dps > encounters[enc]['dps']:
                return encounters|newResult
            # if no change in dps, then no change to encounter list 
            else: 
                return encounters
        #if key not existent in encounters, add it encounters
        else: 
            return encounters|newResult
    #no change because normal mode log
    else: 
        return encounters
    

# returns all top rDPS parses
def log_parses(data):
    bossNum = len(data)
    logDict = {}

    return reduce(update_encounters, data, {})

# rearraged and formats data in embed to be sent on discord
def output(data):
    bossNum = len(data)
    instance = {}
    log = list(data.keys())
    for i in range(0, bossNum):
        instance[i] = len(data[log[i]])
    embed = Embed(title="FF Logs - Combat Analysis", colour=DATA_COLOR)

    for i in range(0, bossNum):
        bossName = log[i]
        
        job = data[bossName]['job']
        rank = data[bossName]['rank']
        totalParses = data[bossName]['outOf']
        percentile = int(data[bossName]['percentile'])
        dps = int(data[bossName]['dps'])
        reportID = data[bossName]['report']
        
        #time returns in ms, divide by 1k for s
        time = int(data[bossName]['time'])/1000 
        minutes = int(time/60)
        seconds = int(time % 60)
        if (seconds < 10):
            seconds = "0" + str(seconds)

        embed.add_field(name = bossName, 
                        value = f"{job} **[**{rank}/{totalParses}**]** **[**Per: {percentile}**]** **[**[DPS: {dps}](https://www.fflogs.com/reports/{reportID})**]** **[**Time: {minutes}:{seconds}**]**\n",
                        inline = False)
    return(embed)

def get_data(firstName, lastName, server, region):
    with open("lib/cogs/logtoken.0", "r", encoding="utf-8") as tf:
        FFLOGS_TOKEN = tf.read()
    URL= f"https://www.fflogs.com:443/v1/rankings/character/{firstName}%20{lastName}/{server}/{region}?metric=rdps&api_key={FFLOGS_TOKEN}"
    data = requests.get(URL)
    jsonData = json.loads(data.text)

    status = data.status_code
    if status != 200:
        result = Embed(title = f"ERROR {status}", colour=ERROR_COLOR)
        result.set_author(name=f"{firstName} {lastName}, {server}", icon_url="https://i.imgur.com/nJ4Yq4R.png")
        result.set_footer(text="Character is not found. Please make sure character name, server, and region (if not NA) are given correctly. If character exists and is unable to be found, the account owner may have hidden parses or no parses.")
        return(result)
    else:
        log = log_parses(jsonData)
        pcname = jsonData[0]['characterName']
        result = output(log)
        result.set_author(name=f"{pcname}, {server}", icon_url="https://i.imgur.com/nJ4Yq4R.png")
        result.set_footer(text=f"Results are based on the log with the best RDPS and do not reflect the user's profile entirely. For best time and historical percentile, please check the user's profile.")
        return(result)
        
class Log(Cog):
    def __init__(self, bot):
        self.bot=bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COG_ID)

    @command(name="characterlog", aliases=["charlog","clog"], help="Retrieve current savage tier FFLogs for a character. Server and region defaulted to 'Coeurl' and 'NA', respectively. Please enter in the server and/or region to look up characters outside default server or region.", brief="Retrive current savage tier FFLogs for a character.")
    async def get_rankings(self, ctx, firstName, lastName, server: Optional[str] = DEF_SERVER, region: Optional[str] = DEF_REGION):
        result = get_data(firstName, lastName, server, region)
        await ctx.send(embed = result)

def setup(bot):
    bot.add_cog(Log(bot))
