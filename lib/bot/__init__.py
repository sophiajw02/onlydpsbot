from datetime import datetime
from glob import glob
from asyncio import sleep
import os
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord import Embed, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context, when_mentioned_or
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, 
                                    CommandOnCooldown)

from ..db import db

load_dotenv()

PREFIX = "!"
COGS = [os.path.split(path)[1][:-3] for path in glob("./lib/cogs/*.py")]
# COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
    return when_mentioned_or(PREFIX)(bot, message)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"     {cog} cog ready")

    def all_ready(self):
        return all([getattr(self,cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        OWNER_ID=os.getenv("OWNER_ID")
        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_ID) #intents=Intents.all()

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"    {cog} cog loaded")
        print("- set up complete!")

    def run(self, version):
        self.VERSION = version
        print("running setup. . .")
        self.setup()
        self.TOKEN = os.getenv("BOT_TOKEN")
        print("running bot. . .")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        if ctx.command is not None and ctx.guild is not None:
            if not self.ready:
                await ctx.send("Healbot is charging up. Please wait to use commands.")
            else:
                await self.invoke(ctx)

    async def rules_reminder(self):
        await self.stdout.send("Please follow the rules!")

    async def on_command(ctx, error):
        print("-- Bot connected!")

    async def on_disconnect():
        print("-- Bot disconnected!")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send(":x: Incorrect command")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(":x: One or more required arguments are missing!")
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f":x: Wait ``{exc.retry_after:,.0f} seconds`` to use this command again.")
        elif hasattr(exc, "original"):
            if isinstance(exc.original, Forbidden):
                await ctx.send(":x: I do not have the permissions to perform that command.")
            else:
                raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            GUILD=os.getenv("GUILD_ID")
            CHANNEL=os.getenv("CHANNEL_ID")

            self.guild = self.get_guild(int(GUILD))
            self.stdout = self.get_channel(int(CHANNEL)) 
            
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=1, minute=0, second=0))
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            embed = Embed(title="Feel... Hear... Think...", 
                          description=f"Always ready to help the Warrior of Light, kupo!", 
                          colour=0x16C77D)
            await self.stdout.send(embed=embed, delete_after=5)
            self.ready = True
            print("-- bot ready")

        else:
            print("-- bot reconnected")

    async def on_message(self,message):
        if not message.author.bot: 
            await self.process_commands(message)

bot = Bot()
        
        