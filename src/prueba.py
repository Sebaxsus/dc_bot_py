import discord 
from discord.ext import commands
import pyaudio, io, sys, pydub, pytube
import numpy as np
import wave

import datetime

from urllib import parse, request
import re
import json
import os
#from youtube_dl import YoutubeDL
import asyncio
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import pathlib, dotenv

sys.path.append(str(pathlib.Path(__file__).parent.parent / "Dev2025/modules"))

DOTENV_PATH = pathlib.Path(__file__).parent / '.env'

dotenv.load_dotenv(DOTENV_PATH)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

#El intents es indispensable, Se usa para que el bot y la libreria obtenga informacion de
#La api de discord con permisos, Los permiosos son los intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()

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



elBulloso = commands.Bot(command_prefix='$', description="Prueba", intents=intents)

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

@elBulloso.command() #No encuentra nada / No sirve \_(._.)_/
async def play1_NoSirve(ctx, *, search):
    link = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + link)
    search_result = re.findall('href=\"\\/watch\\?=(.{11})', html_content.read().decode())
    print(search_result)
    await ctx.send('https://www.youtube.com/watch?v=' + search_result[0]) 

@elBulloso.command()
async def unirse(ctx):
    idGuild = int(ctx.guild.id)
    channel = ctx.author.voice.channel
    if(channel == None):
        channel = ctx.author.voice.channel
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

def extraerCancion(url):
    with YoutubeDL(YTDL_OPTIONS) as ydl:
        try:
            raw = ydl.extract_info(url, download=False)["title"]
        except:
            return False
    return {
        'link':'https://www.youtube.com/results?' + url,
        'Miniatura': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
        'Source': raw['url'],
        'Titulo': raw['title']
    }

@elBulloso.command(
        name="prueba",
        aliases=["h"],
        help="Comando temporal para probar las funcionalidades que ese estan desarrollando."
)
async def prueba(ctx, *args):
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
                isPlaying[idGuild] = False
                await reproducir(ctx)
            else:
                isPaused[idGuild] = False
                isPlaying[idGuild] = True
                isInVc[idGuild].resume()
        else:
            return
    else:
        cancion = extraerCancion(buscar(search)[0])
        if type(cancion) == type(True):
            await ctx.send(f"Que mierda buscate sapa {ctx.author.mention}")
        else:
            queue[idGuild].append([cancion, channel])

            if not isPlaying[idGuild]:
                await reproducir(ctx)
            else:
                await ctx.send(f"Agregado a la cola de reproduccion")
        #queue[idGuild].append([{
        #'link':'https://www.youtube.com/watch?v=yetGML1gWow&list=PLq4RAMp8kLaKvtCnHxEErokU5Kb--fmai&index=1&pp=gAQBiAQB',
        #'Miniatura': 'C:/Users/sebax/OneDrive/Imágenes/Sadgi.JPG',
        #'Source': 'C:/Users/sebax/Music/Triste.mp3',
        #'Titulo': 'Triste'
    #}, channel])

        #if not isPlaying[idGuild]:
            #await reproducir(ctx)
        #else:
            #await ctx.send(f"Agregado a la cola de reproduccion")

elBulloso.run(DISCORD_TOKEN)