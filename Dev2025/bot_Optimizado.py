import discord 
from discord import app_commands
from discord.ext import commands

import spotipy, yt_dlp, asyncio, functools, datetime, concurrent.futures

import discord.ext
from modules.utils import esUrl
from modules.yt_wrapper import buscar_metadatos, buscar, obtener_stream, shutdown_executor
from settings import DISCORD_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Para controlar los tiempos del cache
import time, datetime

## Piscina de Hilos contralados (Yo defino el maximo de hilos)

thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)

# Archivo txt para guardar log de testing
# archivo_test = open("test.txt", "a")

# archivo_test.write(f"\nTest Ejecutado el: {datetime.datetime.now()}\n")



SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/authorize"

# env = dotenv.dotenv_values(pathlib.Path(__file__).parent / ".env")
spClientId=SPOTIFY_CLIENT_ID
spClientSecret=SPOTIFY_CLIENT_SECRET
# spApi = "https://api.spotify.com/v1/"
# spEndPoint = "/track/{track_id}"
# spURI = 'http://localhost:3000'
spUricall = 'https://127.0.0.1:5000/callback/'
tokenBot = DISCORD_TOKEN

scope = """ugc-image-upload,user-read-playback-state,user-modify-playback-state,user-read-currently-playing,
app-remote-control,streaming,playlist-read-private,playlist-modify-public,playlist-read-collaborative,user-read-email,user-read-private
"""

auth_manager = spotipy.oauth2.SpotifyPKCE(
    client_id=spClientId,
    redirect_uri=spUricall,
    scope=scope,
    # open_browser=False
)
# Para generar la url manual y luego obtener el token manual todo por consola se usa
# el parametro open_browser=False en auth_manger
# y auth_manager.get_authorize_url()
# print("Open web: ", auth_manager.get_authorize_url())
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
# Estos colores son en formato hexadecimal, se pueden cambiar a gusto
# Pero python los interpreta como enteros, por lo que no se pueden usar comillas


#El intents es indispensable, Se usa para que el bot y la libreria obtenga informacion de
#La api de discord con permisos, Los permiosos son los intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.all()
intents = discord.Intents.all()

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

# Diccionario Global para manejar las deconciones manuales (Por codigo) y diferenciarlas de las desconexiones por errores (WebSocket closed with 1006)
desconectado_por_codigo = {}
ctx_por_guild = {}
# Diccionario global
autocomplete_cache = {}

CACHE_TTL = 20  # tiempo en segundos para considerar válida una entrada

#Constant for ytdl_Youtube and FFMPEG
#YTDL_OPTIONS = {'format': 'bestaudio', 'nonplaylist': 'True'}
#FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ydl_options = {
    'format': 'bestaudio/best', # Selecciono el mejor formato de audio disponible
    'quiet': True, # Silencia el log de yt_dlp
    'no_warnings': True, # Silencia las advertencias en consola de yt_dlp
    'skip_download': True, # No descarga el archivo
    'default_search': 'ytsearch1',# Limita la busqueda a un resultado
    'extract_flat': False,
    'noplaylist': True,
    'nocheckcertificate': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn',
    }

def verificarTokenSpotify() -> None:
    """
    - Verifica si el token de spotify ha expirado, si es asi lo renueva
    - Si el token no ha expirado, no hace nada.
    - Si el token no es valido, lanza una excepcion y no hace nada.
    - Si el token es valido, lo guarda en la variable global token.

    ---------------------

    **Parameters:**
        **None**

    ---------------------

    **Returns:**
        **None**

    [Mas info sobre el token de spotify](https://spotipy.readthedocs.io/en/2.22.1/#spotipy.oauth2.SpotifyPKCE)
    [Mas info sobre el flujo del token de spotify](https://developer.spotify.com/documentation/general/guides/authorization-guide/)
    [Mas info sobre el flujo de autorizacion del token de spotify](https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow)
    [Mas info sobre el flujo de autorizacion del token de spotify](https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow-with-proof-key-for-code-exchange-pkce)
    """
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

def MensajeBasico(titulo: str, texto: str, color: int) -> discord.Embed:
    """
    - Crea un mensaje embed basico para enviar al canal de discord
    
    ---------------------
    **Parameters:**
        **titulo:** `(str)`
        **texto:** `(str)`
        **color:** `(int)`
        **icon_Url:** `(str) | url de la foto de perfil del bot`
        
    ---------------------
    
    **Returns**
        `discord.embeds.Embed`
    
    [Mas info sobre discord.Embed](https://discordpy.readthedocs.io/en/stable/api.html#discord.Embed)
    [Mas info sobre los hexadecimales](https://www.w3schools.com/python/python_strings_methods.asp)
    """
    em = discord.Embed(
            title=titulo,
            description=texto,
            colour=color
        )
    em.set_footer(icon_url=elBulloso.user.display_avatar)
    return em

# def buscar_metadatos(query: str) -> dict:
#     opciones = {
#         'quiet': True,
#         'skip_download': True,
#         'extract_flat': True, # La diferencia entre False y true es Abismal en True se demora en promedio 0.5seg y en false se demora en promedio 7 seg
#         'nocheckcertificate': True,
#     }

#     with yt_dlp.YoutubeDL(opciones) as ydl:
#         info = ydl.extract_info(f"ytsearch1:{query}", download=False)
#         # print(f"Probando entries {info['entries'][0]}")
#         video = info['entries'][0]
#         # print("\n\nResultado Metadata: ", video, "\n\n\n")
#         return {
#             'Titulo': video.get('title'),
#             'link': video.get('url') or f"https://www.youtube.com/watch?v={video.get('id')}",
#             'streamUrl': None,
#             'Canal': video.get("uploader"),
#             'Duracion': format_audio_seconds(info.get('duration')), # Devuelve el tiempo de duracion ya formateado
#             'Miniatura': f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig",
#         }

# def obtener_stream(url: str) -> dict:
#     print(f"Entro obtener Stream... url:{url}")
#     start = time.time()
#     opciones = {
#         'quiet': True,
#         'skip_download': True,
#         'format': 'bestaudio/best',
#         'extract_flat': False,
#         'default_search': 'ytsearch1',
#         'nocheckcertificate': True,
#     }

#     with yt_dlp.YoutubeDL(opciones) as ydl:
#         info = ydl.extract_info(url, download=False)
#         video = info['entries'][0] if 'entries' in info else info
#         cancion = {
#             'Titulo': video.get('title'),
#             'link': video['webpage_url'],
#             'streamUrl': video['url'],
#             'Canal': video.get('uploader'),
#             'Duracion': video.get('duration_string'), # Devuelve el tiempo de duracion ya formateado
#             'Miniatura': video['thumbnail'],
#         }
#         # print("Termino buscar stream, tiempo de ejecucion: ", time.time() - start)
#         archivo_test.write(f"\tTest func obtener_stream optimizado Tiemo de Ejecucion: {time.time() - start}\n")
#         return cancion

async def procesarBloqueStream(idGuild: int, bloque: list) -> list:
    """
    - Procesa un bloque de canciones para obtener el streamUrl de cada cancion
    en un bloque de 5 canciones dentro de un proceso asincrono alterno para evitar
    que la busqueda consuma los recursos del proceso principal (bot) y no genere un GIL (Global Interpreter Lock),
    si la cancion ya tiene el streamUrl se agrega a una lista de canciones validas,
    si no tiene el streamUrl se agrega a una lista de canciones removidas, 
    si se obtiene el streamUrl se agrega a una lista de canciones validas, 
    al final devuelve la lista de canciones validas.

    ----------------------------

    **Parameters:**
        **idGuild:** `(int)`,
        **bloque:** `(list)`

    ----------------------------

    **Returns:**
        **`(list):`**
            - **canciones_validas**: Lista de canciones con streamUrl obtenida.

    [Mas info sobre asyncio](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)
    [Mas info sobre el GIL](https://realpython.com/python-concurrency/)
    [Mas info sobre el GIL y el ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)
    [Mas info sobre el GIL y el asyncio](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task)
    [Mas info sobre el GIL y el asyncio.gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)
    [Mas info sobre el GIL y el asyncio.run](https://docs.python.org/3/library/asyncio-task.html#asyncio.run)
    """
    canciones_validas = []
    removidas = []

    for cancion, channel in bloque:
        if not cancion.get('stream_url'):
            try:
                nueva_cancion = await obtener_stream(cancion['link'])
                if nueva_cancion['streamUrl']:
                    canciones_validas.append([nueva_cancion, channel])
                    print(f"✅ Stream URL obtenida: {nueva_cancion['Titulo']}")
                else:
                    removidas.append(cancion['Titulo'])
            except Exception as e:
                print(f"❌ Error obteniendo stream de '{cancion['Titulo']}': {e}")
                removidas.append(cancion['Titulo'])
        else:
            canciones_validas.append([cancion, channel])

    if removidas:
        print(f"⚠️ Canciones eliminadas en este bloque: {', '.join(removidas)}")

    return canciones_validas

async def guardarStreamUrls(idGuild: int) -> dict|None:
    """
    - Recorre las cola de reproduccion de una guild en especifico
    para dividir sus canciones en bloques de **5** canciones,
    Cada uno de estos bloques se procesaran de manera asincrona y paralela
    para obtener el streamUrl de cada cancion, luego se guardaran
    en la cola de reproduccion y se reemplazara la cola de reproduccion
    de la guild con la nueva lista de canciones.

    ----------------------------

    **Parameters:**
        **idGuild:** `(int)`

    ----------------------------

    **Returns:**
        **`(dict):`**
            - **Titulo `(str)`**: Titulo del video.
            - **link `(str)`:** Url/Link del video.
            - **streamUrl `(str)`:** Url/Link del stream de bits.
            - **Canal `(str)`:** Nombre de usuario del canal que subio el video.
            - **Duracion `(str)`:** Duracion del video formateado en `MM:SS`.
            - **Miniatura `(str)`:** Url/Link de la minuatura del video.
    """
    bloques = [queue[idGuild][i:i + 5] for i in range(0, len(queue[idGuild]), 5)]
    tareas = []

    for bloque in bloques:
        # print("BloqueQUeue: ", bloque, "\n\n\n")
        tarea = asyncio.create_task(procesarBloqueStream(idGuild, bloque))
        tareas.append(tarea)

    resultados = await asyncio.gather(*tareas)

    canciones_finales = []
    for resultado in resultados:
        canciones_finales.extend(resultado)  # Cada resultado es una lista de [cancion, channel]

    queue[idGuild] = canciones_finales  # reemplaza cola completa con las válidas
    # print(f"\n\nLista cancionesFinales de guardarStreamURL: {canciones_finales}\n\n")
    if canciones_finales:
        return canciones_finales[-1][0]
    else:
        return None


def nombreArtiCancionPlaylistTrack(datosTrack: dict) -> str:
    """
    - Recibe un objeto con todos los metadatos de una cancion
    dentro de una playlist o album y obtiene los nombres de todos
    sus artistas y el nombre de la cancion

    ----------------------------

    **Parameters:**
        **datosTrack:** `(dict)`

    ----------------------------

    **Returns:**
        **`(str):`**
            "Titulo - Artistas"
    """
    # print("entro nombrarArticacnionPlaylistTrac")
    artistaN = ""
    artistas = datosTrack['artists']
    cancion = datosTrack['name']
    for i in range(0, len(artistas), 1):
        artistaN += artistas[i]['name'] + " "

    return f"{cancion} - {artistaN}"

async def guardarCancionesSpList(datos: list, idGuild: int, channel: discord.VoiceChannel) -> dict:
    """
    - Obtiene los metadatos de todas las canciones de una playlist de spotify,
    luego les saca los metadatos necesarios y por ultimo guarda cada cancion
    en la cola de reproduccion.

    ----------------------------

    **Parameters:**
        **datos:** `(list)`,
        **idGuild:** `(int)`,
        **channel:** `(class discord.VoiceChannel)`
    
    ----------------------------

    **Returns:**
        **`(dict):`**
            - **Titulo `(str)`**: Titulo del video.
            - **link `(str)`:** Url/Link del video.
            - **streamUrl `(str)`:** Url/Link del stream de bits.
            - **Canal `(str)`:** Nombre de usuario del canal que subio el video.
            - **Duracion `(str)`:** Duracion del video formateado en `MM:SS`.
            - **Miniatura `(str)`:** Url/Link de la minuatura del video.

    [Info sobre la lib de spotify](https://spotipy.readthedocs.io/en/2.22.1/)
    """
    # print("Entro guardarCancionesSpList ")
    # Datos es una lista que contiene todas las canciones de la Playlist
    # Dentro, es decir que su length es la cantidad de canciones dentro de la lista
    cancion = None
    for i, track in enumerate(datos):
        # start = time.time()
        datosTrack = track['track']
        if datosTrack is None:
            pass
        else:
            strCancion = nombreArtiCancionPlaylistTrack((datosTrack))
            cancion = await buscar_metadatos(strCancion)
            # try:
            #     cancion = buscar(strCancion)
            # except Exception as e:
            #     print("Fallo el buscar la track de Spotify")
            #     return

            queue[idGuild].append([cancion, channel])
            # archivo_test.write(f"\tTest Funcion guardarCancionesSpList optimizado .to_thread Iteracion:{i} - Tiemo de Ejecucion: {time.time() - start}\n")
            # print(f"Cancion {i}: {cancion['Titulo']} \n\tTiemo de Ejecucion: {time.time() - start}" )

    return cancion

async def guardaCancionesSpAlbum(datos: list, idGuild: int, channel: discord.VoiceChannel) -> dict:
    """
    - Obtiene los metadatos de todas las canciones de un album de spotify,
    luego les saca los metadatos necesarios y por ultimo guarda cada cancion
    en la cola de reproduccion.

    ----------------------------

    **Parameters:**
        **datos:** `(list)`,
        **idGuild:** `(int)`,
        **channel:** `(class discord.VoiceChannel)`
    
    ----------------------------

    **Returns:**
        **`(dict):`**
            - **Titulo `(str)`**: Titulo del video.
            - **link `(str)`:** Url/Link del video.
            - **streamUrl `(str)`:** Url/Link del stream de bits.
            - **Canal `(str)`:** Nombre de usuario del canal que subio el video.
            - **Duracion `(str)`:** Duracion del video formateado en `MM:SS`.
            - **Miniatura `(str)`:** Url/Link de la minuatura del video.

    [Info sobre la lib de spotify](https://spotipy.readthedocs.io/en/2.22.1/)
    """
    # print("entro guardaCancionesSpAlbum ")
    # Datos es una lista que contiene todas las canciones de la Playlist
    # Dentro, es decir que su length es la cantidad de canciones dentro de la lista
    cancion = None
    for i, track in enumerate(datos):
        # start = time.time()
        strCancion = nombreArtiCancionPlaylistTrack((track))
        cancion = await buscar_metadatos(strCancion)
        # try:
        #     cancion = buscar(strCancion)
        # except Exception as e:
        #     print("Fallo el buscar la track de Spotify")
        #     return

        queue[idGuild].append([cancion, channel])
        # print(f"Cancion {i}: {cancion['Titulo']} \n\tTiemo de Ejecucion: {time.time() - start}" )

    return cancion

async def busquedaPlaylist(ctx: commands.Context, channel: discord.VoiceChannel, urlPlaylist: tuple[str, str]) -> dict:
    """
    - Busca los metadatos de todas las canciones en una playlist de spotify
    dividiendo la carga de busqueda en bloques de **5** canciones, Cada bloque
    se manda a una funcion asincrona (Corutina) resolviendo primero el primer bloque para
    reproducir las primeras canciones apenas esten disponibles para no dejar el bot
    pensando mientras busca los metadatos de cada cancion,

    - Luego de completar el primer bloque creo una lista de tareas asincrona (Lista de corutinas)
    que se encargara de resolver los bloques de canciones restantes de manera asincrona y paralela,

    - Cuando se complete la lista de tareas asincronas (Corutinas) llamo otra funcion que se encargara
    de obtener la url de stream de bits de cada cancion dentro de las canciones en la cola de reproduccion,

    - Por ultimo devolvera los metadatos de la ultima cancion en cola con su streamUrl ya obtenida.
    
    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **channel:** `(class discord.VoiceChannel)`,
        **urlPlaylist:** `(tuple[str, str])` | [0]: tipo_de_url, [1]: url.

    ----------------------------

    **Returns:**
        `**(dict):**`
         - **Titulo `(str)`:** Titulo del video.
         - **link `(str)`:** Url/Link del video.
         - **streamUrl `(str)`:** Url/Link del stream de bits.
         - **Canal `(str)`:** Nombre de usuario del canal que subio el video.
         - **Duracion `(str)`:** Duracion del video formateado en `MM:SS`.
         - **Miniatura `(str)`:** Url/Link de la minuatura del video.

    [Info sobre la lib de spotify](https://spotipy.readthedocs.io/en/2.22.1/)
    """
    start = time.time()
    # print("Entro busqueda playlist SP")
    idGuild = int(ctx.guild.id)

    # strCancion = ""
    # cancion = None
    #Datos es la cantidad de canciones que contiene la playlist
    # ciclosDatosCancion = divmod(len(datos), 5)
    # Mod, restante
    # print("Pre-search Sp: ", urlPlaylist[1])
    datos = cliente.playlist(urlPlaylist[1])['tracks']['items']
    # print(f"Datos Raw sp, {datos['tracks']['items']['artists']}, {datos['tracks']['items']['name']}")
    
    # Bloque de varias tareas
    bloques = [datos[i:i + 5] for i in range(0, len(datos), 5)]

    #Tareas nose
    tareas = []

    primer_bloque = bloques[0]
    await guardarCancionesSpList(primer_bloque, idGuild, channel)

    #Espero a que se resuelva el primero bloque
    #await elBulloso.loop.run_in_executor(None, func=func)
    #await asyncio.to_thread(func)
    # await elBulloso.bot_loop.run_in_executor(thread_pool, func)
    # Reproducir primera cancion en el diccionario queue (cola)
    # Si no se esta reproduciendo ninguna cancion
    if not isPlaying[idGuild]:
        await reproducir(ctx)

    #Leer recurso para entender esto Link https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
    for bloque in bloques[1:]:
        tarea = asyncio.create_task(guardarCancionesSpList(bloque, idGuild, channel))
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

        #func = functools.partial(guardarCancionesSpList, bloque, idGuild, channel)
        # El bloque de tareas que se va a guardar en la lista de bloques de tareas
        #tarea = elBulloso.bot_loop.run_in_executor(thread_pool, func)
        # Agregando el bloque de tareas a la lista de bloques de tareas
        tareas.append(tarea)

    # Espero a que todas las tareas terminen
    await asyncio.gather(*tareas)
    # print(f"Termino el buscar Playlist track Metadatos, Tiempo de Ejecucion: {time.time() - start}")
    # archivo_test.write(f"Test Func Busqueda_PlaylistTracks_Metadatos optimizado, Tiempo de Ejecucion: {time.time() - start}\n")

    start = time.time()

    ultima_Cancion = await guardarStreamUrls(idGuild)

    # print(f"Termino el buscar los streamUrl, Tiempo de Ejecucion: {time.time() - start}")
    # archivo_test.write(f"Test func guardarStreamURL optimizado, Tiempo de EjecucionL {time.time() - start}\n")

    # Devuelvo el ultimo resultado guardado en el ultimo bloque de tareas resuelto
    if not ultima_Cancion:
        await ctx.send(embed=MensajeBasico("❌ Error", "No se pudo obtener ninguna canción válida del playlist", ROJO))
        return
    else:
        return ultima_Cancion

async def busquedaAlbum(ctx: commands.Context, channel: discord.VoiceChannel, urlPlaylist: tuple[str, str]) -> dict:
    """
    - Busca los metadatos de todas las canciones en un album de spotify
    dividiendo la carga de busqueda en bloques de **5** canciones, Cada bloque
    se manda a una funcion asincrona (Corutina) resolviendo primero el primer bloque para
    reproducir las primeras canciones apenas esten disponibles para no dejar el bot
    pensando mientras busca los metadatos de cada cancion,

    - Luego de completar el primer bloque creo una lista de tareas asincrona (Lista de corutinas)
    que se encargara de resolver los bloques de canciones restantes de manera asincrona y paralela,

    - Cuando se complete la lista de tareas asincronas (Corutinas) llamo otra funcion que se encargara
    de obtener la url de stream de bits de cada cancion dentro de las canciones en la cola de reproduccion,

    - Por ultimo devolvera los metadatos de la ultima cancion en cola con su streamUrl ya obtenida.
    
    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **channel:** `(class discord.VoiceChannel)`,
        **urlPlaylist:** `(tuple[str, str])` | [0]: tipo_de_url, [1]: url.

    ----------------------------

    **Returns:**
        `**(dict):**`
         - **Titulo `(str)`:** Titulo del video.
         - **link `(str)`:** Url/Link del video.
         - **streamUrl `(str)`:** Url/Link del stream de bits.
         - **Canal `(str)`:** Nombre de usuario del canal que subio el video.
         - **Duracion `(str)`:** Duracion del video formateado en `MM:SS`.
         - **Miniatura `(str)`:** Url/Link de la minuatura del video.

    [Info sobre la lib de spotify](https://spotipy.readthedocs.io/en/2.22.1/)
    """
    # print("Entro busqueda album")
    idGuild = int(ctx.guild.id)

    datos = cliente.album(urlPlaylist[1])['tracks']['items']
    
    # Bloque de varias tareas
    bloques = [datos[i:i + 5] for i in range(0, len(datos), 5)]

    #Tareas nose
    tareas = []

    primer_bloque = bloques[0]
    await guardaCancionesSpAlbum(primer_bloque, idGuild, channel)

    # Reproducir primera cancion en el diccionario queue (cola)
    # Si no se esta reproduciendo ninguna cancion
    if not isPlaying[idGuild]:
        await reproducir(ctx)

    #Leer recurso para entender esto Link https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
    for bloque in bloques[1:]:

        # El bloque de tareas que se va a guardar en la lista de bloques de tareas
        tarea = asyncio.create_task(guardaCancionesSpAlbum(bloque, idGuild, channel))

        # Agregando el bloque de tareas a la lista de bloques de tareas
        tareas.append(tarea)
    # Espero a que todas las tareas terminen
    await asyncio.gather(*tareas)

    ultima_Cancion = await guardarStreamUrls(idGuild)

    # Devuelvo el ultimo resultado guardado en el ultimo bloque de tareas resuelto
    if not ultima_Cancion:
        await ctx.send(embed=MensajeBasico("❌ Error", "No se pudo obtener ninguna canción válida del playlist", ROJO))
        return
    else:
        return ultima_Cancion

# def buscar(search):
#     print("Buscando... ", search)
#     start = time.time()
#     with yt_dlp.YoutubeDL(ydl_options) as ydl:
#         # search_results = []
#         info = ydl.extract_info(f"ytsearch1:{search}", download=False)
#         entries = info['entries'][0]
#         # print(f"Termino Buscando {search}\n Tiempo: {time.time() - start}")
#         archivo_test.write(f"Test func Buscando {search} Optimizado ytsearch1 Tiempo: {time.time() - start}\n")
#         return {
#             'Titulo': entries.get('title'),
#             'link': f"https://www.youtube.com/watch?v={entries.get('id')}",
#             'streamUrl': entries.get('url'),
#             'Canal': entries.get('uploader'),
#             'Duracion': entries.get('duration_string'), # Devuelve el tiempo de duracion ya formateado
#             'Miniatura': entries['thumbnail'],
#         }
        # for entry_info in info['entries']:
        #     title = entry_info.get("title", "Sin titulo")
        #     duration = entry_info.get("duration",0)
        #     search_results.append(entry_info)

def getStream(url: str) -> dict:
    """
    - Obtiene la url del stream de bits usando una\n
     url de un video en Youtube,
    - Devuelve un diccionario con los metadatos del video y\n
     la url del stream de bits.

    ----------------------------

    **Parameters:**
        **url:** `(str)`
    
    ----------------------------

    **Returns:**
        `**(dict):**`
         - **Titulo `(str)`**: Titulo del video.
         - **link `(str)`:** Url/Link del video.
         - **streamUrl `(str)`:** Url/Link del stream de bits.
         - **Canal `(str)`:** Nombre de usuario del canal que subio el video.
         - **Duracion `(str)`:** Duracion del video formateado en `MM:SS`.
         - **Miniatura `(str)`:** Url/Link de la minuatura del video.

    [Mas info sobre la lib de scrapping yt](https://github.com/yt-dlp/yt-dlp#readme)
    """
    print("Entro get stream, url: ", url)
    start = time.time()
    with yt_dlp.YoutubeDL(ydl_options) as ydl:

        info = ydl.extract_info(url, download=False)
        # archivo_test.write(f"Test Func getStream sin optimizar, Tiempo de Ejecucion: {time.time() - start}\n")
        return {
            'Titulo': info.get('title'),
            'link': f"https://www.youtube.com/watch?v={info.get('id')}",
            'streamUrl': info.get('url'),
            'Canal': info.get('uploader'),
            'Duracion': info.get('duration_string'),
            'Miniatura': info['thumbnail']
        }
    
def embed_Reproduciendo_Ahora(ctx: commands.Context, cancion: dict) -> discord.Embed:
    """
    - Devuelve un embed de la libreria discord\n
     con los metadatos de una cancion con el siguiente formato
     - Titulo `(str)`
     - descripcion `(str)`
     - colour `(str(hex))`
     - Duracion `(str)`
     - Miniatura `(str)`
     - Footer `(str)`
     - Author `(str)`
    
    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **cancion:** `(dict)`
    
    ----------------------------

    **Returns:**
        `(Embed discord.Embed)`
    """
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
        title="- **Reproduciendo:**",
        description=f'[{Titulo}]({link})',
        colour=0x2c76dd
    )
    embed.add_field(name="- **Duracion:**", value=f"""```cs\n\t{Duracion}```""")
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: **{str(usuario)}**', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

def embed_Añadido_Queue(ctx: commands.Context, cancion: dict) -> discord.Embed:
    """
    - Devuelve un embed de la libreria discord\n
     con los metadatos de una cancion con el siguiente formato
     - Titulo `(str)`
     - descripcion `(str)`
     - colour `(str(hex))`
     - Duracion `(str)`
     - Miniatura `(str)`
     - Footer `(str)`
     - Author `(str)`
    
    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **cancion:** `(dict)`
    
    ----------------------------

    **Returns:**
        `(Embed discord.Embed)`
    """
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
        title="- **Añadido a la cola:**",
        description=f'[{Titulo}]({link})',
        colour=DARK_PURPLE
    )
    embed.add_field(name="- **Duracion:**", value=f"""```cs\n\t{Duracion}```""")
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: **{str(usuario)}**', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

def embed_Eliminado_Queue(ctx: commands.Context, cancion: dict) -> discord.Embed:
    """
    - Devuelve un embed de la libreria discord\n
     con los metadatos de una cancion con el siguiente formato
     - Titulo `(str)`
     - descripcion `(str)`
     - colour `(str(hex))`
     - Duracion `(str)`
     - Miniatura `(str)`
     - Footer `(str)`
     - Author `(str)`
    
    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **cancion:** `(dict)`
    
    ----------------------------

    **Returns:**
        `(Embed discord.Embed)`
    """
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
        title="- **Eliminado de la Cola:**",
        description=f'[{Titulo}]({link})',
        colour=DARK_RED
    )
    embed.add_field(name="- **Duracion:**", value=f"""```cs\n\t{Duracion}```""")
    embed.set_thumbnail(url=miniatura)
    embed.set_footer(text=f'Cancion de: **{str(usuario)}**', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

async def mensaje(ctx: commands.Context, cancion: dict):
    """
    - Manda un mensaje de tipo embed al chat de discord\n
     con los metadatos de una cancion.

    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **cancion:** `(dict)`
    
    ----------------------------

    **Returns:**
        `Mensaje de tipo embed en discord`
    """
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
@elBulloso.hybrid_command(
    name="ping",
    description="Usa un nombre global para mencionar a un usuario.",
    aliases=["PING"],
    help="Comando para mencionar a un usuario usando su nombre global.",
)
@app_commands.describe(nombre="Nombre exacto del usuario (no el nickname)")
async def ping(ctx: commands.Context, *, nombre: str = None):
    """
    - Devuelve un mensaje mencionando a un usuario especificado

    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **nombre:** `(str)` | `*Optional*`
    
    ----------------------------

    **Returns:**
        `Mensaje en discord`

    [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    if not nombre:
        await ctx.send(f'Pong :ping_pong:')
        return
    
    #La variable user guarda un objecto que genere la funcion find de utils, En otras palbras lo que se guarda en user es un objeto no un string ni nada parecido.
    user = discord.utils.find(lambda m: m.name.lower() == nombre.lower(), ctx.channel.guild.members)
    print("Usuario ", user.name)
    #Para manejar un error y usar discord como respuesta al error se debe usar el manejador de errores de discord.ext.commands alias on_command_error() o error().
    #Tambien hay un condicional llamado check usado comunmente para verificar permisos de usuario y si puede usar comandos o no.
    if not user:
        await ctx.send(
            embed=MensajeBasico(
                "Error :scream:",
                "Usuario no encontrado",
                DARK_RED
            ),
            silent=True
        )
    
    await ctx.send(
        f"Pong {user.mention} :ping_pong:"
    )
    # else:
    #     try:
            
    #         print(f"OBjetos o string?: {user}, {user.name}, {type(user)}, {type(user.name)}, {user.id}") #Prueba
    #         #tempUserId = None
    #         #tempUserName = None
    #         tempUserObject = None
    #     except:
    #         await ctx.send(embed=MensajeBasico("Error al ejecutar $ping :scream:","Usuario No encontrado",DARK_RED), silent=True)
    #     else:
    #         for m in ctx.channel.guild.members:
    #             if user.name in m.name: #busco el usario dentro de todos los usuarios de la guild
    #                 #print(m.id, nombre)
    #                 #tempUserId = m.id
    #                 #tempUserName = m.name
    #                 tempUserObject = m
    #         await ctx.send(f'Pong {tempUserObject.mention} :ping_pong:') #con los objetos Puedo mencionar, sacarle la info del objeto (User)


@elBulloso.hybrid_command(
        name="info",
        description="Comando que devuelve informacion general del servidor",
        aliases=["INFO"],
        help = "Este comando manda un mensaje con la informacion del servidor.",
)
async def info(ctx: commands.Context):
    """
    - Muestra la informacion de la guild en donde\n
     se uso el comando

    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`

    ----------------------------

    **Returns:**
        `Mensaje de tipo embed en discord`

    [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    embed = discord.Embed(
        title=f'{ctx.guild.name}',
        description=f"La mierda mas grande jamas vista {datetime.datetime.now(datetime.timezone.utc)}",
        timestamp=datetime.datetime.utcnow(),
        color=DARK_BLUE
    )
    embed.add_field(name="Dueño del server", value=f'{ctx.guild.owner}')
    #embed.add_field(name="Region del server", value=f'{ctx.guild.region}') Segun lo visto en la documentacion el metodofo .region de Discord.guild no existe >:(
    embed.add_field(name="Id del Servidor", value=f'{ctx.guild.id}')
    if ctx.guild.icon:
        embed.set_thumbnail(url=f"{ctx.guild.icon.url}")
    embed.set_author(name="sebaxsus")
    await ctx.send(embed=embed, silent=True)

def truncar_titulo(titulo: str, max_length: int = 60) -> str:
    return titulo if len(titulo) <= max_length else titulo[:max_length - 3] + "..."

@elBulloso.hybrid_command(
    name="cola",
    description="Muestra las canciones en la cola actual",
    aliases=["c", "C", "COLA"],
    help="Commando para mostrar las canciones en la cola actual.",
)
async def cola(ctx: commands.Context):
    """
    - Revisa si hay canciones en la cola de reproduccion\n
     de la guild en donde se uso el comando y muestra una lista
     dentro de un mensaje embed con las siguientes 20 canciones
     y establece un footer con la cantidad de canciones dentro de la cola.

    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`
    
    ----------------------------

    **Returns:**
        `Mensaje de tipo embed en discord`

    [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    idGuild = int(ctx.guild.id)
    # print(f"Entro a cola de reproduccion:\n  Numero actual de la cola: {queueIndex[idGuild]}\n  Titulo Cancion actual: {queue[idGuild][queueIndex[idGuild]][0].get("Titulo")}")
    if not queue[idGuild]:
        colaEmbed = discord.Embed(
            title="🎶 Cola de Reproduccion",
            description="No hay canciones en la cola",
            colour=0x2c76dd
        )

        await ctx.send(
            embed=colaEmbed,
            silent=True
        )
        return
    
    # Si el indice actual es igual o mayor a la cantidad de canciones en la cola mande el mensaje
    if queueIndex[idGuild] >= len(queue[idGuild]) or len(queue[idGuild]) == 0:
        print(f"Provando que es cola cuando se vacia {type(queue[idGuild])} {queue[idGuild]}")
        ctx.send(
            embed=MensajeBasico(
                "🎶 Cola de Reproducción vacia! :face_with_monocle:",
                f"No hay canciones en la cola de reproduccion {len(queue[idGuild])}",
                DARK_RED
            ),
            silent=True
        )
        return
    
    colaEmbed = discord.Embed(
        title="🎶 Cola de Reproducción",
        colour=DARK_PURPLE
    )
    # 0 ---> queueIndex[idGuild] || Es la cancion actual en reproduccion
    # [
    #   {
    #       'Titulo': 'Joe Arroyo - La Noche', 'link': 'https://www.youtube.com/watch?v=B-VBhgh_G8Q', 
    #       'streamUrl': 'https://rr3---sn-ja5gvjv-cvbr.googlevideo.com/videoplayback?expire=1746314130&ei=Mk8WaPmlNYy60_wPqvaGiQ8&ip=2800%3A484%3A3269%3A8100%3Aa185%3Adb42%3A1304%3A5489&id=o-ANhqsnfk0jCri2fC6-8QDOe7aOUErWKWkJdT8hIslUcs&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1746292530%2C&mh=y-&mm=31%2C29&mn=sn-ja5gvjv-cvbr%2Csn-cvb7sn7k&ms=au%2Crdu&mv=m&mvi=3&pl=40&rms=au%2Cau&initcwndbps=2035000&bui=AecWEAZGR-w3dzZkFfisxg5TvlEwRU3riY39F2jLOhoiyr1K5Y0VpyUFQYfHOXZqSkrpSBMaF1fdlWp5&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=k3gdxaXx_S_NUn9vBqQf1bcQ&rqh=1&gir=yes&clen=3617132&dur=262.401&lmt=1714529778800952&mt=1746291920&fvip=4&keepalive=yes&lmw=1&c=TVHTML5&sefc=1&txp=4502434&n=DV4K17x5gWAeyQ&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=ACuhMU0wRQIhAOxjidNIUwXs8JNzkfGf58G1pEnWov2B1-oNjmqikQfXAiBv2ezvAHCV-gEMvigWW3CytBqlHkSG3oxf5bFYwCbLgg%3D%3D&sig=AJfQdSswRAIgB50vNzA87l6Hw4ER9FA_nvXEp34Un_SMo2FeDWhqYLICIAlaPPgaZHkJiIWWhEEl3HMEuzEKUIqLPmnwBclX6HEj', 
    #       'Canal': 'Joe Arroyo', 'Duracion': '4:22', 
    #       'Miniatura': 'https://i.ytimg.com/vi/B-VBhgh_G8Q/hqdefault.jpg?sqp=-oaymwEmCOADEOgC8quKqQMa8AEB-AG-AoAC8AGKAgwIABABGGUgWyg9MA8=&rs=AOn4CLBK2OieNfbNHBzhHg6Q8uKwr2zLOQ'
    #   }, 
    #   <VoiceChannel id=1119856147520823309 name='General' rtc_region=None position=0 bitrate=64000 video_quality_mode=<VideoQualityMode.auto: 1> user_limit=0 category_id=1119856147520823307>
    # ] ---> Este es el indice [queueIndex[idGuild]] ||
    # Es decir que para acceder al objeto de la cancion tengo que acceder al indice 0 de queue[idGuild][indice_De_la_Cancion en Queue][0][atributo_que_necesito_acceder]
    
    miniatura = queue[idGuild][queueIndex[idGuild]][0]["Miniatura"]
    colaEmbed.set_thumbnail(url=miniatura)

    maxRange = min(len(queue[idGuild]), 20)
    totalSongs = len(queue[idGuild])

    for i in range(queueIndex[idGuild], maxRange):
        returnIndex = i - queueIndex[idGuild]
        cancion = queue[idGuild][i][0]
        titulo = f"[{returnIndex}]. ▶️ **Escuchando**" if returnIndex == 0 else (f"[{returnIndex}]. ⏭️ **Siguiente**" if returnIndex == 1 else f"[{returnIndex}]. 🎵 - **{truncar_titulo(cancion["Titulo"])}**")
        mensaje = f" - *[{cancion['Titulo']}]({cancion['link']})*\n - *{cancion['Canal']}* | `{cancion['Duracion']}`" if returnIndex == 0 else (f" - *[{cancion['Titulo']}]({cancion['link']})*\n - *{cancion['Canal']}* | `{cancion['Duracion']}`\n===")
        colaEmbed.add_field(
            name=titulo,
            value=mensaje,
            inline=False
        )

    colaEmbed.set_footer(text=f"`🎶 Total de canciones en cola: **{totalSongs}**`")
    await ctx.send(
        embed=colaEmbed,
        silent=True
    )

    # returnVaule = ""
    # miniatura = queue[idGuild][queueIndex[idGuild]][0]['Miniatura']
    # colaEmbed = discord.Embed(
    #     title="Cola de Reproduccion",
    #     description=returnVaule,
    #     colour=0x2c76dd
    # )
    # colaEmbed.set_thumbnail(url=miniatura)
    # if queue[idGuild] == []:
    #     colaEmbed.clear_fields()
    #     colaEmbed.add_field(name="Cola Vacia",value="No hay canciones el la cola de reproducion.")
    # else:
    #     print(f"Verificando las canciones en cola...\nqueueDict: {queue[idGuild]}, queueIndexDic: {queueIndex[idGuild]}")
    #     # In embeds.0.fields: Must be 25 or fewer in length. |||| Este es el mensaje de error cuando la cola es muy grande
    #     if len(queue[idGuild]) >= 20:
    #         maxRange = 20
    #         totalSongs = len(queue[idGuild])
    #     for i in range(queueIndex[idGuild], maxRange):
    #         upNextSongs = len(queue[idGuild]) - queueIndex[idGuild]
    #         if i > 5 + upNextSongs:
    #             break
    #         returnIndex = i - queueIndex[idGuild]
    #         # Condicional para establecer el Titulo del embed de la cola con Escuchando para la primera cancion 
    #         # y Siguiente para la segunda cancion en la lista cola de reproduccion
    #         if returnIndex == 0:
    #             returnIndex = "Escuchando"
    #         elif returnIndex == 1:
    #             returnIndex = "Siguente"
    #         colaEmbed.add_field(name=f"{returnIndex}", value=f"[{queue[idGuild][i][0]['Titulo']}]({queue[idGuild][i][0]['link']})\n- {queue[idGuild][i][0]['Canal']} {queue[idGuild][i][0]['Duracion']}", inline=False)
    #         returnVaule += f"{returnIndex} - [{queue[idGuild][i][0]['Titulo']}]({queue[idGuild][i][0]['link']}) - {queue[idGuild][i][0]['Canal']} {queue[idGuild][i][0]['Duracion']}"

    #         if returnVaule == "":
    #             colaEmbed.clear_fields()
    #             colaEmbed.add_field(name="Cola Vacia",value="No hay canciones el la cola de reproducion.")
    #     colaEmbed.add_field(name="Total de canciones en Cola!", value=f"Hay un total de {totalSongs}")
    # await ctx.send(embed=colaEmbed, silent=True)

@elBulloso.hybrid_command(
    name="limpiar",
    description="Elimina todas las canciones de la cola excepto la que está sonando.",
    aliases=["l", "L", "LIMPIAR"],
    help="Commando para limpiear/Eliminar la cola de reproduccion.",
)
async def limpiar(ctx: commands.Context):
    """
    - Limpia la cola de reproduccion de la guild en donde se uso el comando.

    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`
    
    ----------------------------

    **Returns:**
        `Mensaje de tipo embed en discord`
    
    [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    idGuild = int(ctx.guild.id)

    usuario = ctx.author

    pfp = usuario.display_avatar
    #if isInVc != None and isPlaying[idGuild]:
        #isPlaying[idGuild] = False
        #isPaused[idGuild] = False
        #isInVc[idGuild].pause()
    if queue[idGuild]:

        embedClear = discord.Embed(
            title="Cola de reproduccion Limpiada!",
            description=f'Se quitaron correctamente de la cola de reproduccion todas las canciones',
            colour=DARK_PURPLE
        )
        embedClear.set_footer(text=f'Peticion de: {str(usuario)}', icon_url=pfp)

        await ctx.send(embed=embedClear, silent=True)
        #print(f'Cola actual: {queue[idGuild]}\nCancion Cola en reproduccion {queue[idGuild][0]}')
        if len(queue[idGuild]) > 0 and queueIndex[idGuild] > len(queue[idGuild]):
            queue[idGuild][0] = queue[idGuild][queueIndex[idGuild]]
            del (queue[idGuild])[1:]
        else:
            queue[idGuild] = []
        #print(f'Cola actual: {queue[idGuild]}\nCancion Cola en reproduccion {queue[idGuild][0]}')
        #queue[idGuild] = []
    ctx_por_guild.pop(ctx.guild.id, None)
    queueIndex[idGuild] = 0

@elBulloso.hybrid_command(
        name="eliminar",
        description="Quita la última canción agregada a la cola.",
        aliases=["rm", "RM", "ELIMINAR"],
        help="Este comando elimina la ultima cancion agregada a la cola de reproduccion.",
)
@app_commands.describe(cancion="Elige una cancion de la cola")
async def eliminar(ctx: commands.Context, cancion: str = None):
    """
    - Se encarga de validar que halla canciones en la queue
    - Elminina la ultima cancion en la queue si no se pasan argumentos\n
     y si pasa un argumento elimina la cancion en ese indice
    - por ultimo envia un mensaje en discord para dar contexto\n
     de que elimino correctamente la cancion o que fallo
    
    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **cancion:** `(str)` | `*Optional*`
    
    ----------------------------

    **Returns:**
        `Mensaje del tipo embed en discord`

    [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    [Mas info sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
    """
    idGuild = int(ctx.guild.id)

    # await ctx.send(
    #     embed=embed_Eliminado_Queue(ctx, cancion),
    #     silent=True
    # )
    # queue[idGuild] = queue[idGuild][:-1]

    if not queue[idGuild]:
        await ctx.send(
            embed=MensajeBasico(
                "No se pudo Eliminar :melting_face: ",
                "No hay canciones en la cola de reproduccion.",
                DARK_RED
            ),
            silent=True
        )
        return
    
    if cancion is None:
        cancion = queue[idGuild][-1][0]

    index = next((i for i, item in enumerate(queue[idGuild]) if item[0]['Title'] == cancion), None )

    if index is None:
        await ctx.send("❌ Canción no encontrada en la cola.")
        return
    
    eliminada = queue[idGuild].pop(index)
    await ctx.send(
        embed=embed_Eliminado_Queue(ctx, eliminada[0]),
        silent=True
    )

    if not queue[idGuild] and isInVc[idGuild]:
        desconectado_por_codigo[idGuild] = True

        await isInVc[idGuild].disconnect()

        isInVc[idGuild] = None
        
        isPlaying[idGuild] = isPaused[idGuild] = False

        queueIndex[idGuild] = 0
        ctx_por_guild.pop(ctx.guild.id, None)

    elif queueIndex[idGuild] == len(queue[idGuild]):

        isInVc[idGuild].pause()
        queueIndex[idGuild] -= 1

        await reproducir(ctx)

@eliminar.autocomplete("cancion")
async def eliminar_autocomplete(interaction: discord.Interaction, current: str):
    """
        - Revisa dentro de una interaccion (SlashCommand) si hay canciones en la cola de reproduccion,\n
         Muestra los primeros 25 resultados dentro de la cola de reproduccion

        ----------------------------

        **Parameters:**
            **interaction:** `(class discord.Interaction)`,
            **current:** `(str)`
        
        ----------------------------

        **Returns:**
            `Lista de opciones dentro de la interaccion`

        [Mas info sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
    """
    idGuild = interaction.guild.id

    if not queue[idGuild]:
        return []
    
    canciones = [item[0]['Titulo'] for item in queue[idGuild]]

    resultados = [c for c in canciones if current.lower() in c.lower()][:25]
    return [discord.app_commands.Choice(name=title, value=title) for title in resultados]

@elBulloso.hybrid_command(
    name="pause",
    description="Detiene la reproducción sin borrarla.",
    aliases=["d", "pa", "PAUSE", "PA", "STOP", "stop", "D"],
    help="Commando para detener la cancion actual.",
)
async def pause(ctx: commands.Context):
    """
        - Pausa la reproduccion de musica si el bot\n
         Esta en un canal de voz,
        
        - Si el bot no esta en un canal de voz,\n
         no hay canciones en la cola o no esta reproduciendo una cancion

        ----------------------------

        **Parameters:**
            **ctx:** `(class discord.ext.commands.Context)`
        
        ----------------------------

        **Returns:**
            `Mensaje en discord de tipo embed`
        
        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    idGuild = int(ctx.guild.id)

    if not isInVc[idGuild]:
        await ctx.send(
            embed=MensajeBasico(
                "**No se pudo Pausar :face_exhaling: **",
                "No se puede pausar una cancion\nSi no estoy en un chat de voz.",
                ROJO
            ),
            silent=True
        )

    elif not queue[idGuild]:

        await ctx.send(
            embed=MensajeBasico(
                "**No se pudo Pausar :face_exhaling: **",
                "No se puede pausar una cancion\nSi no hay canciones en la cola.",
                ROJO
            ),
            silent=True
        )

    elif isPlaying[idGuild]:

        await ctx.send(
            embed=MensajeBasico(
                "**Pausando! :sleeping: **",
                "Pausando la cancion!.",
                DARK_GREEN
            ),
            silent=True
        )
        isPlaying[idGuild] = False
        isPaused[idGuild] = True
        isInVc[idGuild].pause()

@elBulloso.hybrid_command(
    name="resume",
    description="Continúa la canción que estaba pausada.",
    aliases=["r", "RESUME", "R"],
    help="Commando para volver a reproducir una cancion pausada",
)
async def resume(ctx: commands.Context):
    """
        - Revisa que el bot este en un chat de voz de una guild,\n
         que no este pausado (Verifica el diccionario de estado isPaused )\n
         y que la cola de reproduccion tenga canciones.

        - Si esta en un chat de voz y esta pausado, volvera a reproducir la primera\n
         cancion de la cola de reproduccion

        ----------------------------

        **Parameters:**
            **ctx:** `(class discord.ext.commands.Context)`
        
        ----------------------------

        **Returns:**
            `Mensaje en discord de tipo embed`
        
        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    # print("Resumiendo...")
    idGuild = int(ctx.guild.id)

    if not isInVc[idGuild]:
        await ctx.send(
            embed=MensajeBasico(
                "**No se pudo Pausar :face_exhaling: **",
                "No se puede pausar una cancion\nSi no estoy en un chat de voz.",
                ROJO
            ),
            silent=True
        )
    elif not queue[idGuild]:

        await ctx.send(
            embed=MensajeBasico(
                "**No se pudo reanudar :nerd: **",
                "No hay canciones por reproducir.",
                ROJO
            ),
            silent=True
        )

    elif isPaused[idGuild]:
        await ctx.send(
            embed=MensajeBasico(
                "**Reanudando! :upside_down: **",
                "Reanudando la cancion!.",
                DARK_GREEN
            ),
            silent=True
        )
        isPlaying[idGuild] = True
        isPaused[idGuild] = False
        isInVc[idGuild].resume()

@elBulloso.hybrid_command(
    name="skip",
    description="Salta la canción actual o varias si se especifica una en la cola.",
    aliases=["s", "S", "SKIP"],
    help="Commando para saltar a la siguente cancion en la cola de reproducion",
)
@app_commands.describe(cancion="Cancion a la que quieres saltar!")
async def skip(ctx: commands.Context, cancion: str = None):
    """
        - Salta a una cancion determinada o solo una cancion\n
         dentro de la cola de reproduccion si hay canciones y\n
         hay una cancion adelante.

        ----------------------------

        **Parameters:**
            **ctx:** `(class commands.Context)`,
            **cancion:** `(str)` | `*Optional*`

        ----------------------------

        **Returns:**
            `(dict)`

        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
        [Mas info sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
    """
    #print("".join(arg))
    # arg = " ".join(arg)
    #print(not arg, type(arg), arg == type(arg))

    idGuild = int(ctx.guild.id)
    print(f"Logger del skip, numero de skips {cancion}, Numero de canciones en cola: {len(queue[idGuild])}, Indice actual de la cola: {queueIndex[idGuild]}")
    #cancion = queue[idGuild][queueIndex[idGuild]][0]
    if isInVc[idGuild] == None:
        await ctx.send(
            ctx.author.mention,
            embed=MensajeBasico(
                "**No se pudo skipear :nerd: **",
                f"{ctx.author.mention} El bulloso Necesita estar en un canal de voz para usar ester comando!",
                DARK_RED
            ),
            silent=True
        )
        return
    
    if not queue[idGuild] or queueIndex[idGuild] >= len(queue[idGuild]):
        await ctx.send(
            embed=MensajeBasico(
                "**No hay canciones en la cola! :dizzy_face: **",
                f"No puede saltar mas canciones de las que hay en la cola\n**Canciones en cola: `{len(queue[idGuild])}`**",
                DARK_PURPLE
            ),
            silent=True
        )
        return
    
    # Skip a una cancion en especifico
    if cancion is not None:
        index = int(cancion)
        if index >= len(queue[idGuild]) or index <= queueIndex[idGuild]:
            await ctx.send(
                embed=MensajeBasico(
                    "** Indice de canción no válido o ya reproducido! :dizzy_face: **",
                    f"No puede saltar mas canciones de las que hay en la cola\n**Canciones en cola: `{len(queue[idGuild])}`**",
                    DARK_PURPLE
                ),
                silent=True
            )
            return
        
        queueIndex[idGuild] = index
    else:
        queueIndex[idGuild] += 1

    isInVc[idGuild].pause()
    await reproducir(ctx)
    
    # if not queue[idGuild] or queueIndex[idGuild] >= len(queue[idGuild]) - 1:
    #     await ctx.send(
    #         embed=MensajeBasico(
    #             "Saltando la cancion :face_with_diagonal_mouth: ",
    #             "No hay mas canciones en la cola de reproducion\n\n\tQuitando La cancion",
    #             DARK_BLUE
    #         ),
    #         silent=True
    #     )
    #     isInVc[idGuild].stop()
    #     await siguienteCancion(ctx)
    #     return
    #     #await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))

    # if cantidad < 1:
    #     await ctx.send(
    #         embed=MensajeBasico(
    #             "Suaga ahi sog :face_with_diagonal_mouth:",
    #             f"{ctx.author} Necesita estar en un canal de voz para usar ester comando!",
    #             DARK_RED
    #         ),
    #         silent=True
    #     )
    #     return
    
    
    
    # if cancion is None:
    #     await ctx.send(
    #         "❌ Debes elegir una canción para saltar.",
    #         silent=True
    #     )
    #     return
    
    # index = int(cancion)

    # if index >= len(queue[idGuild]):
    #     await ctx.send("❌ Índice fuera de rango.", silent=True)
    #     return

    
    # if isInVc[idGuild].is_playing():
    #     isInVc[idGuild].pause()
    
    # queueIndex[idGuild] += cantidad
    # await reproducir(ctx)

    # if not arg:
    #     if isInVc[idGuild] != None and isInVc[idGuild]:
    #         isInVc[idGuild].pause()
    #         queueIndex[idGuild] += 1
    #         await reproducir(ctx)
    # else:
    #     if int(arg) > len(queue[idGuild]):
    #         await ctx.send(embed=MensajeBasico("No hay canciones en la cola! :dizzy_face:",f"No puede saltar mas canciones de las que hay en la cola\nCanciones en cola: {len(queue[idGuild])}",DARK_PURPLE), silent=True)
    #     else:
    #         if isInVc[idGuild] != None and isInVc[idGuild]:
    #             isInVc[idGuild].pause()
    #             queueIndex[idGuild] += int(arg)
    #             await reproducir(ctx)

@skip.autocomplete("cancion")
async def skip_autocomplete(interaction: discord.Interaction, current: str):
    """
        - Se encarga de verificar la cola de reproduccion en la guild\n
         donde se genero el comando, Devuelve a la interacion de discord\n
         Las siguientes 25 canciones si hay canciones en la cola, si no\n
         Devuelve un arreglo(Vector,Lista) vacio a la interacion de discord.

        - Al comando skip le devuelve si se pasa el indice de la cancion en formato string

        - Current hace referencia al input del usuario durante la interaccion\n
         En este caso el numero especifico de cancion a saltar.

        ----------------------------

        **Parameters:**
            **interaction:** `(class discord.Interaction)`,
            **current:** `(str)`

        ----------------------------

        **Returns:**
            `(str(int))`

        [Mas info sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
    """
    print("Cancion actual: ", current)
    idGuild = interaction.guild.id
    if not queue[idGuild]:
        return []
    
    return [
        discord.app_commands.Choice(
            name=item[0]['Titulo'][:100],
            value=str(i)
        ) for i, item in enumerate(queue[idGuild])
        if i > queueIndex[idGuild] and current.lower() in item[0]['Titulo'].lower()
    ][:25]
    # return [
    #     discord.app_commands.Choice(
    #         name=item[0]['Titulo'][:100],
    #         value=str(i)
    #     ) for i, item in enumerate(queue[idGuild][queueIndex[idGuild]:])
    #     if current.lower() in item[0]['Titulo'].lower()
    # ][:25]

@elBulloso.hybrid_command(
    name="previus",
    description="Devuelve la cancion en la cola de reproducion",
    aliases=["pr, PR, PREVIUS"],
    help="Commando para volver una cancion en la cola de reproducion",
    usage="$pr"
)
@app_commands.describe(cancion="Canción anterior a la que deseas volver")
async def previus(ctx: commands.Context, cancion: str = None):
    """
        - Se encarga de devolver la cancion de la cola de reproduccion\n
         de la guild en donde se uso el comando, Puede devolverse un numero\n
         determido de canciones o solo una.

        ----------------------------

        **Parameters:**
            **ctx:** `(class discord.ext.commands.Context)`,
            **cancion:** `(str)` | `*Optional*`
        
        ----------------------------

        **Returns:**
            `Mensaje en el chat donde se uso el comando en discord`

        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
        [Mas info sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
    """
    idGuild = int(ctx.guild.id)
    print(f"Log Previus, indice de cancion a devolverse: {int(cancion)}, Indice actual de la cola: {queueIndex[idGuild]}\nbot: {elBulloso.user.global_name} | {ctx.author} | {ctx.bot}")

    if ctx.interaction:
        ctx.interaction.response.defer(thinking=True)
    #cancion = queue[idGuild][queueIndex[idGuild]][0]

    try:
        if isInVc[idGuild] == None:

            await ctx.send(
                embed=MensajeBasico(
                    "**Suaga ahi sog :face_with_diagonal_mouth: **",
                    f"{ctx.author} Necesita estar en un canal de voz para usar este comando!",
                    DARK_RED
                ),
                silent=True
            )
            return
        
        if not queue[idGuild]:
            await ctx.send(
                embed=MensajeBasico(
                    "** Cola Vacia :open_mouth: **",
                    "No hay canciones a las que volver",
                    DARK_RED
                ),
                silent=True
            )
            return

        if cancion is not None:
            index = int(cancion)
            if index >= queueIndex[idGuild]:
                await ctx.send(
                    "** Trateme mas que serio **",
                    "Esa cancion esta sonando o aun no ha sonado",
                    silent=True
                )
                return
            queueIndex[idGuild] = index
        else:
            if queueIndex[idGuild] <= 0:

                await ctx.send(
                    embed=MensajeBasico(
                        "** No hay cancion anterior :open_mouth: **",
                        "No hay cancion anterior en la cola de reproducion\nVolviendo a reproducir la cancion actual",
                        DARK_RED
                    ),
                    silent=True
                )
                # Lo pause para volver a reproducirlo con reproducir en el indice actual
                isInVc[idGuild].pause()
                await reproducir(ctx)
                return
                #await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))
            else:
                # Reduciendo el indice si se hizo previus sin numero, y hay al menos una cancion anterior  
                queueIndex[idGuild] -= 1
        if ctx.interaction:
            await ctx.interaction.followup.send(f"Se devolvio a la cancion numero {queueIndex[idGuild]}")
        
        isInVc[idGuild].pause()
        await reproducir(ctx)
        
    except Exception as e:
        await ctx.interaction.followup.send(f"❌ Ocurrió un error", ephemeral=True)
        print(f"Fallo el previus: {e}")

@previus.autocomplete("cancion")
async def previus_autocomplete(interaction: discord.Interaction, current: str):
    """
        - Se encarga de revisar si hay canciones en la cola de reproduccion,\n
         Evalua tambien que no este en la primera cancion de la cola de reproduccion.

        - Devuelve a la interacion de discord las 25 canciones anteriores en la cola,\n
         Y si no hay ninguna cancion anterior devuelve un arreglo vacio a la interacion.

        - Al comando previus le devuelve el indice de la cancion a devolverse\n
         si se escoje una opcion de la interacion o se pasa un arg cancion: Numero de indice.
        
        - Current hace referencia al input del usuario durante la interaccion\n
         En este caso el numero especifico de cancion a devolver.

        ----------------------------

        **Parameters:**
            **interaction:** `(class discord.Interaction)`,
            **current:** `(str)`
        
        ----------------------------

        **Returns:**
            `(str(int))`

        [Mas infor sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
    """
    idGuild = interaction.guild.id

    if not queue[idGuild] or queueIndex[idGuild] == 0:
        return []
    
    return [
        discord.app_commands.Choice(
            name=item[0]['Titulo'][:100],
            value=str(i)          # Que recorra el diccionario queue llave guild desde 0 hasta el indice actual de la cola
        ) for i, item in enumerate(queue[idGuild][:queueIndex[idGuild]])
        if current.lower() in item[0]['Titulo'].lower()
    ][-25:] # Que muestres los primeros 25 registros de atras hacia adelante

async def siguienteCancion(ctx: commands.Context):
    #print("\nEntro a siguiente cancion")
    idGuild = int(ctx.guild.id)
    if not isPlaying[idGuild]:
        return
    # Si la el indice de la cola actual + 1 es menor a la cantidad de canciones en la cola
    if queueIndex[idGuild] + 1 < len(queue[idGuild]):
        isPlaying[idGuild] = True
        queueIndex[idGuild] += 1
        #         queue[Guild][numero_Actual_de_la_Cola_de_Reproduccion[Guild]][cancion]
        #         Es decir la queue Completa de Guild indice -> numero en la cola actual de reproducion de la guild -> el 0 es cancion 1 canal de voz
        cancion = queue[idGuild][queueIndex[idGuild]][0]
        # print(f"Precondicion cancion: {cancion}, condiciones: {not cancion['streamUrl']} {cancion['streamUrl'] is None}")
        # Verificando si el diccionario cancion tiene la llave streamUrl
        if not cancion.get('streamUrl') or cancion.get('streamUrl') is None:
            cancion = await asyncio.to_thread(getStream, cancion['link'])
            queue[idGuild][queueIndex[idGuild]][0] = cancion

        await mensaje(ctx, cancion)
        #print("anted de await ctx.send en linea 267")
        #await ctx.send(embed= embed_Reproduciendo_Ahora(ctx, cancion))
        #print(f"Source: {cancion['Source']}")
        source = discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(source, 0.5)
        isInVc[idGuild].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(siguienteCancion(ctx), elBulloso.bot_loop))
        #isInVc[idGuild].source = discord.PCMVolumeTransformer(isInVc[idGuild].source, 0.5)
    else:
        # Se supone que ya no hay mas canciones en la cola entonces entra aqui
        # Por eso entonces limpio la cola
        queueIndex[idGuild] = 0
        queue[idGuild] = []
        isPlaying[idGuild] = False
        await ctx.send(
            embed=MensajeBasico(
                "**Se termino la cola de reproduccion! :frowning2: **",
                "Limpiando la cola de reproduccion",
                DARK_GREEN
            ),
            silent=True
        )
        

#Funcion para reproducir la musica
async def reproducir(ctx: commands.Context):
    """
        - Esta funcion se encarga de Verificar la cola de reproduccion\n
         conectar el bot al canal de voz del usuario que uso el comando\n
         Revisar si la cancion guardada en la cola tiene la streamUrl\n
         Buscar la streamUrl si no esta,

        - Mandar un contexto de la cancion que va a reproducir

        - reproducir la cancion usando FFmpeg

        - al terminar de reproducir ir a la funcion siguienteCancion

        ----------------------------

        **Parameters:**
            **ctx:** `(class discord.ext.commands.Context)`
        
        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
        [Mas infor sobre FFmpegPCMAudio](https://discordpy.readthedocs.io/en/stable/api.html#ffmpegpcmaudio)
    """
    idGuild = int(ctx.guild.id)
    # print(f'entro a reproducir queIndex: {queueIndex[idGuild]} queue: {len(queue[idGuild])}, channel: {queue[idGuild][queueIndex[idGuild]][1]}')
    if queueIndex[idGuild] < len(queue[idGuild]):
        isPlaying[idGuild] = True
        isPaused[idGuild] = False

        #print(f"Estado is playing: {isPlaying[idGuild]} ")
        # Conectarse usando el canal guardado en el diccionario queue llave Guild, Indice de la Cola actual (queueIndex[idGuild]), posicion 1 [1] (canal de voz)
        await conectarse(ctx, queue[idGuild][queueIndex[idGuild]][1])

        cancion = queue[idGuild][queueIndex[idGuild]][0]
        # print(f"Precondicion cancion: {cancion["Titulo"]}, condiciones: {not cancion['streamUrl']} {cancion['streamUrl'] is None}")
        # Verificando si el diccionario cancion tiene la llave streamUrl
        if not cancion.get('streamUrl') or cancion.get('streamUrl') is None:
            cancion = await asyncio.to_thread(getStream, cancion['link'])
            queue[idGuild][queueIndex[idGuild]][0] = cancion

        await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion), silent=True)
        source = discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS)

        ## ******************************* Probando el PCMVolumeTransformer
        source = discord.PCMVolumeTransformer(source, 0.5)
        ## ****************************************************************************

        isInVc[idGuild].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(siguienteCancion(ctx), elBulloso.bot_loop))
        #print(f"Source: {cancion['Source']}")
        #isInVc[idGuild].play(discord.FFmpegPCMAudio(
        #    cancion['Source']), after=lambda e: siguienteCancion(ctx)
        #)
        #isInVc[idGuild].source = discord.PCMVolumeTransformer(isInVc[idGuild].source, 0.5)
        #print("Antes de siguente cancion")
    else:
        await ctx.send(embed=MensajeBasico("**Cola Vacia! :melting_face: **","No hay mas canciones en la cola de reproduccion",DARK_PURPLE), silent=True)
        queueIndex[idGuild] += 1
        isPlaying[idGuild] = False

#Comando para conectar / Mover el bot a un canal de voz Edit: No deberia ser un comando
#Funcion para conectar el bot al canal de voz del autor 
#@elBulloso.command()
async def conectarse(ctx: commands.Context, channel: discord.VoiceChannel):
    """
        - Este comando se encarga de conectar o mover el bot a un canal de voz

        ----------------------------

        **Parameters:**
            **ctx:** `(class discord.ext.commands.Context)`
            **channel:** `(class discord.VoiceChannel)`
        
        ----------------------------

        **Returns:**
            `None`
            Devuelve contexto en discord
    """
    idGuild = int(ctx.guild.id)
    if isInVc[idGuild] == None or not isInVc[idGuild].is_connected():
        isInVc[idGuild] = await channel.connect()
        em = discord.Embed(
            title=f"**Conectado a {ctx.author.voice.channel}**",
            description=f"Peticion de union hecha por {ctx.author.mention}",
            colour=VERDE
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        await ctx.send(embed=em, silent=True)
        if isInVc[idGuild] == None:
            await ctx.send(embed=MensajeBasico("**A lo bien :middle_finger: **","No me pude conectar al canal de voz\nDebe estar en un canal de Voz",ROJO))
            return
    else:
        await isInVc[idGuild].move_to(channel)

@elBulloso.hybrid_command(
        name="usuarios",
        description="Este comando muestra la lista de usuarios que ve el bot.",
        help="Este comando muestra la lista de usuarios que ve el bot.",
        usage="$usuarios"
)
async def usuarios(ctx: commands.Context):
    """
        Este comando muestra la lista de usuarios que ve el bot.
    """
    usuarios = list(elBulloso.users)
    for user in usuarios:
        await ctx.send(user, silent=True)

# @elBulloso.command(
#         name="sebax",
#         help="Comando para mencionar a sebax ._.",
#         brief="Comando para mencionar a sebax",
#         description="Comando para mencionar a sebax ._."
# ) #No sirve, al parecer la property mention no tiene setter, ._.
@elBulloso.hybrid_command(
    name="sebax",
    description="Comando para mencionar a sebax ._.",
    help="Comando para mencionar a sebax ._.",
    usage="$sebax",
)
async def sebax(ctx: commands.Context):
    """
        - Este comando recibe el contexto del comando y devuelve en discord un mensaje mencionando a sebax

        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
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
@elBulloso.hybrid_command(
    name="unirse",
    description="Mueve el bot o Une el bot al canal de voz actual",
    aliases=["u","U","UNIRSE"],
    help="Comando usado para unir al bot al canal de voz actual",
    usage="$u"
)
async def unirse(ctx: commands.Context):
    """
        - Une el bot a un chat de voz en el que esta el usuario que uso el comando

        ----------------------------

        **Parameters:**
            **ctx:** `(class discord.ext.commands.Context)`
        
        **Returns:**
            `None`
            No retorna nada manda el contexto a Discord

        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await conectarse(ctx, channel)
    else:
        await ctx.send(embed=MensajeBasico("**Sea serio pa! :clown: **",f'Tiene que estar en un canal de voz para unirme.',ROJO))


@elBulloso.hybrid_command(
        name="salir",
        description="Saca al bot del canal de voz y limpia la cola de reproducción.",
        aliases=["q","Q","SALIR"],
        help="Comando usado para desconectar el bot del canal de voz actual.\nEsto eliminara la cola de reproduccion actual.",
)
async def salir(ctx: commands.Context):
    """
        - Se encarga de limpiar la cola de reproduccion,\n
         reiniciar los estados globales y desconectar el bot

        ----------------------------

        **Parameters:**
            **ctx**: `(class discord.ext.commands.Context)`
        
        **Returns**:
            `None`
            Manda el contexto a discord directamente

        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
    """
    idGuild = int(ctx.guild.id)

    #Deteniendo la reproduccion si esta activa
    if isInVc[idGuild] and isInVc[idGuild].is_playing():
        isInVc[idGuild].stop()
    
    # Limipiando la cola de reproduccion

    await limpiar(ctx)
    
    # Reiniciando los estados
    isPlaying[idGuild] = False
    isPaused[idGuild] = False
    queue[idGuild] = []
    queueIndex[idGuild] = 0

    if isInVc[idGuild] != None:
        em = discord.Embed(
            title=f"**Desconectado de {ctx.author.voice.channel}**",
            description=f"ElBulloso Se abrio por culpa de {ctx.author.mention}",
            colour=0xdf1141
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        desconectado_por_codigo[idGuild] = True

        await ctx.send(embed=em)
        await isInVc[idGuild].disconnect()
        ctx_por_guild.pop(ctx.guild.id, None)
        isInVc[idGuild] = None
    else:
        await ctx.send("❌ No estoy conectado a ningún canal de voz. Sapa :middle_finger:")


async def agregarPlaylistYT(ctx: commands.Context, url: str, channel: discord.VoiceChannel):
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

# def search_youtube(query):

#         with yt_dlp.YoutubeDL(ydl_options) as ydl:
#             data = ydl.extract_info(query, download=False)

#             if 'entries' in data:
#                 return data['entries'][:5]
#             return [data]



# @elBulloso.command(name="play",
#         aliases=["p","P","PLAY"],
#         help="Comando para buscar en youtube una cancion con el nombre de la cancion",
#         usage="$p link",
#         description='Comando que ejecuta exlusivamente links o nombres de una cancion'
# )
# /play search:Joe Arroyo La Noche
@elBulloso.hybrid_command(
    name="play",
    description="Ejecuta una canción por nombre o link",
    aliases=["p", "P", "PLAY"],
    help="Comando para buscar en YouTube una canción con el nombre o URL",
    usage="$p <nombre o link>",
)
@app_commands.describe(search="Titulo o enlace de la cancion")
async def play(ctx: commands.Context, *, search: str = None):
    """
        - Comando que se encarga de buscar y reproducir canciones
         Usando un texto o url, si no se usan args verificara si hay canciones
         en la cola y si esta reproduciendo una cancion el bot, Si hay cancion y no esta reproduciendo
         audio, reproducira la primera cancion de la cola

        ----------------------------

        **Parameters:**
            **ctx:** `(class discord.ext.commands.Context),`
            **search** `Optional (str)`
        
        ----------------------------

        **Returns:**
            `None`
            Devuelve directamente a discord

        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)
        [Mas infor sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
    """
    # Si el contexto es de una Interaccion (slashCommand)
    # Esto le dice a Discord:
    #“Estoy trabajando, espera por favor…”, y te da 15 minutos para responder sin que la interacción expire.
    if ctx.interaction:
        await ctx.interaction.response.defer(thinking=True)

    print("Entro play... Search: ", search)
    search = search
    idGuild = int(ctx.guild.id)
    #print(type(search), search, search.replace(" ", ""))

    # Guardado el contexto de manera temporal para reconectar y volver a reproducir en caso de errores
    # Esto tambien se sobre escribe cada vez que se llame el comando play
    ctx_por_guild[idGuild] = ctx
    try:
        channel = ctx.author.voice.channel
        print("Channel: ", channel, " Channelid: ", channel.id)

        # if not ctx.author.voice:
        #     await ctx.send(embed=MensajeBasico("A lo bien :middle_finger:","No me pude conectar al canal de voz\nDebe estar en un canal de Voz",ROJO), silent=True)
        #     return
        
        await conectarse(ctx, channel)
    except:
        em = discord.Embed(
            title=f"**No me pude conectar**",
            description=f"Para conectarme debe estar en un canal de voz",
            colour=0xdf1141
        )
        em.set_footer(icon_url=elBulloso.user.display_avatar)
        await ctx.send(ctx.author.mention,embed=em)
        return
    
    if not search or search is None:
        if len(queue[idGuild]) == 0:
            await ctx.send(embed=MensajeBasico("**Cola Vacia! :face_with_monocle: **","No hay canciones en la cola\n\nIngrese un link o una cancion para buscarla", DARK_RED), silent=True)
            return
        elif not isPlaying[idGuild]:
            if queue[idGuild] == None or isInVc[idGuild] == None:
                print("Entro no hay queue o esta en vc es igual a none")
                #isPlaying[idGuild] = False       Si se da;a algo activar esto
                await reproducir(ctx)
            else:
                print("Entro else not args play")
                if ctx.interaction:
                    await ctx.interaction.followup.send(
                        embed=MensajeBasico(
                            "**Reanundando / Reproduciendo cancion**",
                            "Reproduciendo la cancion actual en la cola",
                            DARK_GREEN
                        ),
                        ephemeral=True, # Solo visible para el usuario
                        silent=True
                    )
                else:
                    await ctx.send(
                        embed=MensajeBasico(
                            "**Reanundando / Reproduciendo cancion**",
                            "Reproduciendo la cancion actual en la cola",
                            DARK_GREEN
                        ),
                        silent=True
                    )
                isPaused[idGuild] = False
                isPlaying[idGuild] = True
                isInVc[idGuild].resume()
        else:
            return
    else:
        #esplaylist = esPlaylistYT(search)
        # print("Precondicion search: ",search)
        veriSearch = esUrl(search) 
        match veriSearch[0]:
            case "youtube_playlist":
                search = veriSearch[1]
                cancion = await agregarPlaylistYT(ctx, search, channel)
            case "spotify_playlist":
                search = veriSearch
                start = time.time()
                cancion = await busquedaPlaylist(ctx, channel, search)
                # archivo_test.write(f"Test funcion: busquedaPlaylist optimizado tiempo de ejecucion: {time.time() - start}\n")
                # print(f"\tTermino BusquedaPlaylistSp\nUtlima_CancionPl: {cancion}\n tiempo de ejecucion: ", time.time() - start)
            case "spotify_album":
                search = veriSearch
                cancion = await busquedaAlbum(ctx, channel, search)
            case "spotify_track":
                search = veriSearch[1]
                try:
                    track_data = cliente.track(search)
                    cancion = await buscar(nombreArtiCancionPlaylistTrack(track_data))
                except Exception as e:
                    await ctx.send(embed=MensajeBasico("❌ **No se pudo obtener el track**", "Fallo el buscar la track de Spotify", ROJO), silent=True)
                    return
            case "youtube_video":
                search = veriSearch[1]
                try:
                    cancion = await obtener_stream(search)
                    if not cancion:
                        raise ValueError("No se encontró la canción")
                except Exception as e:
                    await ctx.send(embed=MensajeBasico("❌ **Error al buscar**", "Fallo el buscar video por link de Youtube", ROJO), silent=True)
                    return
            case "url_generica":
                search = veriSearch[1]
                cancion = await obtener_stream(search)
            case "texto":
                try:
                    cancion = await buscar(search)
                    if not cancion:
                        raise ValueError("No se encontró la canción")
                except Exception as e:
                    await ctx.send(embed=MensajeBasico("❌ **Error al buscar**", "Fallo el buscar video por titulo o nombre", ROJO), silent=True)
            case _:
                await ctx.send(embed=MensajeBasico("**Uy cual es esa :rage: **",f"Que mierda buscate sapa {ctx.author.mention}", ROJO), silent=True)
                return
                

        # if search.startswith("https://www.youtube.com/playlist?list=") == True:
        #     cancion = await agregarPlaylistYT(ctx, search, channel)
        # if search.startswith("https://open.spotify.com/") == True:
        #     # verificarTokenSpotify()
        #     search = search.split('?')[0]   
        #     #La unica solucion seria poner la busqueda de pl en un segundo subproceso no hay mas manera
        #     if search.startswith('https://open.spotify.com/playlist/') == True:
        #         #print("Loop antes de empezar la busqueda sp ", asyncio.get_running_loop(), " ", asyncio.get_event_loop())
        #         #print('entro a playlist')
        #         #cancion = asyncio.run_coroutine_threadsafe(busquedaPlaylist(ctx, channel, search), elBulloso.loop)
        #         #asyncio.run_coroutine_threadsafe(busquedaPlaylist(ctx, channel, search), elBulloso.loop)
        #         #cancion = None
        #         #asyncio.threads.to_thread(busquedaPlaylist(ctx, channel, search))
        #         #print("Loop despues de busqueda sp ", asyncio.get_running_loop(), " ", asyncio.get_event_loop())
        #         cancion = await busquedaPlaylist(ctx, channel, search)
        #         # print("Spotify playlis, termino la cancion ", cancion['Titulo'])
        #     elif search.startswith("https://open.spotify.com/intl-es/album"):
        #         cancion = await busquedaPlaylist(ctx, channel, search)
        #     else:
        #         search = search.removeprefix('https://open.spotify.com/intl-es/track/')

        #         cancion = await asyncio.to_thread(buscar, nombreArtiCancionPlaylistTrack(cliente.track(search)))     
              
        # if veriSearch[0] in ["youtube_playlist", "url_generica"]:
        #     cancion = await asyncio.to_thread(getStream, veriSearch[1])
        # else:
        #     cancion = await asyncio.to_thread(buscar, search)

        if not cancion or not isinstance(cancion, dict) or 'Titulo' not in cancion:
            await ctx.send(embed=MensajeBasico("**Uy cual es esa :rage: **",f"Que mierda buscate sapa {ctx.author.mention}", ROJO), silent=True)
            return
        else:
            if veriSearch and veriSearch[0] in ["spotify_album", "spotify_playlist", "youtube_playlist"]:
                None
            else:
                queue[idGuild].append([cancion, channel])

            if not isPlaying[idGuild]:
                await reproducir(ctx)
            else:
                await ctx.send(embed=embed_Añadido_Queue(ctx, cancion), silent=True)

    

    # vc = await voice.channel.connect()

    
    
    # await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion=audio_info), silent=True)

    # source = discord.FFmpegPCMAudio(audio_info['url'], **FFMPEG_OPTIONS)

    # vc.play(source, after=lambda e: print('Reproducción terminada', e))

def limpiar_cache():
    """
    - Se encarga de limpiar el cache global del autocomplete\n
     en el comando play

    - Analiza la diferencia en segundos desde que se creo el cache para\n
     una query en especifico y si execede el tiempo la elimina
    """
    ahora = time.time()
    try:
        expirados = [k for k, (t, _) in autocomplete_cache.items() if ahora - t > CACHE_TTL]
        for k in expirados:
            del autocomplete_cache[k]
        print("Limpiado el cache de autocomplete")
    except Exception as e:
        print(f"Fallo la Limpieza de el cache: {e}")

def search_youtube_lite_cached(query: str) -> dict:
    """
    - Se encarga de hacer una busqueda ligera en youtube\n
     Con una query y cachear el resultado

    ----------------------------

    **Parameters:**
        **query:** `(str)`
    
    ----------------------------

    **Returns:**
        `(dict)`
    """
    now = time.time()
    print("Entro search_Lite_cached, query", query)

    if query in autocomplete_cache:
        print(" cached_time: ", {now - autocomplete_cache[query][0]})
        cached_time, cached_results = autocomplete_cache[query]
        # Cache TTL es Time To Live
        if now - cached_time < CACHE_TTL:
            return cached_results # Cache valido
    
    if query.startswith("https://www.youtube.com/watch?"):
        # print("Entro autocomplete YTVid")
        # Si no está en cache o está vencido, buscar
        opciones = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': True,  # evita bajar info del stream
            'default_search': 'ytsearch1',
        }
        query = f"ytsearch1:{query}"

    else:
        # Si no está en cache o está vencido, buscar
        opciones = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': 'in_playlist',  # evita bajar info del stream
            'default_search': 'ytsearch5',
        }
        query = f"ytsearch4:{query}"
            # 'forcejson': True,
            # 'simulate': True,

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(query, download=False)
        entries = info['entries'] if 'entries' in info else [info]
        # print(f"AutoComplete Youtube Search id: {entries[0].get('id')}")
        # Retorna solo lo esencial
        results = [{
            'title': entry.get('title'),
            'uploader': entry.get('uploader'),
            'id': entry.get('id'),
            'url': entry.get('url'),
        } for entry in entries[:4]]

        # print(f"Autocomplet result 0 {results[0].get('id')}  {time.time() - now}")

        autocomplete_cache[query] = (now, results)
        limpiar_cache()
        return results


@play.autocomplete("search")
async def youtube_autocomplete(interaction: discord.Interaction, current: str):
        """
        - Parsea un texto dentro de una interaccion de un slashCommand\n
         Para definir si es texto o URL/Link,

        - Luego busca los primeros 5 resultados si es un texto,\n
         Si es un link de youtube o Spotify muestra su titulo,\n

        - Por ultimo devuelve a la logica del comando un string parseado

        ----------------------------

        **Parameters:** 
            **interaction:** `(class discord.Interaction)`, 
            **current:** `(str)`
            
        ----------------------------

        **Returns:**
            `(str)`
        
        [Mas infor sobre autocomplete](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.HybridCommand.autocomplete)
        """
        if not current or len(current) < 3:
            return []
        
        # results = await asyncio.to_thread(search_youtube, current)

        # Si la busqueda es de spotify entre aqui
        veriUrl = esUrl(current)
        if veriUrl[0] in ["spotify_playlist", "spotify_track", "spotify_album"]:
            try:
                match veriUrl[0]:
                    case "spotify_track":
                        data = nombreArtiCancionPlaylistTrack(cliente.track(veriUrl[1]))
                    case "spotify_playlist":
                        # playlist_data = cliente.playlist(veriUrl[1])
                        # Por temas de protecion de datos no muestro el usuario que creo la playlist
                        # data = f"{playlist_data.get("name")} - {playlist_data.get("owner")}
                        data = cliente.playlist(veriUrl[1]).get("name")
                    case "spotify_album":
                        data = cliente.album(veriUrl[1]).get("name")
                    case _:
                        data = "No hay autocompletado con Spotify 😘"
            except Exception as e:
                data = f"Revisa el link o vuelvelo a copiar, No lo encontre 😓 " or None # Para que la ternaria en el return Devuelva el else en caso de que pase de aqui
                print("‼️🆘 Fallo la busqueda por spotipy, Busqueda:\n ", veriUrl[1], "\nException: ", e, type(e))
                return [
                    discord.app_commands.Choice(
                        name = data,
                        value = "Reivsa el link"
                    )
                ]
                # interaction.followup.send(
                #     embed=MensajeBasico(
                #         "Fallo el autcomplete",
                #         "Mala mia sog :melting_face: ",
                #         DARK_RED
                #     )
                # )
                
            # Estructura de la Ternaria
            # True if Condicion else False
            # "Hola" if "$Saludo" else "Saludame"
            return [
                discord.app_commands.Choice(
                    name = data if data else "No hay autocompletado con Spotify 😘",
                    value = current
                )
            ]
        # Si la busqueda es un texto o link de youtube entre aqui
        if veriUrl[0] in ["youtube_video", "texto", "youtube_playlist"]:
            current = veriUrl[1]
            
        
        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(search_youtube_lite_cached, current),
                timeout=2.5
            )
        except asyncio.TimeoutError:
            # Si se queda buscando y alguien escoge la opcion buscara lo que puso en search:
            return [
                discord.app_commands.Choice(name="⌛ Buscando...", value=current)
            ]
        
        return [
            discord.app_commands.Choice(
                name=f"{result['title']} - {result['uploader']}"[:100],
                value=result.get('url'))
                for result in results[:4]
        ]


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
                cancion = await buscar(nombreArtiCancionPlaylistTrack(cliente.track(search)))

                queue[idGuild].append([cancion, channel])

                if not isPlaying[idGuild]:
                    await reproducir(ctx)
                else:
                    await ctx.send(embed=embed_Añadido_Queue(ctx, cancion), silent=True)
            except Exception as e:
                await ctx.send(embed=MensajeBasico("El Token de Spotify Expiro 😶‍🌫️", ROJO))

@elBulloso.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """
        - Registra un evento en los manejadores de errores\n
        para los tree comand para la siguiente corrutina

        ----------------------------

        **Parameters:**
            **interaction:** `(class discord.Interaction)`,
            **error:** `(class discord.app_commands.AppCommandError)`
        
        ----------------------------

        **Returns:**
            `Mensaje en discord indicando que fallo el slash command`
        
        [Mas info sobre tree](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Bot.tree)
        [Mas infor sobre error](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Command.error)
    """
    print("Entro manejo de error SlashCommand")
    await interaction.response.send_message(
        f"❌ Error ejecutando el comando: `{error}`", ephemeral=True
    )

@elBulloso.event
async def on_ready():
    """
    - Evento que se encarga de activarse al momento de que el bot\n
    se conecte al weebhook de discord

    `discord.on_ready`

    [Mas info](https://discordpy.readthedocs.io/en/stable/api.html#discord.on_ready)
    """
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

    # guild=None limpia comandos globales. Si registras por guild_id, debes limpiar con guild=discord.Object(id=GUILD_ID)
    # elBulloso.tree.clear_commands(guild=None)  # Limpia globales
    # print(f"Comandos actualizados y limpiados.")
    elBulloso.bot_loop = asyncio.get_running_loop()
    

    try:
        cliente = spotipy.Spotify(auth_manager=auth_manager)
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
        desconectado_por_codigo[idGuild] = False
    # print(elBulloso.user.mention)
    # try:
    #     comandos_Sincronizados = await elBulloso.tree.sync()
    #     print(f"Se sincronizaron {len(comandos_Sincronizados)} comandos slash")
    # except Exception as e:
    #     print(f"Error al sincronizar comandos: {e}")

    print(f'Inicializando como {elBulloso.user}, SpotifyUsr: {user_name['display_name']} \n Intents Activos: {intents} - Loop registrado')

#Listener para que el bot se desconecte al momento que no hallan usuarios en el canal de voz actual del bot.
@elBulloso.listen()
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """
    - Evento que se activa cuando el estado del bot en un chat de voz cambia

    ----------------------------

    **Parameters:**
        **member:** `(class discord.Member)`, | El usuario del que se debe escuchar si cambia su estado
        **before:** `(class discord.VoiceState)`, | El estado antes del cambio
        **after:** `(class discord.VoiceState)` | El estado despues del cambio

    ----------------------------

    - Desconecta el bot del canal de voz si se queda solo

    - Reconecta el bot si la conexion con el webhook de discord se pierde y luego se reconecta,\n
     Luego reproduce la cancion actual de la queue si hay.

    [Mas info](https://discordpy.readthedocs.io/en/stable/api.html#voice)
    """
    idGuild = int(member.guild.id)
    # Si el bot se queda solo en el canal de voz
    if member.id != elBulloso.user.id and before.channel != None and after.channel != before.channel:
        usuariosEnCanal = before.channel.members
        if len(usuariosEnCanal) == 1 and usuariosEnCanal[0].id == elBulloso.user.id and isInVc[idGuild].is_connected():
            isPlaying[idGuild] = isPaused[idGuild] = False
            queue[idGuild] = []
            queueIndex[idGuild] = 0
            desconectado_por_codigo[idGuild] = True

            await isInVc[idGuild].disconnect()

    # Probando un evento de disconect
    # para revisar si se perido la conexion con el socket
    # Y reconectar y reproducir la cancion automaticamente
    if member.id == elBulloso.user.id and before.channel and not after.channel:
        if desconectado_por_codigo.get(idGuild):
            print("✅ El bot fue desconectado manualmente (por comando).")
            desconectado_por_codigo[idGuild] = False
        else:
            print("❌ El bot fue desconectado inesperadamente (kick, socket error).")
            # Aquí puedes reconectar y continuar
            if queue[idGuild] and queueIndex[idGuild] < len(queue[idGuild]):
                ctx = ctx_por_guild.get(idGuild)
                await asyncio.sleep(2)
                canal = queue[idGuild][queueIndex[idGuild]][1]
                if ctx:
                    await conectarse(elBulloso, canal)
                    await reproducir(elBulloso)
                else:
                    print("⚠️ No hay contexto almacenado para este servidor.")


@elBulloso.event
async def on_close():
    """
        Registra un evento al cliente (Bot)

        [Mas info](https://discordpy.readthedocs.io/en/stable/api.html#discord.Client.event)
    """
    print("Closing Bot..")
    shutdown_executor()

if __name__ == "__main__":
    try:
        elBulloso.run(tokenBot)
    except KeyboardInterrupt:
        shutdown_executor()
        print("⛔️ Cierre manual del bot (Ctrl+C). Recursos liberados.")