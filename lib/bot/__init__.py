from datetime import datetime
from glob import glob
from asyncio import sleep

from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument)
from discord.ext.commands import Context
from discord.errors import HTTPException, Forbidden
from discord import Embed, File
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..db import db

PREFIX = "!"
OWNER_IDS = [524668365349060610]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument, MissingRequiredArgument)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

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
        super().__init__(
            command_prefix=PREFIX, 
            owner_ids=OWNER_IDS) #intents=Intents.all()

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("set up complete")

    def run(self, version):
        self.VERSION = version

        print("running setup")
        self.setup()

        with open("lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    # async def process_commands(self, message):
    #     ctx = await self.get_context(message, cls=Context)

    #     if ctx.command is not None and ctx.guild is not None:
    #         if any([isinstance(exc,error) for error in IGNORE_EXCEPTIONS]):
    #             pass
    #         elif isinstance(exc, BadArgument):
    #             pass
    #         elif isinstance(exc, MissingRequiredArgument):
    #             await ctx.send("one or more arguments missing")
    #         elif isinstance(exc.original, HTPPException):
    #             await ctx.send("unble to send message")
    #         elif isinstance(exc.original, Forbidden):
    #             await ctx.send("no permission to complete command")
    #         else:
    #             await exc.original

    async def rules_reminder(self):
        await self.stdout.send("Please follow the rules!")

    async def on_command(ctx, error):
        print("Bot connected and online!")

    async def on_disconnect():
        print("Bot disconnected!")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Incorrect command")
        await self.stdout.send("Error")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass
        else:
            raise exc

    #embed message on bot start up
    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(758769744362340373)
            self.stdout = self.get_channel(805839915463213107)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()
           
            #embed = Embed(title="Healbot Online", description="Succor is ready to nyoom", colour=0x16C77D, timestamp=datetime.utcnow())
            #fields = [("Name", "Value", True),
            #          ("Another", "Wow Next", True),
            #          ("A final one", "Last", False)]
            #for name, value, inline in fields:
            #    embed.add_field(name=name, value=value, inline=inline)
            #embed.set_author(name="Soap", icon_url=self.guild.icon_url)
            #embed.set_footer(text="This is a foooooooooterrrr")
            #await channel.send(embed=embed)
            #await channel.send(file=File("data/images/glare.jpg")) #bot sends files in channel

            while not self.cogs_ready.all_ready():
                await sleep(0.5)
            
            await self.stdout.send("Healbot online and ready!")
            self.ready = True
            print("bot ready")


        else:
            print("bot reconnected")

    async def on_message(self,message):
        if not message.author.bot: #ignore messages from bots
            await self.process_commands(message)

bot = Bot()
        
        