from datetime import datetime
from glob import glob
from asyncio import sleep

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord import Embed, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context, when_mentioned_or
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, 
                                    CommandOnCooldown)

from ..db import db

PREFIX = "!"
OWNER_IDS = [524668365349060610] 
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
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
        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS) #intents=Intents.all()

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"    {cog} cog loaded")
        print("- set up complete!")

    def run(self, version):
        self.VERSION = version
        print("running setup. . .")
        self.setup()
        with open("lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
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
        # else:
        #     await self.stdout.send("Error")
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
            self.guild = self.get_guild(758769744362340373)
            self.stdout = self.get_channel(758769744362340376) 
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=1, minute=0, second=0))
            self.scheduler.start()
           
            # embed = Embed(title="Healbot Online", description="Succor is ready to nyoom", colour=0x16C77D, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True),
            #          ("Another", "Wow Next", True),
            #          ("A final one", "Last", False)]
            # for name, value, inline in fields:
            #    embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Only DPS Bot", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is a foooooooooterrrr")
            #await channel.send(embed=embed)
            #await channel.send(file=File("data/images/glare.jpg")) #bot sends files in channel

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
        
        