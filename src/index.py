import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()

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

client.run('MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc')

#Configuro el bot con 'commands.Bot()'  / command_prefix define con que caracter el bot va a responder

#elBulloso = commands.Bot(command_prefix='!', description="Intento de bot con discord.py")

#@elBulloso.command()
#Con ping el servidor me respondera, se usa para verificar la conexion del bot al servidor
#async def ping(ctx):
#    await ctx.send('pong')

#elBulloso.run('MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc')