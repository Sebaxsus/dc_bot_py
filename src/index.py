import discord
from discord.ext import commands
import os, sys, dotenv, pathlib


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()

sys.path.append(str(pathlib.Path(__file__).parent.parent / "Dev2025/modules"))

DOTENV_PATH = pathlib.Path(__file__).parent / '.env'

dotenv.load_dotenv(DOTENV_PATH)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

token_bot = DISCORD_TOKEN

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Inicializando como {client.user}')

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    
    if message.content.startswith('yo'):
        await message.channel.send('Sapa ', mention_author=True)

@client.event
async def on_message(message):
    if message.content.startswith('!canal'):
        await message.channel.send(f"es puto")

client.run(token_bot)

#Configuro el bot con 'commands.Bot()'  / command_prefix define con que caracter el bot va a responder

#elBulloso = commands.Bot(command_prefix='!', description="Intento de bot con discord.py")

#@elBulloso.command()
#Con ping el servidor me respondera, se usa para verificar la conexion del bot al servidor
#async def ping(ctx):
#    await ctx.send('pong')

#elBulloso.run(token_bot)