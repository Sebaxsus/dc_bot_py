import discord
from discord.ext import commands
from discord import app_commands
#Actualiza comando a un servidor especifico con la id del servidor

MY_GUILD = discord.Object(id=401031749758353418)

class Servidor(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
#
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = Servidor(intents=intents)