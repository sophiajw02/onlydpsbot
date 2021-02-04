from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, command
from discord import Embed, File
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

PREFIX = "!"
OWNER_IDS = [524668365349060610]

class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=PREFIX, 
            owner_ids=OWNER_IDS) #intents=Intents.all()

    def run(self, version):
        self.VERSION = version

        with open("lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_command():
        print("Bot connected and online!")

    async def on_disconnect():
        print("Bot disconnected!")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Incorrect command")
        channel = self.get_channel(805839915463213107)
        await channel.send("Error")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass
        elif hasattr(exc, "original"):
            raise exc.original
        else:
            raise exc

    #embed message on bot start up
    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(758769744362340373)
            print("bot ready")

            channel = self.get_channel(805839915463213107)
            #await channel.send("Healbot online and ready!")

            embed = Embed(title="Healbot Online", description="Succor is ready to nyoom", colour=0x16C77D, timestamp=datetime.utcnow())
            fields = [("Name", "Value", True),
                      ("Another", "Wow Next", True),
                      ("A final one", "Last", False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            #embed.set_author(name="Soap", icon_url=self.guild.icon_url)
            #embed.set_footer(text="This is a foooooooooterrrr")
            await channel.send(embed=embed)

            #await channel.send(file=File("data/images/glare.jpg")) #bot sends files in channel

        else:
            print("bot reconnected")

    async def on_message(self,message):
        pass

    self.command()
    async def test(ctx, arg):
        await send(arg)

bot = Bot()
        
        