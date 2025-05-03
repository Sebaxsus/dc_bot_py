import discord 
from discord import app_commands
from discord.ext import commands
import spotipy, dotenv, yt_dlp, asyncio, functools, datetime


env = dotenv.dotenv_values("bot_dc_py/src/.env")

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/authorize"

#enviromentVariables = dotenv_values("bot_dc_py/src/.env")
spClientId='99d13bd2585a46c8acc7b7c9028dbfbe'
spClientSecret='dc04ddb0ad22464c94a65580f5fdd529'
spApi = "https://api.spotify.com/v1/"
spEndPoint = "/track/{track_id}"
spURI = 'http://localhost:3000'
spUricall = 'http://google.com/callback/'
tokenBot = 'MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc'

scope = """ugc-image-upload,user-read-playback-state,user-modify-playback-state,user-read-currently-playing,
app-remote-control,streaming,playlist-read-private,playlist-modify-public,playlist-read-collaborative,user-read-email,user-read-private
"""

auth_manager = spotipy.oauth2.SpotifyPKCE(
    client_id=spClientId,
    redirect_uri=spUricall,
    scope=scope
)
#auth_manager = spotipy.oauth2.SpotifyClientCredentials(client_id=spClientId, client_secret=spClientSecret)
# token = auth_manager.get_access_token()
#token = token_dict['access_token']

cliente = spotipy.Spotify(auth_manager=auth_manager)

# try:
#     #print(token)
#     user_name = cliente.current_user() 
# except:
#     print("Fallo token")
# else:
#     #print(json.dumps(user_name, sort_keys=True, indent=4))
#     #print(f'token: {token}')
#     print('token correcto')


########################################################## Discord Para Abajo

#Colores embed Azul= 0x2c76dd, Rojo= 0xdf1141, Verde= 0x0eaa51
AZUL,ROJO,VERDE,DARK_PURPLE,DARK_BLUE = 0x2c76dd, 0xdf1141,0x0eaa51,0x71368A,0x206694
TEAL,DARK_RED,DARK_GREEN = 0x1ABC9C, 0x992D22,0x1F8B4C


#El intents es indispensable, Se usa para que el bot y la libreria obtenga informacion de
#La api de discord con permisos, Los permiosos son los intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()

#Utilizando la funcion commands de discord.ext, se define una descripcion y el comando con el que el bot
#Va a responder en el chat "command_prefix", Y con commands.when_mentioned_or el bot tambien respondera como prefijo cuadno lo mencionen
#   Es obligatorio mandarle el atributo "intends" ya que asi el bot obtiene permisos y informacion
elBulloso = commands.Bot(command_prefix=commands.when_mentioned_or('$'), description="Bot de Musica En desarrollo", intents=intents)

#https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.when_mentioned_or Esto e



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

ydl_options = {
    'format': 'bestaudio/best', # Selecciono el mejor formato de audio disponible
    'quiet': True, # Silencia el log de yt_dlp
    'no_warnings': True, # Silencia las advertencias en consola de yt_dlp
    'skip_download': True, # No descarga el archivo
    'default_search': 'ytsearch',
    'extract_flat': False,
    'noplaylist': True,
    'default_search': 'ytsearch3',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn',
    }

def verificarTokenSpotify():
    global token
    print("Entro a verificar token")
    tokenAuthSpotify = auth_manager.get_cached_token()
    
    print(auth_manager.is_token_expired(tokenAuthSpotify))
    if auth_manager.is_token_expired(tokenAuthSpotify):
        print(f"El token espiro: {auth_manager.is_token_expired(tokenAuthSpotify)}, Extendiendo Tiempo del Token...")
        try:
            token = auth_manager.refresh_access_token(tokenAuthSpotify['refresh_token'])
            print("Nuevo token: ", token['access_token'],"\n",token)
            #token = auth_manager.get_access_token()
        except Exception as e:
            print(f"No se pudo extender el Tiempo del token en spotify, ", e)
        else:
            print(f"Se extendio el tiempo del token:\nExpiro el token?: {auth_manager.is_token_expired(tokenAuthSpotify)}")

def MensajeBasico(titulo, texto, color) -> discord.embeds.Embed:
    em = discord.Embed(
            title=titulo,
            description=texto,
            colour=color
        )
    em.set_footer(icon_url=elBulloso.user.display_avatar)
    return em

def embed_Reproduciendo_Ahora(ctx, cancion):
    Titulo = cancion['Titulo']
    link = cancion['link']
    #link = 'prueba'
    miniatura = cancion['Miniatura']
    Canal = cancion['Canal']
    Duracion = cancion['Duracion']
    usuario = ctx.author
    #print(f'Autor en funcion embed: {ctx.author}, Tipo: {type(ctx.author)}') #Autor en funcion embed: sebaxsus, Tipo: <class 'discord.member.Member'>
    pfp = usuario.display_avatar
    embed = discord.Embed(
        title="* Reproduciendo:",
        description=f'[{Titulo}]({link})',
        colour=0x2c76dd
    )
    embed.add_field(name="* Duracion", value=f"""```cs\n\t{Duracion}```""")
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

def format_audio_seconds(seconds):
    if seconds is None:
        return "desconocido"
    mins, secs = divmod(int(seconds), 60)
    return f"{mins}:{secs:02}"

def esUrl(texto):
    tmp = False
    texto = texto.split()
    for i in texto:
        if i.startswith("https:"):
            tmp = True
    return tmp

def nombreArtiCancionPlaylistTrack(datosTrack):
    artistaN = ""
    artistas = datosTrack['artists']
    cancion = datosTrack['name']
    for i in range(0, len(artistas), 1):
        artistaN += artistas[i]['name'] + " "

    return f"{cancion} - {artistaN}"

def guardarCancionesSpList(datos, idGuild, channel):
    # Datos es una lista que contiene todas las canciones de la Playlist
    # Dentro, es decir que su length es la cantidad de canciones dentro de la lista
    cancion = None
    for i, track in enumerate(datos):

        strCancion = nombreArtiCancionPlaylistTrack((track['track']))
        cancion = buscar(strCancion)

        queue[idGuild].append([cancion, channel])
        print(f"Cancion {i}: ", cancion['Titulo'])

    return cancion

async def busquedaPlaylist(ctx, channel, urlPlaylist):
    idGuild = int(ctx.guild.id)

    # strCancion = ""
    # cancion = None
    #Datos es la cantidad de canciones que contiene la playlist
    # ciclosDatosCancion = divmod(len(datos), 5)
    # Mod, restante

    datos = cliente.playlist(urlPlaylist)['tracks']['items']
    # Bloque de varias tareas
    bloques = [datos[i:i + 5] for i in range(0, len(datos), 5)]

    #Tareas nose
    tareas = []

    primer_bloque = bloques[0]
    func = functools.partial(guardarCancionesSpList, primer_bloque, idGuild, channel)

    #Espero a que se resuelva el primero bloque
    await elBulloso.loop.run_in_executor(None, func=func)

    # Reproducir primera cancion en el diccionario queue (cola)
    await reproducir(ctx)

    #Leer recurso para entender esto Link https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
    for bloque in bloques[1:]:

        # ini = 5 * i #al inicio sera 5 * 0 que es cero y nuestro punto de partida
        # last = 5 * (i + 1) # Al inicio sera 5 * (0 + 1) que es 5
        # if i == ciclosDatosCancion[0]:
        #     last = len(datos)
        #if not isPlaying[idGuild]:
            #asyncio.run_coroutine_threadsafe(reproducir(ctx), elBulloso.loop)
            #await reproducir(ctx)
        #else:
            #await ctx.send(embed=embed_Añadido_Queue(ctx, cancion))
            #pass

        func = functools.partial(guardarCancionesSpList, bloque, idGuild, channel)
        # El bloque de tareas que se va a guardar en la lista de bloques de tareas
        tarea = elBulloso.loop.run_in_executor(None, func=func)
        # Agregando el bloque de tareas a la lista de bloques de tareas
        tareas.append(tarea)
    # Espero a que todas las tareas terminen
    resultados = await asyncio.gather(*tareas)

    return resultados[-1] if resultados else None
        

def buscar(search):
    print("Buscando... ", search)
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        # search_results = []
        info = ydl.extract_info(f"ytsearch3:{search}", download=False)
        info = info['entries']
        return {
            'Titulo': info[0].get('title'),
            'link': info[0]['webpage_url'],
            'streamUrl': info[0]['url'],
            'Canal': info[0].get('uploader'),
            'Duracion': info[0].get('duration_string'), # Devuelve el tiempo de duracion ya formateado
            'Miniatura': info[0]['thumbnail'],
        }
        # for entry_info in info['entries']:
        #     title = entry_info.get("title", "Sin titulo")
        #     duration = entry_info.get("duration",0)
        #     search_results.append(entry_info)

def getStream(url):

    with yt_dlp.YoutubeDL(ydl_options) as ydl:

        info = ydl.extract_info(url, download=False)

        return {
            'Titulo': info.get('title'),
            'link': info['webpage_url'],
            'streamUrl': info['url'],
            'Canal': info.get('uploader'),
            'Duracion': format_audio_seconds(info.get('duration')),
            'Miniatura': info['thumbnail'],
            'info': info,
        }
def embed_Reproduciendo_Ahora(ctx, cancion):
    Titulo = cancion['Titulo']
    link = cancion['link']
    #link = 'prueba'
    miniatura = cancion['Miniatura']
    Canal = cancion['Canal']
    Duracion = cancion['Duracion']
    usuario = ctx.author
    #print(f'Autor en funcion embed: {ctx.author}, Tipo: {type(ctx.author)}') #Autor en funcion embed: sebaxsus, Tipo: <class 'discord.member.Member'>
    pfp = usuario.display_avatar
    embed = discord.Embed(
        title="* Reproduciendo:",
        description=f'[{Titulo}]({link})',
        colour=0x2c76dd
    )
    embed.add_field(name="* Duracion", value=f"""```cs\n\t{Duracion}```""")
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

def embed_Añadido_Queue(ctx, cancion):
    Titulo = cancion['Titulo']
    link = cancion['link']
    #link = 'prueba'
    miniatura = cancion['Miniatura']
    Canal = cancion['Canal']
    Duracion = cancion['Duracion']
    usuario = ctx.author
    #print(f'Autor en funcion embed: {ctx.author}, Tipo: {type(ctx.author)}') #Autor en funcion embed: sebaxsus, Tipo: <class 'discord.member.Member'>
    pfp = usuario.display_avatar
    embed = discord.Embed(
        title="* Añadido a la cola:",
        description=f'[{Titulo}]({link})',
        colour=DARK_PURPLE
    )
    embed.add_field(name="* Duracion", value=f"""```cs\n\t{Duracion}```""")
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

def embed_Eliminado_Queue(ctx, cancion):
    Titulo = cancion['Titulo']
    link = cancion['link']
    #link = 'prueba'
    miniatura = cancion['Miniatura']
    Canal = cancion['Canal']
    Duracion = cancion['Duracion']
    usuario = ctx.author
    #print(f'Autor en funcion embed: {ctx.author}, Tipo: {type(ctx.author)}') #Autor en funcion embed: sebaxsus, Tipo: <class 'discord.member.Member'>
    pfp = usuario.display_avatar
    embed = discord.Embed(
        title="* Eliminado de la Cola:",
        description=f'[{Titulo}]({link})',
        colour=DARK_RED
    )
    embed.add_field(name="* Duracion", value=f"""```cs\n\t{Duracion}```""")
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

async def mensaje(ctx, cancion):
    #idGuild = int(ctx.guild.id)
    #corutina = ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))
    em = embed_Reproduciendo_Ahora(ctx, cancion)
    #fut = asyncio.run_coroutine_threadsafe(corutina, elBulloso.loop)
    #await ctx.send(embed=em)
    try:
        #print("Entro a mensaje embed")
        #print('entro a mensaje')
        #fut.result()
        await ctx.send(embed=em, silent=True)
    except:
        print("Error al mandar mensaje mediante la funcion mensaje")
        pass
    else:
        return
    
#El discord.utils.find solo busca los nombres exactos sin alias el nombre de discord
@elBulloso.command(
        name="ping",
        aliases=["PING"],
        help="Comando para mencionar a un usuario usando su nombre global."
)
async def ping(ctx, *args):
    nombre = "".join(args)
    if not args:
        await ctx.send(f'Pong :ping_pong:')
    #Para manejar un error y usar discord como respuesta al error se debe usar el manejador de errores de discord.ext.commands alias on_command_error() o error().
    #Tambien hay un condicional llamado check usado comunmente para verificar permisos de usuario y si puede usar comandos o no.
    else:
        try:
            #La variable user guarda un objecto que genere la funcion find de utils, En otras palbras lo que se guarda en user es un objeto no un string ni nada parecido.
            user = discord.utils.find(lambda m: m.name == nombre, ctx.channel.guild.members)
            print(f"OBjetos o string?: {user}, {user.name}, {type(user)}, {type(user.name)}, {user.id}") #Prueba
            #tempUserId = None
            #tempUserName = None
            tempUserObject = None
        except:
            await ctx.send(embed=MensajeBasico("Error al ejecutar $ping :scream:","Usuario No encontrado",DARK_RED), silent=True)
        else:
            for m in ctx.channel.guild.members:
                if user.name in m.name: #busco el usario dentro de todos los usuarios de la guild
                    #print(m.id, nombre)
                    #tempUserId = m.id
                    #tempUserName = m.name
                    tempUserObject = m
            await ctx.send(f'Pong {tempUserObject.mention} :ping_pong:') #con los objetos Puedo mencionar, sacarle la info del objeto (User)


@elBulloso.command(
        name="info",
        aliases=["INFO"],
        help = "Este comando manda un mensaje con la informacion del servidor."
)
async def info(ctx):
    ambed = discord.Embed(title=f'{ctx.guild.name}', description=f"La mierda mas grande jamas vista",timestamp=datetime.datetime.utcnow(), color=discord.colour.Color.dark_blue())
    ambed.add_field(name="Dueño del server", value=f'{ctx.guild.owner}')
    #ambed.add_field(name="Region del server", value=f'{ctx.guild.region}') Segun lo visto en la documentacion el metodofo .region de Discord.guild no existe >:(
    ambed.add_field(name="Id del Servidor", value=f'{ctx.guild.id}')
    ambed.set_thumbnail(url=f"{ctx.guild.icon}")
    ambed.set_author(name="sebaxsus")
    await ctx.send(embed=ambed, silent=True)

@elBulloso.command(
    name="cola",
    aliases=["c", "C", "COLA"],
    help="Commando para mostrar la reproduccion de la cola."
)
async def cola(ctx):
    idGuild = int(ctx.guild.id)
    returnVaule = ""
    miniatura = queue[idGuild][queueIndex[idGuild]][0]['Miniatura']
    colaEmbed = discord.Embed(
        title="Cola de Reproduccion",
        description=returnVaule,
        colour=0x2c76dd
    )
    colaEmbed.set_thumbnail(url=miniatura)
    if queue[idGuild] == []:
        colaEmbed.clear_fields()
        colaEmbed.add_field(name="Cola Vacia",value="No hay canciones el la cola de reproducion.")
    else:
        for i in range(queueIndex[idGuild], len(queue[idGuild])):
            upNextSongs = len(queue[idGuild]) - queueIndex[idGuild]
            if i > 5 + upNextSongs:
                break
            returnIndex = i - queueIndex[idGuild]
            if returnIndex == 0:
                returnIndex = "Escuchando"
            elif returnIndex == 1:
                returnIndex = "Siguente"
            colaEmbed.add_field(name=f"{returnIndex}", value=f"[{queue[idGuild][i][0]['Titulo']}]({queue[idGuild][i][0]['link']})\n- {queue[idGuild][i][0]['Canal']} {queue[idGuild][i][0]['Duracion']}", inline=False)
            returnVaule += f"{returnIndex} - [{queue[idGuild][i][0]['Titulo']}]({queue[idGuild][i][0]['link']}) - {queue[idGuild][i][0]['Canal']} {queue[idGuild][i][0]['Duracion']}"

            if returnVaule == "":
                colaEmbed.clear_fields()
                colaEmbed.add_field(name="Cola Vacia",value="No hay canciones el la cola de reproducion.")
    await ctx.send(embed=colaEmbed, silent=True)

@elBulloso.command(
    name="limpiar",
    aliases=["l", "L", "LIMPIAR"],
    help="Commando para limpiear/Eliminar la cola de reproduccion."
)
async def limpiar(ctx):
    idGuild = int(ctx.guild.id)
    usuario = ctx.author
    pfp = usuario.display_avatar
    embedClear = discord.Embed(
        title="Cola de reproduccion Limpiada!",
        description=f'Se quitaron correctamente de la cola de reproduccion todas las canciones',
        colour=0x0eaa51
    )
    embedClear.set_footer(text=f'Peticion de: {str(usuario)}', icon_url=pfp)
    #if isInVc != None and isPlaying[idGuild]:
        #isPlaying[idGuild] = False
        #isPaused[idGuild] = False
        #isInVc[idGuild].pause()
    if queue[idGuild] != []:
        await ctx.send(embed=embedClear, silent=True)
        #print(f'Cola actual: {queue[idGuild]}\nCancion Cola en reproduccion {queue[idGuild][0]}')     
        del (queue[idGuild])[1:]
        #print(f'Cola actual: {queue[idGuild]}\nCancion Cola en reproduccion {queue[idGuild][0]}')
        #queue[idGuild] = []
    queueIndex[idGuild] = 0

@elBulloso.command(
        name="eliminar",
        aliases=["rm", "RM", "ELIMINAR"],
        help="Este comando elimina la ultima cancion agregada a la cola de reproduccion."
)
async def eliminar(ctx):
    idGuild = int(ctx.guild.id)
    if queue[idGuild] != []:
        cancion = queue[idGuild][-1][0]
        await ctx.send(embed=embed_Eliminado_Queue(ctx, cancion), silent=True)
    else:
        await ctx.send(embed=MensajeBasico("No se pudo Eliminar :melting_face: ","No hay canciones en la cola de reproduccion.",DARK_RED), silent=True)
    queue[idGuild] = queue[idGuild][:-1]
    if queue[idGuild] == []:
        if isInVc[idGuild] != None and isPlaying[idGuild]:
            isPlaying[idGuild] = isPaused[idGuild] = False
            isInVc.disconnect()
            isInVc[idGuild] = None
        queueIndex[idGuild] = 0
    elif queueIndex[idGuild] == len(queue[idGuild]) and isInVc[idGuild] != None and isInVc[idGuild]:
        isInVc.pause()
        queueIndex[idGuild] -= 1
        await reproducir(ctx)


@elBulloso.command(
    name="pause",
    aliases=["d", "pa", "PAUSE", "PA", "STOP", "stop", "D"],
    help="Commando para detener la reproduccion de la cola."
)
async def pause(ctx):
    idGuild = int(ctx.guild.id)
    if not isInVc[idGuild]:
        await ctx.send(embed=MensajeBasico("No se pudo Pausar :face_exhaling: ","No se puede pausar una cancion\nSi no estoy en un chat de voz.",ROJO), silent=True)
    elif isPlaying[idGuild]:
        await ctx.send(embed=MensajeBasico("Pausando! :sleeping: ","Pausando la cancion!.",DARK_GREEN), silent=True)
        isPlaying[idGuild] = False
        isPaused[idGuild] = True
        isInVc[idGuild].pause()

@elBulloso.command(
    name="resume",
    aliases=["r", "RESUME", "R"],
    help="Commando para volver a reproducir una cancion pausada"
)
async def resume(ctx):
    print("Resumiendo...")
    idGuild = int(ctx.guild.id)
    if not isInVc[idGuild]:
        await ctx.send(embed=MensajeBasico("No se pudo reanudar :nerd: ","No hay canciones por reproducir.",ROJO), silent=True)
    elif isPaused[idGuild]:
        await ctx.send(embed=MensajeBasico("Reanudando! :upside_down: ","Reanudando la cancion!.",DARK_GREEN), silent=True)
        isPlaying[idGuild] = True
        isPaused[idGuild] = False
        isInVc[idGuild].resume()

@elBulloso.command(
    name="skip",
    aliases=["s", "S", "SKIP"],
    help="Commando para saltar a la siguente cancion en la cola de reproducion"
)
async def skip(ctx, *arg):
    #print("".join(arg))
    arg = " ".join(arg)
    #print(not arg, type(arg), arg == type(arg))
    idGuild = int(ctx.guild.id)
    #cancion = queue[idGuild][queueIndex[idGuild]][0]
    if isInVc[idGuild] == None:
        await ctx.send(ctx.author.mention,embed=MensajeBasico("No se pudo skipear :nerd: ",f"{ctx.author.mention} El bulloso Necesita estar en un canal de voz para usar ester comando!",DARK_RED), silent=True)
    elif queueIndex[idGuild] >= len(queue[idGuild]) - 1:
        await ctx.send(embed=MensajeBasico("Saltando la cancion :face_with_diagonal_mouth: ","No hay mas canciones en la cola de reproducion\n\n\tQuitando La cancion",DARK_BLUE), silent=True)
        isInVc[idGuild].stop()
        await siguienteCancion(ctx)
        #await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))
    elif not arg:
        if isInVc[idGuild] != None and isInVc[idGuild]:
            isInVc[idGuild].pause()
            queueIndex[idGuild] += 1
            await reproducir(ctx)
    else:
        if int(arg) > len(queue[idGuild]):
            await ctx.send(embed=MensajeBasico("No hay canciones en la cola! :dizzy_face:",f"No puede saltar mas canciones de las que hay en la cola\nCanciones en cola: {len(queue[idGuild])}",DARK_PURPLE), silent=True)
        else:
            if isInVc[idGuild] != None and isInVc[idGuild]:
                isInVc[idGuild].pause()
                queueIndex[idGuild] += int(arg)
                await reproducir(ctx)

@elBulloso.command(
    name="previus",
    aliases=["pr"],
    help="Commando para volver una cancion en la cola de reproducion"
)
async def previus(ctx):
    idGuild = int(ctx.guild.id)
    #cancion = queue[idGuild][queueIndex[idGuild]][0]
    if isInVc[idGuild] == None:
        await ctx.send(embed=MensajeBasico("Suaga ahi sog :face_with_diagonal_mouth:",f"{ctx.author} Necesita estar en un canal de voz para usar ester comando!",DARK_RED),silent=True)
    elif queueIndex[idGuild] <= 0:
        await ctx.send(embed=MensajeBasico("No hay cancion anterior :open_mouth: ","No hay cancion anterior en la cola de reproducion\nVolviendo a reproducir la cancion actual", DARK_RED), silent=True)
        isInVc[idGuild].pause()
        await reproducir(ctx)
        #await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))
    elif isInVc[idGuild] != None and isInVc[idGuild]:
        isInVc[idGuild].pause()
        queueIndex[idGuild] -= 1
        await reproducir(ctx)

async def siguienteCancion(ctx):
    #print("\nEntro a siguiente cancion")
    idGuild = int(ctx.guild.id)
    if not isPlaying[idGuild]:
        return
    if queueIndex[idGuild] + 1 < len(queue[idGuild]):
        isPlaying[idGuild] = True
        queueIndex[idGuild] += 1

        cancion = queue[idGuild][queueIndex[idGuild]][0]
        await mensaje(ctx, cancion)
        #print("anted de await ctx.send en linea 267")
        #await ctx.send(embed= embed_Reproduciendo_Ahora(ctx, cancion))
        #print(f"Source: {cancion['Source']}")
        source = discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS)
        isInVc[idGuild].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(siguienteCancion(ctx), elBulloso.loop))
        isInVc[idGuild].source = discord.PCMVolumeTransformer(isInVc[idGuild].source, 0.5)
    else:
        queueIndex[idGuild] += 1
        isPlaying[idGuild] = False
        

#Funcion para reproducir la musica
async def reproducir(ctx):
    idGuild = int(ctx.guild.id)
    #print(f'entro a reproducir queIndex: {queueIndex[idGuild]} queue: {len(queue[idGuild])}')
    if queueIndex[idGuild] < len(queue[idGuild]):
        isPlaying[idGuild] = True
        isPaused[idGuild] = False

        #print(f"Estado is playing: {isPlaying[idGuild]} ")

        await conectarse(ctx, queue[idGuild][queueIndex[idGuild]][1])

        cancion = queue[idGuild][queueIndex[idGuild]][0]
        await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion), silent=True)
        source = discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS)
        isInVc[idGuild].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(siguienteCancion(ctx), elBulloso.loop))
        #print(f"Source: {cancion['Source']}")
        #isInVc[idGuild].play(discord.FFmpegPCMAudio(
        #    cancion['Source']), after=lambda e: siguienteCancion(ctx)
        #)
        isInVc[idGuild].source = discord.PCMVolumeTransformer(isInVc[idGuild].source, 0.5)
        #print("Antes de siguente cancion")
    else:
        await ctx.send(embed=MensajeBasico("Cola Vacia! :melting_face: ","No hay mas canciones en la cola de reproduccion",DARK_PURPLE), silent=True)
        queueIndex[idGuild] += 1
        isPlaying[idGuild] = False

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
            colour=VERDE
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        await ctx.send(embed=em, silent=True)
        if isInVc[idGuild] == None:
            await ctx.send(embed=MensajeBasico("A lo bien :middle_finger:","No me pude conectar al canal de voz\nDebe estar en un canal de Voz",ROJO))
            return
    else:
        await isInVc[idGuild].move_to(channel)

@elBulloso.command(
        name="usuarios",
        help="Este comando muestra la lista de usuarios que ve el bot."
)
async def usuarios(ctx):
    usuarios = list(elBulloso.users)
    for user in usuarios:
        await ctx.send(user, silent=True)

@elBulloso.command(
        name="sebax",
        help="Comando para mencionar a sebax ._.",
        brief="Comando para mencionar a sebax",
        description="Comando para mencionar a sebax ._."
) #No sirve, al parecer la property mention no tiene setter, ._.
async def sebax(ctx):
    objetoUser = None
    for m in ctx.guild.members:
        if 'sebaxsus' == m.name:
            objetoUser = m
    await ctx.send(f'{objetoUser.mention}, Id: {objetoUser.id} Nombre: {objetoUser.global_name}')

#client.guild.get_member_named('nombre') me busca el primer nombre mas cercano a eso sin id y sin na :/
    
#commands.command es una simplificacion del metodo (commandtree) de discord.py
#Lo que hace es guardar y mostrar una breve descricion del comando al momendo de escribir el comando en discord
discord.app_commands.autocomplete()


#Comando para unir al bot al canal de voz del usuario
@elBulloso.command(
    name="unirse",
    aliases=["u","U","UNIRSE"],
    help="Comando usado para unir al bot al canal de voz actual"
)
async def unirse(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await conectarse(ctx, channel)
    else:
        await ctx.send(embed=MensajeBasico("Sea serio pa! :clown: ",f'Tiene que estar en un canal de voz para unirme.',ROJO))

# @elBulloso.command(
#         name="salir",
#         aliases=["q","Q","SALIR"],
#         help="Comando usado para desconectar el bot del canal de voz actual.\nEsto eliminara la cola de reproduccion actual."
# )
@elBulloso.command(
    name="salir",
    description="Comando usado para desconectar el bot del canal de voz actual.\nEsto eliminara la cola de reproduccion actual."
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


async def agregarPlaylistYT(ctx, url, channel):
    cancion = None
    opciones = {
        'quit': True,
        'extract_flat': True,
        'playlistend': 50,
        'noplaylist': False,
        'format': 'bestaudio/best',
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)

    idGuild = int(ctx.guild.id)
    for entry in info['entries']:
        cancion = await asyncio.to_thread(getStream, entry['url'])
        queue[idGuild].append([cancion, channel])

        if not isPlaying[idGuild]:
            await reproducir(ctx)
        else:
            await ctx.send(embed=embed_Añadido_Queue(ctx, cancion), silent=True)
    return cancion


@elBulloso.command(name="play",
        aliases=["p","P","PLAY"],
        help="Comando para buscar en youtube una cancion con el nombre de la cancion",
        usage="$p link",
        description='Comando que ejecuta exlusivamente links o nombres de una cancion'
)
async def play(ctx, *args):
    search = " ".join(args)
    idGuild = int(ctx.guild.id)
    #print(type(search), search, search.replace(" ", ""))
    try:
        channel = ctx.author.voice.channel
        await conectarse(ctx, channel)
    except:
        em = discord.Embed(
            title=f"No me pude conectar",
            description=f"Para conectarme debe estar en un canal de voz",
            colour=0xdf1141
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        await ctx.send(ctx.author.mention,embed=em)
        return
    if not args:
        if len(queue[idGuild]) == 0:
            await ctx.send(embed=MensajeBasico("Cola Vacia! :face_with_monocle: ","No hay canciones en la cola\n\nIngrese un link o una cancion para buscarla", DARK_RED), silent=True)
            return
        elif not isPlaying[idGuild]:
            if queue[idGuild] == None or isInVc[idGuild] == None:
                print("Entro no hay queue o esta en vc es igual a none")
                #isPlaying[idGuild] = False       Si se da;a algo activar esto
                await reproducir(ctx)
            else:
                print("Entro else not args play")
                isPaused[idGuild] = False
                isPlaying[idGuild] = True
                isInVc[idGuild].resume()
        else:
            return
    else:
        #esplaylist = esPlaylistYT(search)
        print(search)
        # if search.startswith("https://www.youtube.com/playlist?list=") == True:
        #     cancion = await agregarPlaylistYT(ctx, search, channel)
        if search.startswith("https://open.spotify.com/") == True:
            # verificarTokenSpotify()
            search = search.split('?')[0]     
            #La unica solucion seria poner la busqueda de pl en un segundo subproceso no hay mas manera
            if search.startswith('https://open.spotify.com/playlist/') == True:
                #print("Loop antes de empezar la busqueda sp ", asyncio.get_running_loop(), " ", asyncio.get_event_loop())
                #print('entro a playlist')
                #cancion = asyncio.run_coroutine_threadsafe(busquedaPlaylist(ctx, channel, search), elBulloso.loop)
                #asyncio.run_coroutine_threadsafe(busquedaPlaylist(ctx, channel, search), elBulloso.loop)
                #cancion = None
                #asyncio.threads.to_thread(busquedaPlaylist(ctx, channel, search))
                #print("Loop despues de busqueda sp ", asyncio.get_running_loop(), " ", asyncio.get_event_loop())
                cancion = await busquedaPlaylist(ctx, channel, search)
                # print("Spotify playlis, termino la cancion ", cancion['Titulo'])
            else:
                search = search.removeprefix('https://open.spotify.com/intl-es/track/')

                cancion = await asyncio.to_thread(buscar, nombreArtiCancionPlaylistTrack(cliente.track(search)))            
        elif esUrl(search) == True:
            cancion = await asyncio.to_thread(getStream, search)
        else:
            cancion = await asyncio.to_thread(buscar, search)

        if isinstance(cancion, bool):
            await ctx.send(embed=MensajeBasico("Uy cual es esa :rage: ",f"Que mierda buscate sapa {ctx.author.mention}", ROJO), silent=True)
            return
        else:
            queue[idGuild].append([cancion, channel])

            if not isPlaying[idGuild]:
                await reproducir(ctx)
            else:
                await ctx.send(embed=embed_Añadido_Queue(ctx, cancion), silent=True)
    voice = ctx.author.voice

    if not voice:
        await ctx.send(embed=MensajeBasico("A lo bien :middle_finger:","No me pude conectar al canal de voz\nDebe estar en un canal de Voz",ROJO), silent=True)
        return

    # vc = await voice.channel.connect()

    
    
    # await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion=audio_info), silent=True)

    # source = discord.FFmpegPCMAudio(audio_info['url'], **FFMPEG_OPTIONS)

    # vc.play(source, after=lambda e: print('Reproducción terminada', e))


@elBulloso.command(
        name="spotify",
        aliases=["sp", "SP", "SPOTIFY"],
        help="Comando para probar musica por sporify",
        usage="$sp link",
        description='Comando que ejecuta exlusivamente links de spotify'
)
async def spotify(ctx, args):
    search = args
    search = search.split('?')[0]
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
            await ctx.send(embed=MensajeBasico("No hay canciones en la cola!","La cola de reproducion esta actualmente Vacia", ROJO))
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
        if search.startswith('https://open.spotify.com/playlist/') == True:
            await busquedaPlaylist(ctx, channel, search)
        else:
            search = search.removeprefix('https://open.spotify.com/intl-es/track/')
            try:
                cancion = getStream(buscar(nombreArtiCancionPlaylistTrack(cliente.track(search))))

                queue[idGuild].append([cancion, channel])

                if not isPlaying[idGuild]:
                    await reproducir(ctx)
                else:
                    await ctx.send(embed=embed_Añadido_Queue(ctx, cancion), silent=True)
            except Exception as e:
                await ctx.send(embed=MensajeBasico("El Token de Spotify Expiro 😶‍🌫️", ROJO))



@elBulloso.event
async def on_ready():
    # try:
    # #   print(token)
    #     cliente = spotipy.Spotify(auth=token)
    #     user_name = cliente.current_user() 
    # except:
    #     print("Fallo token SpotiPy")
    # else:
    #     #print(json.dumps(user_name, sort_keys=True, indent=4))
    #     #print(f'token: {token}')
    #     print('token correcto Spotipy')

    cliente = spotipy.Spotify(auth_manager=auth_manager)

    try:
        #print(token)
        user_name = cliente.current_user() 
    except:
        print("Fallo token")
    else:
        #print(json.dumps(user_name, sort_keys=True, indent=4))
        #print(f'token: {token}')
        print('token correcto SpotiPy')
    
    #members = elBulloso.get_all_members() #Obtiene todos los usuarios que ve el bot y los guarda en members
    for guild in elBulloso.guilds:
        idGuild = int(guild.id)
        queue[idGuild] = []
        queueIndex[idGuild] = 0
        isInVc[idGuild] = None
        isPlaying[idGuild] = False
        isPaused[idGuild] = False
    #print(elBulloso.user.mention)
    await elBulloso.tree.sync()
    print(f'Inicializando como {elBulloso.user}, SpotifyUsr: {user_name['display_name']}')

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

elBulloso.run(tokenBot)