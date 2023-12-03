import discord 
from discord.ext import commands

import datetime

from urllib import parse, request
import re
import json
import os
from youtube_dl import YoutubeDL

#El intents es indispensable, Se usa para que el bot y la libreria obtenga informacion de
#La api de discord con permisos, Los permiosos son los intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()

#Utilizando la funcion commands de discord.ext, se define una descripcion y el comando con el que el bot
#Va a responder en el chat "command_prefix"
#   Es obligatorio mandarle el atributo "intends" ya que asi el bot obtiene permisos y informacion
elBulloso = commands.Bot(command_prefix='$', description="Bot de Musica En desarrollo", intents=intents)

#Diccionarios para almacenar la id de la Guild (Server) y el status actual del bot
isPlaying = {}

isPaused = {}

queue = {}
#Diccionario con id de la Guild (Server) y cuantas canciones estan en cola
queueIndex = {}
#Diccionario con id de la Guild y el status de si esta conectado a un canal de voz o no
isInVc = {}

#Constant for ytdl_Youtube and FFMPEG

YTDL_OPTIONS = {'format': 'bestaudio', 'nonplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

#El discord.utils.find solo busca los nombres exactos sin alias el nombre de discord
@elBulloso.command()
async def ping(ctx, *, nombre):
    try:
        user = discord.utils.find(lambda m: m.name == nombre, ctx.channel.guild.members)
        #tempUserId = None
        #tempUserName = None
        tempUserObject = None
    except:
        ctx.send("Usuario No encontrado")
    else:
        for m in ctx.channel.guild.members:
            if user in m.name: #busco el usario dentro de todos los usuarios de la guild
                #print(m.id, nombre)
                #tempUserId = m.id
                #tempUserName = m.name
                tempUserObject = m
        await ctx.send(f'Pong {tempUserObject.mention}') #con los objetos Puedo mencionar, sacarle la info del objeto (User)

@elBulloso.command()
async def info(ctx):
    ambed = discord.Embed(title=f'{ctx.guild.name}', description=f"La mierda mas grande jamas vista",timestamp=datetime.datetime.utcnow(), color=discord.colour.Color.dark_blue())
    ambed.add_field(name="Dueño del server", value=f'{ctx.guild.owner}')
    ambed.add_field(name="Region del server", value=f'{ctx.guild.region}')
    ambed.add_field(name="Id del Servidor", value=f'{ctx.guild.id}')
    ambed.set_thumbnail(url=f"{ctx.guild.icon}")
    ambed.set_author(name="sebaxsus")
    await ctx.send(embed=ambed)

#Comando para conectar / Mover el bot a un canal de voz
@elBulloso.command()
async def unirse(ctx, channel):
    idGuild = int(ctx.guild.id)
    if isInVc[idGuild] == None or not isInVc[idGuild].is_connected():
        isInVc[idGuild] = await channel.connect()

        if isInVc[idGuild] == None:
            await ctx.send("No me pude conectar al canal de voz")
            return
        else:
            await isInVc.move_to(channel)

#Comando que lee el mensaje y busca eso mismo en youtube
@elBulloso.command()
async def play(ctx, *,search):
    buscar = parse.urlencode({'search_query': search})#                                                                              <<<---   (search_query=search)
    htmlContent = request.urlopen('https://www.youtube.com/results?' + buscar)#htmlContent = request.urlopen('https://www.youtube.com/results?' + buscar)
    resultadosBusqueda = re.findall('/watch\?v=(.{11})', htmlContent.read().decode())
    print(f"Resultados Busqueda: https://www.youtube.com/results?{buscar} \n")
    print(resultadosBusqueda[0:10])
    await ctx.send(f"Busqueda Exitosa: https://www.youtube.com/results?{buscar}")

@elBulloso.command()
async def usuarios(ctx):
    usuarios = list(elBulloso.users)
    for user in usuarios:
        await ctx.send(user)

@elBulloso.command() #No sirve, al parecer la property mention no tiene setter, ._.
async def sebax(ctx):
    objetoUser = None
    for m in ctx.guild.members:
        if 'sebaxsus' == m.name:
            objetoUser = m
    await ctx.send(f'{m.mention}')

#client.guild.get_member_named('nombre') me busca el primer nombre mas cercano a eso sin id y sin na :/

@elBulloso.event
async def on_ready():
    #members = elBulloso.get_all_members() #Obtiene todos los usuarios que ve el bot y los guarda en members
    for guild in elBulloso.guilds:
        idGuild = int(guild.id)
        queue[idGuild] = []
        queueIndex[idGuild] = 0
        isInVc[idGuild] = None
        isPaused[idGuild] = isPlaying[idGuild] = False
    #print(elBulloso.user.mention)
    print(f'Inicializando como {elBulloso.user}')

elBulloso.run('MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc')