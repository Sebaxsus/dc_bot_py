import discord 
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()



elBulloso = commands.Bot(command_prefix='$', description="Prueba", intents=intents)

@elBulloso.command()
async def ping(ctx):
    await ctx.send('Pong')

@elBulloso.command()
async def info(ctx):
    ambed = discord.Embed(title=f'{ctx.guild.name}', description=f"La mierda mas grande jamas vista A.K.A Yo")
    await ctx.send(embed=ambed)

@elBulloso.command()
async def usuarios(ctx):
    for t in test:
        await ctx.send(t)

@elBulloso.command() #No sirve, alparece la property mention no tiene setter, ._.
async def flick(ctx):
    
    await ctx.send(f'{ctx.guild.get_member_named('sebax')}')

#client.guild.get_member_named('nombre') me busca el primer nombre mas cercano a eso sin id y sin na :/

@elBulloso.event
async def on_ready():
    members = elBulloso.get_all_members()
    global test
    test = list(elBulloso.users)
    print(elBulloso.user.mention)
    print(f'Inicializando como {elBulloso.user}')

elBulloso.run('MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc')