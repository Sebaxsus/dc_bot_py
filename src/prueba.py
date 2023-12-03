import discord 
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()



elBulloso = commands.Bot(command_prefix='$', description="Prueba", intents=intents)

@elBulloso.command()
async def ping(ctx, *, nombre):
    user = discord.utils.find(lambda m: m.name == nombre, ctx.channel.guild.members)
    print(user, nombre, ctx.channel.guild.members)
    print("Separador \n")
    #print(discord.Guild.get_member_named(ctx.guild.id, str(nombre)))
    print(discord.Guild.members)
    await ctx.send(f'Pong {user}')

@elBulloso.command()
async def info(ctx):
    ambed = discord.Embed(title=f'{ctx.guild.name}', description=f"La mierda mas grande jamas vista A.K.A Yo")
    await ctx.send(embed=ambed)

#@elBulloso.command()
#async def usuarios(ctx):
    #for t in test:
        #await ctx.send(t)

@elBulloso.command() #No sirve, alparece la property mention no tiene setter, ._.
async def flick(ctx):
    
    await ctx.send(f'{ctx.guild.get_member_named('sebax')}')

#client.guild.get_member_named('nombre') me busca el primer nombre mas cercano a eso sin id y sin na :/

#El discord.utils.find solo busca los nombres exactos sin alias el nombre de discord
@elBulloso.command()
async def ping(ctx, *, nombre):
    user = discord.utils.find(lambda m: m.name == nombre, ctx.channel.guild.members)
    tempUserId = None
    tempUserName = None
    tempUserObject = None
    print(user, nombre, ctx.channel.guild.members)
    for m in ctx.channel.guild.members:
        if user in m.name:
            print(m.id, nombre)
            tempUserId = m.id
            tempUserName = m.name
            tempUserObject = m
            print("encontrado")  
    print("Separador \n")
    #print(discord.Guild.get_member_named(ctx.guild.id, str(nombre)))
    print(discord.Guild.members)
    await ctx.send(f'Pong {tempUserObject.mention}') #con los objetos Puedo mencionar, sacarle la info del objeto (User)
    print(elBulloso.user.mention)
    print(f'Inicializando como {elBulloso.user}')

elBulloso.run('MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc')