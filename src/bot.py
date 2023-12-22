import discord 
from discord.ext import commands

import datetime

from urllib import parse, request
import re
import json
import os
from youtube_dl import YoutubeDL

#Colores embed Azul= 0x2c76dd, Rojo= 0xdf1141, Verde= 0x0eaa51

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

#Funcion para extraer el audio/cancion de el resultado de busqueda en $play
def extraerCancion(url):
    with YoutubeDL(YTDL_OPTIONS) as ydl:
        try:
            raw = ydl.extract_info(url, download=False)
        except:
            return False
    return {
        'link':'https://www.youtube.com/results?' + url,
        'Miniatura': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
        'Source': raw['fomats'][0]['url'],
        'Titulo': raw['title']
    }

#El discord.utils.find solo busca los nombres exactos sin alias el nombre de discord
@elBulloso.command()
async def ping(ctx, *, nombre):
    #Para manejar un error y usar discord como respuesta al error se debe usar el manejador de errores de discord.ext.commands alias on_command_error() o error().
    #Tambien hay un condicional llamado check usado comunmente para verificar permisos de usuario y si puede usar comandos o no.
    try:
        #La variable user guarda un objecto que genere la funcion find de utils, En otras palbras lo que se guarda en user es un objeto no un string ni nada parecido.
        user = discord.utils.find(lambda m: m.name == nombre, ctx.channel.guild.members)
        print(f"OBjetos o string?: {user}, {user.name}, {type(user)}, {type(user.name)}, {user.id}") #Prueba
        #tempUserId = None
        #tempUserName = None
        tempUserObject = None
    except:
        await ctx.send("Usuario No encontrado")
    else:
        for m in ctx.channel.guild.members:
            if user.name in m.name: #busco el usario dentro de todos los usuarios de la guild
                #print(m.id, nombre)
                #tempUserId = m.id
                #tempUserName = m.name
                tempUserObject = m
        await ctx.send(f'Pong {tempUserObject.mention}') #con los objetos Puedo mencionar, sacarle la info del objeto (User)


@elBulloso.command()
async def unirse(ctx):
    idGuild = int(ctx.guild.id)
    channel = ctx.author.voice.channel
    #if(channel == None):
        #channel = ctx.author.voice.channel
    if isInVc[idGuild] == None or not isInVc[idGuild].is_connected():
        isInVc[idGuild] = await channel.connect()
        await ctx.send(embed=discord.Embed(
            title=f"Conectado a {ctx.author.voice.channel}",
            description=f"Peticion de union hecha por {ctx.author.mention}",
            colour=0x0eaa51
        ))
        if isInVc[idGuild] == None:
            await ctx.send("No me pude conectar al canal de voz")
            return
    else:
        await isInVc[idGuild].move_to(channel)

@elBulloso.command()
async def info(ctx):
    ambed = discord.Embed(title=f'{ctx.guild.name}', description=f"La mierda mas grande jamas vista",timestamp=datetime.datetime.utcnow(), color=discord.colour.Color.dark_blue())
    ambed.add_field(name="Dueño del server", value=f'{ctx.guild.owner}')
    #ambed.add_field(name="Region del server", value=f'{ctx.guild.region}') Segun lo visto en la documentacion el metodofo .region de Discord.guild no existe >:(
    ambed.add_field(name="Id del Servidor", value=f'{ctx.guild.id}')
    ambed.set_thumbnail(url=f"{ctx.guild.icon}")
    ambed.set_author(name="sebaxsus")
    await ctx.send(embed=ambed)

#Comando para conectar / Mover el bot a un canal de voz Edit: No deberia ser un comando
#Funcion para conectar el bot al canal de voz del autor 
#@elBulloso.command()
async def conectarse(ctx, channel):
    idGuild = int(ctx.guild.id)
    if isInVc[idGuild] == None or not isInVc[idGuild].is_connected():
        isInVc[idGuild] = await channel.connect()

        if isInVc[idGuild] == None:
            await ctx.send("No me pude conectar al canal de voz")
            return
    else:
        await isInVc[idGuild].move_to(channel)

def embed_Reproduciendo_Ahora(ctx, cancion):
    Titulo = cancion['Titulo']
    link = cancion['link']
    miniatura = cancion['Miniatura']
    usuario = ctx.author
    print(f'Autor en funcion embed: {ctx.author}, Tipo: {type(ctx.author)}')
    pfp = usuario.avatar_url

    embed = discord.Embed(
        title="Reproduciendo:",
        description=f'[{Titulo}]({link})',
        colour=0xdf1141
    )
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    return embed

async def mensaje(ctx, mensaje):
    try:
        ctx.send(embed=mensaje)
    except:
        print("Error al mandar mensaje mediante la funcion mensaje")

def siguienteCancion(ctx):
    idGuild = int(ctx.guild.id)
    if not isPlaying[idGuild]:
        return
    if queueIndex[idGuild] + 1 < len(queue[idGuild]):
        isPlaying[idGuild] = True
        queueIndex[idGuild] += 1

        cancion = queue[idGuild][queueIndex[idGuild]][0]
        mensaje(ctx, embed_Reproduciendo_Ahora(ctx, cancion))

        isInVc[idGuild].play(discord.FFmpegPCMAudio(
            cancion['source'], FFMPEG_OPTIONS, after=lambda e: siguienteCancion(ctx)
        ))
    else:
        queueIndex[idGuild] += 1
        isPlaying = False
        


#Funcion para reproducir la musica
async def reproducir(ctx):
    idGuild = int(ctx.guild.id)
    if queueIndex[idGuild] < len(queue[id]):
        isPlaying[idGuild] = True
        isPaused[idGuild] = False

        await conectarse(ctx, queue[idGuild][queueIndex[idGuild]][1])

        cancion = queue[idGuild][queueIndex[idGuild]][0]
        await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))

        isInVc[idGuild].play(discord.FFmpegPCMAudio(
            cancion['source'], FFMPEG_OPTIONS, after=lambda e: siguienteCancion(ctx)
        ))
    else:
        await ctx.send("No hay mas canciones en la cola de reproduccion")
        queueIndex[idGuild] += 1
        isPlaying = False


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
    await ctx.send(f'{objetoUser.mention}')

#client.guild.get_member_named('nombre') me busca el primer nombre mas cercano a eso sin id y sin na :/
    
#commands.command es una simplificacion del metodo (commandtree) de discord.py
#Lo que hace es guardar y mostrar una breve descricion del comando al momendo de escribir el comando en discord



#Comando para unir al bot al canal de voz del usuario
@elBulloso.command(
    name="unirse",
    aliases=["u"],
    help="Comando usado para unir al bot al canal de voz actual"
)
async def unirse(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await conectarse(ctx, channel)
        await ctx.send(embed=discord.Embed(
            title=f"Conectado a {ctx.author.voice.channel}",
            description=f"Peticion de union hecha por {ctx.author.mention}",
            colour=0x0eaa51
        ))
    else:
        await ctx.send(f'Tiene que estar en un canal de voz para unirme.')

@elBulloso.command(
        name="salir",
        aliases=["s"],
        help="Comando usado para desconectar el bot del canal de voz actual.\nEsto eliminara la cola de reproduccion actual."
)
async def salir(ctx):
    idGuild = int(ctx.guild.id)
    isPlaying[idGuild] = isPaused[idGuild] = False
    queue[idGuild] = []
    queueIndex[idGuild] = 0
    if isInVc[idGuild] != None:
        await ctx.send(embed=discord.Embed(
            title=f"Desconectado de: {ctx.author.voice.channel}",
            description=f"Peticion hecha por {ctx.author.mention}",
            colour=0xdf1141
        ))
        await ctx.send("ElBulloso Se abrio.")
        await isInVc[idGuild].disconnect()

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