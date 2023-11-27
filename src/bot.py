import discord 
from discord.ext import commands

import datetime

from urllib import parse, request
import re

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()


elBulloso = commands.Bot(command_prefix='$', description="Bot de Musica En desarrollo", intents=intents)

@elBulloso.command()
async def ping(ctx):
    await ctx.send('Pong')

@elBulloso.command()
async def info(ctx):
    ambed = discord.Embed(title=f'{ctx.guild.name}', description=f"La mierda mas grande jamas vista",timestamp=datetime.datetime.utcnow(), color=discord.colour.Color.dark_blue())
    ambed.add_field(name="Dueño del server", value=f'{ctx.guild.owner}')
    ambed.add_field(name="Region del server", value=f'{ctx.guild.region}')
    ambed.add_field(name="Id del Servidor", value=f'{ctx.guild.id}')
    ambed.set_thumbnail(url=f"{ctx.guild.icon}")
    ambed.set_author(name="sebaxsus")
    await ctx.send(embed=ambed)

@elBulloso.command()
async def play(ctx, *, search):
    link = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + link)
    search_result = re.findall('href=\"\\/watch\\?=(.{11})', html_content.read().decode())
    print(search_result)
    await ctx.send('https://www.youtube.com/watch?v=' + search_result[1])


@elBulloso.command()
async def usuarios(ctx):
    usuarios = list(elBulloso.users)
    for user in usuarios:
        await ctx.send(user)

@elBulloso.command() #No sirve, alparece la property mention no tiene setter, ._.
async def flick(ctx):
    
    await ctx.send(f'{ctx.guild.get_member_named('sebax')}')

#client.guild.get_member_named('nombre') me busca el primer nombre mas cercano a eso sin id y sin na :/

@elBulloso.event
async def on_ready():
    members = elBulloso.get_all_members()
    #print(elBulloso.user.mention)
    print(f'Inicializando como {elBulloso.user}')

elBulloso.run('MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc')