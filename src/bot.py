import discord 
from discord.ext import commands
import pyaudio, io, sys, pydub, pytube
import numpy as np
import wave
import os

import datetime

from urllib import parse, request
import re
import json
import os
#from youtube_dl import YoutubeDL
import asyncio
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch


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
#YTDL_OPTIONS = {'format': 'bestaudio', 'nonplaylist': 'True'}
#FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


YTDL_OPTIONS = {'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

def endSong(path):
    os.remove(path)

def esUrl(texto):
    tmp = False
    texto = texto.split()
    for i in texto:
        if i.startswith("https:"):
            tmp = True
    return tmp

def getStream(url):

    #Crea un buffer
    buffer = io.BytesIO()
    #Con la libreria Pytube crea un objeto de la url de yotube
    yt = pytube.YouTube(url)

    #Obtengo el stream (DASH) y lo filtro para solo obtener el audio y obtener el primer resultado
    audio_stream = yt.streams.filter(only_audio=True).first()
    
    #Con la libreria io methodo BytesIo que me escribe el stream en el buffer
    audio_data = io.BytesIO(audio_stream.stream_to_buffer(buffer))

    #Inicializo el buffer, Por que ni idea
    buffer.seek(0)

    #audio = pydub.AudioSegment.from_file(buffer, format="mp4")

    #audio_source = discord.AudioSource.read(audio)

    #print("audio source type: ", audio_source)


    #Mando el buffer en formato BufferedIOBase
    return buffer

#Funcion para extraer el audio/cancion de el resultado de busqueda en $play
def extraerCancion(url):
    codeUrl = url.removeprefix("https://www.youtube.com/watch?v=")
    print(codeUrl)
    with YoutubeDL(YTDL_OPTIONS) as ydl:
        try:
            raw = ydl.extract_info(codeUrl, download=False)["title"]
        except:
            return False
    search = VideosSearch(url, limit= 1)
    #print(search.result())
    #print("\nSeparador\n")
    #print(search.result()["result"][0])
    #print("\nSeparador\n")
    #print(search.result()["result"][0]["link"])
    return {
        'link': url,
        'Miniatura': 'https://i.ytimg.com/vi/' + codeUrl + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
        'Source': search.result()["result"][0]["link"],
        'Titulo': search.result()["result"][0]["title"]
    }

#funcion que lee el mensaje y busca eso mismo en youtube
def buscar(search):
    buscar = parse.urlencode({'search_query': search})#                                                                              <<<---   (search_query=search)
    htmlContent = request.urlopen('https://www.youtube.com/results?' + buscar)#htmlContent = request.urlopen('https://www.youtube.com/results?' + buscar)
    resultadosBusqueda = re.findall('/watch\?v=(.{11})', htmlContent.read().decode())
    #print(f"Resultados Busqueda: https://www.youtube.com/results?{buscar} \n")
    #print(resultadosBusqueda[0:5])
    return resultadosBusqueda[0:2]


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
async def info(ctx):
    ambed = discord.Embed(title=f'{ctx.guild.name}', description=f"La mierda mas grande jamas vista",timestamp=datetime.datetime.utcnow(), color=discord.colour.Color.dark_blue())
    ambed.add_field(name="Dueño del server", value=f'{ctx.guild.owner}')
    #ambed.add_field(name="Region del server", value=f'{ctx.guild.region}') Segun lo visto en la documentacion el metodofo .region de Discord.guild no existe >:(
    ambed.add_field(name="Id del Servidor", value=f'{ctx.guild.id}')
    ambed.set_thumbnail(url=f"{ctx.guild.icon}")
    ambed.set_author(name="sebaxsus")
    await ctx.send(embed=ambed)

@elBulloso.command(
    name="pause",
    aliases=["d"],
    help="Commando para detener la reproduccion de la cola."
)
async def pause(ctx):
    idGuild = int(ctx.guild.id)
    if not isInVc[idGuild]:
        await ctx.send("No hay canciones por pausar.")
    elif isPlaying[idGuild]:
        await ctx.send("Pausando la cancion!.")
        isPlaying[idGuild] = False
        isPaused[idGuild] = True
        isInVc[idGuild].pause()

@elBulloso.command(
    name="resume",
    aliases=["r"],
    help="Commando para volver a reproducir una cancion pausada"
)
async def resume(ctx):
    idGuild = int(ctx.guild.id)
    if not isInVc[idGuild]:
        await ctx.send("No hay canciones por reproducir.")
    elif isPaused[idGuild]:
        await ctx.send("Reanudando la cancion!.")
        isPlaying[idGuild] = True
        isPaused[idGuild] = False
        isInVc[idGuild].resume()

#Comando para conectar / Mover el bot a un canal de voz Edit: No deberia ser un comando
#Funcion para conectar el bot al canal de voz del autor 
#@elBulloso.command()
async def conectarse(ctx, channel):
    idGuild = int(ctx.guild.id)
    if isInVc[idGuild] == None or not isInVc[idGuild].is_connected():
        isInVc[idGuild] = await channel.connect()
        em = discord.Embed(
            title=f"Conectado a {ctx.author.voice.channel}",
            description=f"Peticion de union hecha por {ctx.author.mention}",
            colour=0x0eaa51
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        await ctx.send(embed=em)
        if isInVc[idGuild] == None:
            await ctx.send("No me pude conectar al canal de voz")
            return
    else:
        await isInVc[idGuild].move_to(channel)

def embed_Reproduciendo_Ahora(ctx, cancion):
    Titulo = cancion['Titulo']
    link = cancion['link']
    #link = 'prueba'
    miniatura = cancion['Miniatura']
    usuario = ctx.author
    #print(f'Autor en funcion embed: {ctx.author}, Tipo: {type(ctx.author)}') #Autor en funcion embed: sebaxsus, Tipo: <class 'discord.member.Member'>
    pfp = usuario.display_avatar
    embed = discord.Embed(
        title="Reproduciendo:",
        description=f'[{Titulo}]({link})',
        colour=0x2c76dd
    )
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    return embed

def embed_Añadido_Queue(ctx, cancion):
    Titulo = cancion['Titulo']
    link = cancion['link']
    #link = 'prueba'
    miniatura = cancion['Miniatura']
    usuario = ctx.author
    #print(f'Autor en funcion embed: {ctx.author}, Tipo: {type(ctx.author)}') #Autor en funcion embed: sebaxsus, Tipo: <class 'discord.member.Member'>
    pfp = usuario.display_avatar
    embed = discord.Embed(
        title="Añadido a la cola:",
        description=f'[{Titulo}]({link})',
        colour=0x2c76dd
    )
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    return embed

async def mensaje(ctx, mensaje):
    try:
        print("Entro a mensaje embed")
        await ctx.send(embed=mensaje)
    except:
        print("Error al mandar mensaje mediante la funcion mensaje")
        return
    else:
        return

async def siguienteCancion(ctx):
    #print("\nEntro a siguiente cancion")
    idGuild = int(ctx.guild.id)
    if not isPlaying[idGuild]:
        return
    if queueIndex[idGuild] + 1 < len(queue[idGuild]):
        isPlaying[idGuild] = True
        queueIndex[idGuild] += 1

        cancion = queue[idGuild][queueIndex[idGuild]][0]
        mensaje(ctx, embed_Reproduciendo_Ahora(ctx, cancion))
        print("anted de await ctx.send en linea 267")
        await ctx.send(embed= embed_Reproduciendo_Ahora(ctx, cancion))
       # print(f"Source: {cancion['Source']}")
        await isInVc[idGuild].play(discord.FFmpegPCMAudio(
            source=getStream(cancion['link']), pipe=True), after=lambda e: siguienteCancion(ctx)
        )
    else:
        queueIndex[idGuild] += 1
        isPlaying[idGuild] = False
        


#Funcion para reproducir la musica
async def reproducir(ctx):
    idGuild = int(ctx.guild.id)
    if queueIndex[idGuild] < len(queue[idGuild]):
        isPlaying[idGuild] = True
        isPaused[idGuild] = False

        await conectarse(ctx, queue[idGuild][queueIndex[idGuild]][1])

        cancion = queue[idGuild][queueIndex[idGuild]][0]
        await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))
        isInVc[idGuild].play(discord.FFmpegPCMAudio(source=getStream(cancion['link']), pipe=True), after= lambda e: siguienteCancion(ctx))
        #print(f"Source: {cancion['Source']}")
        #isInVc[idGuild].play(discord.FFmpegPCMAudio(
        #    cancion['Source']), after=lambda e: siguienteCancion(ctx)
        #)
        isInVc[idGuild].source = discord.PCMVolumeTransformer(isInVc[idGuild].source, 0.5)
    else:
        await ctx.send("No hay mas canciones en la cola de reproduccion")
        queueIndex[idGuild] += 1
        isPlaying[idGuild] = False

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
        em = discord.Embed(
            title=f"Desconectado de {ctx.author.voice.channel}",
            description=f"ElBulloso Se abrio por culpa de {ctx.author.mention}",
            colour=0xdf1141
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        await ctx.send(embed=em)
        await isInVc[idGuild].disconnect()
        isInVc[idGuild] = None

@elBulloso.command(
        name="play",
        aliases=["p"],
        help="Comando para buscar en youtube una cancion con el nombre de la cancion"
)
async def play(ctx, *args):
    search = " ".join(args)
    idGuild = int(ctx.guild.id)
    try:
        channel = ctx.author.voice.channel
        await conectarse(ctx, channel)
    except:
        em = discord.Embed(
            title=f"No me pude conectar {ctx.author.mention}",
            description=f"Para conectarme debe estar en un canal de voz",
            colour=0xdf1141
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        await ctx.send(embed=em)
        return
    if not args:
        if len(queue[idGuild]) == 0:
            await ctx.send("No hay canciones en la cola")
            return
        elif not isPlaying[idGuild]:
            if queue[idGuild] == None or isInVc[idGuild] == None:
                #isPlaying[idGuild] = False       Si se da;a algo activar esto
                await reproducir(ctx)
            else:
                isPaused[idGuild] = False
                isPlaying[idGuild] = True
                isInVc[idGuild].resume()
        else:
            return
    else:
        if esUrl(search) == True:
            cancion = extraerCancion(search)
        else:
            cancion = extraerCancion('https://www.youtube.com/watch?v='+buscar(search)[0])

        if type(cancion) == type(True):
            await ctx.send(f"Que mierda buscate sapa {ctx.author.mention}")
            return
        else:
            queue[idGuild].append([cancion, channel])

            if not isPlaying[idGuild]:
                await reproducir(ctx)
            else:
                await ctx.send(embed=embed_Añadido_Queue(ctx, cancion))
    




@elBulloso.event
async def on_ready():
    #members = elBulloso.get_all_members() #Obtiene todos los usuarios que ve el bot y los guarda en members
    for guild in elBulloso.guilds:
        idGuild = int(guild.id)
        queue[idGuild] = []
        queueIndex[idGuild] = 0
        isInVc[idGuild] = None
        isPlaying[idGuild] = False
        isPaused[idGuild] = False
    #print(elBulloso.user.mention)
    print(f'Inicializando como {elBulloso.user}')

#Listener para que el bot se desconecte al momento que no hallan usuarios en el canal de voz actual del bot.
@elBulloso.listen()
async def on_voice_state_update(member, before, after):
    idGuild = int(member.guild.id)
    if member.id != elBulloso.user.id and before.channel != None and after.channel != before.channel:
        usuariosEnCanal = before.channel.members
        if len(usuariosEnCanal) == 1 and usuariosEnCanal[0].id == elBulloso.user.id and isInVc[idGuild].is_connected():
            isPlaying[idGuild] = isPaused[idGuild] = False
            queue[idGuild] = []
            queueIndex[idGuild] = 0
            await isInVc[idGuild].disconnect()

elBulloso.run('MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc')