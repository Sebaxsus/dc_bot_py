import discord 
from discord import app_commands
from discord.ext import commands

from math import log10

import spotipy, yt_dlp, asyncio, functools, datetime, concurrent.futures

import discord.ext
from modules.utils import esUrl, is_elbulloso
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



##   Diccionarios para almacenar la id de la Guild (Server) y el status actual del bot

# Diccionario para almacenar el estado de reproduccion (Manual) en un determinado Server con la llave Guild id (int) | - (bool)
isPlaying = {}
# Diccionario para almacenar el estado de Pausa en la reproducción (Manual) en un determinado Server con la llave Guild id (int) | - (bool)
isPaused = {}

# Diccionario para almacenar todas las canciones de un Server con la llave Guild id (int) | - (List[dict cancion, object discord.VoiceChannel])
queue = {}
# Diccionario para almacenar el indice de la cola de reproducción de un Server con la llave Guild id (int) | (int)
queueIndex = {}
# Diccionario para almacenar el discord.VoiceClient de un Server con la llava Guild id (int) | (object discord.VoiceClient)
isInVc = {}

# Diccionario Global de Guild para manejar un objeto discord.Message para poder Limpiar sus reacciones y añadirlas se accede con la llave Guild id (int) | (object discord.Message)
musicMensssageController = {}

# Diccionario Global para manejar las desconxiones manuales (Por codigo) y diferenciarlas de las desconexiones por errores (WebSocket closed with 1006) llave Guild id (int) | (bool)
desconectado_por_codigo = {}
# Diccionario Global para guardar el objeto discord.Context con el fin de manejar las reconexion despues de una desconexion por Socket llave Guild id (int) | (object discord.commands.Context)
ctx_por_guild = {}
# Diccionario Global para guardar la configuracion del servidor en cuanto al volumen de sonido del bot, Utiliza como llave Guild id (int) | (float) Volume setting
volumePreference = {}
# Diccionario global para manejar los datos en cache del autocomple del slashCommand play llave String de busqueda (str) | (list[float (Time created), dict (cancion_metadata)])
autocomplete_cache = {}

CACHE_TTL = 40  # tiempo en segundos para considerar válida una entrada

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

# Options FFMPEG
# -vn --> No procesa video (Ahorro CPU y Memoria)
# -f s16le --> Fuerza el formato de salida a PCM 16-bit little endian.
# -ar 48000 --> Pone la Frecuencia de Muestrueo (Sample Rate) a 48000kHz (Requerido por Discord)
# -ac 2 --> Pone los Audio Channels en 2 (Estereo), 1 (Mono)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn -f s16le -ar 48000 -ac 2',
    }


@elBulloso.hybrid_command(
        name="volume",
        description="Establece el volumen de reproduccion de audio del bot (100 - 0)",
        aliases=["VOLUME","VOL","vol"],
        help="Establece el volumen de reproduccion de audio del bot (100  - 0)"
)
@app_commands.describe(vol="Volumen porcentual al que quieres establecer el bot")
async def volume(ctx: commands.Context, vol: float):
    """
    Se encarga de establecer el valor del Diccionario global
    `volumePreference`

    El 100% es 1.0 y el 0% es mas o menos 0.00

    ---------------------

    **Parameters:**
        **ctx:** `(object discord.commads.Context)`
        **vol:** `(float)`
    
    ---------------------

    **Returns:**
        `Establece el valor de vol en el diccionario volumePreference`

    """

    idGuild = ctx.guild.id
    # Como el valor vol puede venir del autocomplete puede ser un str entonces fuerzo a que lo convierta a float
    vol = float(vol)

    # print("Entro a cambio de volumen: ", vol, "Is Expired?:", ctx.interaction.is_expired(), "Is Responded?: ", ctx.interaction.response.is_done())
    # Si se llamo a Volume por una interaccion y No se ha respondido.
    if ctx.interaction and not ctx.interaction.response.is_done():
        # Responde la interaccion con un "Dejeme trabajar" entonces resulve la interaccion
        # Las respuestas siguientes se haran con interaction.followup
        await ctx.interaction.response.defer(thinking=True)

    # Si el porcentaje del volumen esta por encima de 100 o por debajo de 0
    if (vol > 100 or vol < 0):
        await ctx.send(
            mention_author=True,
            content=":Rage:\nEl volumen debe estar entre 100 y 0\n!No Puede Ser Mayor a 100 o Negativo!",
            silent=True,
            delete_after=60  
        )
        return
    
    # Guardando el valor porcentual antes de convertirlo en logaritmico
    porcentaje = vol
    # Conviertiendo el Volumen de Porcentual a Logaritmico.
    if vol < 1:
        vol = 10 ** ((0 - 100) / 40)
    else:
        vol = 10 ** ((vol - 100) / 40)

    if isInVc[idGuild]:
        # Si el bot esta reproduciendo sonido en un canal de voz
        if (isInVc[idGuild].is_playing()):

            # print(f"Es el source actual una instancia de PCMVolume: {type(isInVc[idGuild].source)}")
            # Si la fuente del sonido es una instancia de la clase discord.PCMVolumeTransforme
            # Si no lo es no podre cambiar el volumen del sonido en tiempo real.
            if isinstance(isInVc[idGuild].source, discord.PCMVolumeTransformer):

                # print(f"Volumen anterior: {isInVc[idGuild].source.volume}, Volumen Nuevo: {vol}")
                # Lo de abajo es lo mismo que discord.PCMVolumeTransformer.source.volume = vol
                isInVc[idGuild].source.volume = vol

            else:
                await ctx.send("No se pudo cambiar el volumen 😓", silent=True, delete_after=30)
                print("El source actual no permite cambiar el volumen dinámicamente.")
    else:
        print("El bot no esta dentro de un canal de voz")
    
    bloques_llenos = int((porcentaje / 100) * 10)
    bloques_vacios = 10 - bloques_llenos

    await ctx.send(embed=MensajeBasico(
            titulo="🎵 **Volumen Ajustado**",
            texto=f"🔊 [{"🟪" * bloques_llenos}{"⬛" * bloques_vacios}] {porcentaje} %",
            color=DARK_GREEN
        ),
        silent=True,
        delete_after=45
    )

    volumePreference[idGuild] = vol

    print(f"🔊 Se establecio el volumen a {porcentaje} %, Valor Log: {vol}")

# Current hace referencia a lo que el usuario escribio en el Arg
@volume.autocomplete("vol") 
async def volume_autocomplete(interaction: discord.Interaction, current: str):
    """
    Convierte un valor porcentual en un volumen lineal de decibeles
    usando la formula inversa del decibelio

    ¿Por que el sonido no es Linea?

    El oido humano no percibe el sonido linealmente, En vez de eso, responde logarítmicamente
        - Si se duplica la energía (Ejemplo de 0.5 a 1.0 en .volume), no se escucha "el doble" de volumen
        - Para que algo suene el doble de fuerte **Perceptivamente**, Se necesita multiplicar el sonido dB unas **4 veces**

    volumen lineal ≈ 10 ^ (dB / 40)

    Formula Inversa para estimar los dB desde un percepcion Humana (Estimado)

        dB ≈ 20 * log10 (volumen_percibido / 100)

        Ejemplo:
            50% percepción ≈ 20 * log10(50/100) ≈ -6.02 dB
            Por ende -6.02 dB ≈ 10 ^ (-6.02 / 40 ) ≈ 0.5
            20 * log10(20/100) ≈  -14 dB ≈  10 ^ (-14/20) ≈ 0.2
            20% percepción ≈ -14 dB → volume ≈ 0.2

        Para sacar el 20% se usa
            10 ^ ((20 - 100) / 40) ≈ 0.01

    Percepción Humana	Valor Lineal (.volume)
        100%      ->         (original)1.0
        50%	      ->             0.056
        40%	      ->             0.031
        30%	      ->             0.017
        20%	      ->             0.01

    Ejemplo:
    50% percepción ≈ -6 dB → volume ≈ 0.056

    20% percepción ≈ -14 dB → volume ≈ 0.017
    """

    try:
        idGuild = interaction.guild.id

        # Escalado logarítmico
        # VolLog = 10 ^ ( (porcentaje - 100) / 40)
        # porcentaje =   (10 ^ VolLog) * 40
        volumenActual = volumePreference[idGuild]

        porcentajeVolumenActual = 40 * log10(volumenActual) + 100

        # Le agrego de primeras en la lista, Para que aparezca de primeras en Discord.
        listaPorcentajes = [
            discord.app_commands.Choice(
                name=f"Volumen Actual: {porcentajeVolumenActual} %",
                value=f"{porcentajeVolumenActual}"
            )
        ]

        # Si la entrada es un tipo float, Significa que no se ha puesto nada
        if type(current) == float:
            # Como no hay todavia una entrada por el usuario utilizo 
            # el porcentajeActual para los condicionales de abajo
            current = porcentajeVolumenActual
            # Agrego a la Lista objetos discord.Choice que va de 100 hasta 0 con saltos de 10
            for valor in range(100, -1, -10):
                listaPorcentajes.append(
                    discord.app_commands.Choice(
                        name=f"{valor} %",
                        value=valor
                    )
                )
        else:
            # Como ya se que el usuario escribio algo
            # Elimino los espacios y escojo solo la primera parte (Numeros se supone)
            current = float(current.split()[0])
            # Agrego a la Lista objectos discord.Choice que va desde el numero que puso el usuario hasta 0 con salto de 10
            for valor in range(int(current), -1, -10):
                listaPorcentajes.append(
                    discord.app_commands.Choice(
                        name=f"{valor} %",
                        value=valor
                    )
                )
        
        # print(f"Verificando que es current: {current} | {type(current)}.\nporcentajeActual: {porcentajeVolumenActual} | valorActual: {volumenActual}")
        # Verifico que el numero que uso el usuario este dentro el rango de 100 a 0
        if (current < 100 or current > 0) or current:
            
            return listaPorcentajes
        else:
            listaPorcentajes.insert(0, discord.app_commands.Choice(
                    name="‼️ Tiene que ser un valor entre 0 y 100",
                    value=f"{porcentajeVolumenActual}"
                )
            )
            return listaPorcentajes
    except Exception as e:
        print(f"Fallo el autocomplete de volume\n {e}")
        return [
            discord,app_commands.Choice(
                name="⚠️ Estoy experimentando Errores 😓, Asegurate de usar numeros",
                value=f"{porcentajeVolumenActual}"
            )
        ]

@elBulloso.hybrid_command(
    name="purge",
    description="Purga todos los mensaje de el bot en un canal de texto. | No discrimina mensajes!!.",
    aliases=["PURGE"],
    help="Comando para Purga todos los mensaje de el bot en un canal de texto.",
)
async def purge(ctx: commands.Context):
    """
    Se encarga de purgar el canal de texto en donde
    se origino el comando.

    Se creo para limpiar los canales de bots y mantenerlos mas
    limpios de tanto mensaje basura.

    AL terminar de limpiar devuelve un mensaje contextual
    Con la cantidad de mensajes que elimino.

    **IMPORTANTE**

    Actualmente por razones de limpieza la purga
    **NO** discrimina entre mensajes solo elimina
    los primeros veinte.

    ---------------------

    **Parameters:**
        **ctx:** `(object commands.Context)`
    
    ---------------------

    **Returns:**
        `Mensaje en Discord tipo embed`

    ---------------------

    [Mas info sobre Purge](https://discordpy.readthedocs.io/en/latest/api.html?highlight=get%20channel#discord.TextChannel.purge)
    [Mas info sobre send](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=send#discord.ext.commands.Context.send)
    """
    # print(f"Channel data: \nNombre:{channel.name}\nCantidad de Mensajes: {channel}\nCantidad de usuario en el: {channel}\nid: {channel.id}\nEl ultimo mensaje es de el bulloso: {is_elbulloso(channel.last_message)}")
    channel = ctx.channel
    deleted = await ctx.channel.purge(limit=20, reason=f"Limpiando el Canal de Texto: ${channel.name}")
    await channel.send(embed=MensajeBasico(
        titulo=f"⚠️ Se purgo el canal {channel.name} :cold_face:",
        texto=f"Se purgaron {len(deleted)} mensajes :shushing_face:",
        color=DARK_RED,
        ),
        silent=True,
        delete_after=30,
    )

async def addMusicMessageController(mensaje: discord.Message, idGuild: int):
    """
    Se encarga de obtener un Objeto del tipo (class discord.Message),
    Para añadirle las reacciones de control de reproductor de musica

    🔽, ◀️, ⏯️, ▶️, 🔼

    ---------------------

    **Parameters:***
        **mensaje:** `(object discord.Message)`

    ---------------------

    **Returns:**
        `None`

    ---------------------

    [Mas info sobre message reactions](https://discordpy.readthedocs.io/en/latest/api.html#message)
    """

    # Todo 
    # Verificar si hay canciones previas (Anteriores), En caso de que si mostrar el icono de atras  ◀️
    # Verificar si hay canciones siguientes (Mas canciones), En caso de que si mostrar el icono de ▶️

    # print(f"Entro addMusicMessageController Message ID: {mensaje.id}\n\tGuild id: {idGuild}")

    # Inicializo la variable que contiene la lista de emjois a agregar
    emojis = ["🔽","⏯️","🔼"]

    # Limpio cualquier reaccion posible dentro del mensaje
    await mensaje.clear_reactions()

    # Si el indice actual es mayor a 0 y la cola tiene al menos 2 canciones
    if (queueIndex[idGuild] > 0 and len(queue[idGuild]) > 1):
        # Inserto el emoji al principio para asegurar consistencia en el UX y UI
        emojis.insert(1, "◀️")

    # Si la cantidad de canciones en cola es mayor a 1 y el indice actual de la cola + 1 es menor a la cantidad de canciones en cola
    # El + 1 en el indice de cola de reproduccion se debe a que la cola de reproduccion utiliza indices empezando por 0 pero
    # len() devuelve la cantidad de canciones empezando por 1.

    # Esencialmente de podira hacer un len() - 1 pero no cambia en nada creo.
    if (len(queue[idGuild]) > 1 and (queueIndex[idGuild] + 1) < len(queue[idGuild])):
        # Inserto el emoji al fondo para asegurar consistencia en la UI y UX
        emojis.insert(-1,"▶️")

    # Le agrego las reacciones al mensaje
    # print("Emojis Antes de agregar al mensaje", emojis)
    for emoji in emojis:
        await mensaje.add_reaction(emoji)

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
        await ctx.send(embed=MensajeBasico("❌ Error", "No se pudo obtener ninguna canción válida del playlist", ROJO),silent=True,delete_after=60)
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
        await ctx.send(embed=MensajeBasico("❌ Error", "No se pudo obtener ninguna canción válida del playlist", ROJO),silent=True,delete_after=60)
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
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
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
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
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
    embed.set_footer(text=f'Cancion de: {str(usuario)}', icon_url=pfp)
    embed.set_author(name=f"{Canal}")
    return embed

async def mensaje(ctx: commands.Context, cancion: dict) -> discord.Message:
    """
    - Manda un mensaje de tipo embed al chat de discord\n
     con los metadatos de una cancion.

    ----------------------------

    **Parameters:**
        **ctx:** `(class discord.ext.commands.Context)`,
        **cancion:** `(dict)`
    
    ----------------------------

    **Returns:**
        `(object dicord.Message)`
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
        return await ctx.send(embed=em, silent=True)
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
        await ctx.send(f'Pong :ping_pong:', silent=True, delete_after=30)
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
            silent=True,
            delete_after=60
        )
    
    await ctx.send(
        f"Pong {user.mention} :ping_pong:",
        silent=True,
        delete_after=30
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
    await ctx.send(embed=embed, silent=True, delete_after=180)

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
            silent=True,
            delete_after=45
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
            silent=True,
            delete_after=45
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
        mensaje = f"- *[{cancion['Titulo']}]({cancion['link']})*\n- *{cancion['Canal']}* | `{cancion['Duracion']}`" if returnIndex == 0 else (f"- *[{cancion['Titulo']}]({cancion['link']})*\n- *{cancion['Canal']}* | `{cancion['Duracion']}`\n------------")
        colaEmbed.add_field(
            name=titulo,
            value=mensaje,
            inline=False
        )

    colaEmbed.set_footer(text=f"`🎶 Total de canciones en cola: {totalSongs}`")
    await ctx.send(
        embed=colaEmbed,
        silent=True,
        delete_after=300,
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

        await ctx.send(embed=embedClear, silent=True, delete_after=45)
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
    #Limpiando el estado del musicMensssageController
    musicMensssageController[idGuild] = None

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
            silent=True,
            delete_after=60
        )
        return
    
    if cancion is None:
        cancion = queue[idGuild][-1][0]

    index = next((i for i, item in enumerate(queue[idGuild]) if item[0]['Title'] == cancion), None )

    if index is None:
        await ctx.send("❌ Canción no encontrada en la cola.",delete_after=60)
        return
    
    eliminada = queue[idGuild].pop(index)
    await ctx.send(
        embed=embed_Eliminado_Queue(ctx, eliminada[0]),
        silent=True,
        delete_after=45
    )

    if not queue[idGuild] and isInVc[idGuild]:
        desconectado_por_codigo[idGuild] = True

        await isInVc[idGuild].disconnect()
        # Limpiando cualquier posible cache residiual de la
        # Instancia de conexión
        await isInVc[idGuild].cleanup()

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
            silent=True,
            delete_after=60
        )

    elif not queue[idGuild]:

        await ctx.send(
            embed=MensajeBasico(
                "**No se pudo Pausar :face_exhaling: **",
                "No se puede pausar una cancion\nSi no hay canciones en la cola.",
                ROJO
            ),
            silent=True,
            delete_after=60
        )

    elif isPlaying[idGuild]:

        await ctx.send(
            embed=MensajeBasico(
                "**Pausando! :sleeping: **",
                "Pausando la cancion!.",
                DARK_GREEN
            ),
            silent=True,
            delete_after=30,
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
            silent=True,
            delete_after=60,
        )
    elif not queue[idGuild]:

        await ctx.send(
            embed=MensajeBasico(
                "**No se pudo reanudar :nerd: **",
                "No hay canciones por reproducir.",
                ROJO
            ),
            silent=True,
            delete_after=60
        )

    elif isPaused[idGuild]:
        await ctx.send(
            embed=MensajeBasico(
                "**Reanudando! :upside_down: **",
                "Reanudando la cancion!.",
                DARK_GREEN
            ),
            silent=True,
            delete_after=30
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
    # print(f"Logger del skip, numero de skips {cancion}, Numero de canciones en cola: {len(queue[idGuild])}, Indice actual de la cola: {queueIndex[idGuild]}")
    #cancion = queue[idGuild][queueIndex[idGuild]][0]
    if isInVc[idGuild] == None:
        await ctx.send(
            ctx.author.mention,
            embed=MensajeBasico(
                "**No se pudo skipear :nerd: **",
                f"{ctx.author.mention} El bulloso Necesita estar en un canal de voz para usar ester comando!",
                DARK_RED
            ),
            silent=True,
            delete_after=60
        )
        return
    
    if not queue[idGuild] or queueIndex[idGuild] >= len(queue[idGuild]):
        await ctx.send(
            embed=MensajeBasico(
                "**No hay canciones en la cola! :dizzy_face: **",
                f"No puede saltar mas canciones de las que hay en la cola\n**Canciones en cola: `{len(queue[idGuild])}`**",
                DARK_PURPLE
            ),
            silent=True,
            delete_after=45
        )
        return
    
    # Skip a una cancion en especifico | Si cancion es distinto a None
    if cancion is not None:
        # Obtengo el Indice proporcionado por el usuario
        index = int(cancion)
        # Si el Indice proporcionado por el usuario es mayor o igual que la cantidad de canciones empezando en 0
        # O
        # El Indice proporcionado por el usuario es menor al indice actual de la Cola
        if index >= len(queue[idGuild]) or index <= queueIndex[idGuild]:
            await ctx.send(
                embed=MensajeBasico(
                    "** Indice de canción no válido o ya reproducido! :dizzy_face: **",
                    f"No puede saltar mas canciones de las que hay en la cola\n**Canciones en cola: `{len(queue[idGuild])}`**",
                    DARK_PURPLE
                ),
                silent=True,
                delete_after=60
            )
            return
        
        # En caso de que sea un Indice valido
        queueIndex[idGuild] = index
    else:
        queueIndex[idGuild] += 1

    await ctx.send(
        embed=MensajeBasico(
            titulo=f"Saltando a {queue[idGuild][queueIndex[idGuild]][0].get("Titulo")}!",
            texto=f"Se salto a la cancion numero {queueIndex[idGuild]}",
            color=TEAL
        ),
        silent=True,
        delete_after=30
    )
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
    # print(f"Log Previus, indice de cancion a devolverse: {cancion}, Indice actual de la cola: {queueIndex[idGuild]}\n bot: {elBulloso.user.global_name} | {ctx.author} | {ctx.bot}\nIs Expired?: {ctx.interaction.is_expired()} | Is Respondend?: {ctx.interaction.response.is_done()}")
    if ctx.interaction and not ctx.interaction.response.is_done():
        await ctx.interaction.response.defer(thinking=True)
    #cancion = queue[idGuild][queueIndex[idGuild]][0]

    try:
        if isInVc[idGuild] == None:

            await ctx.send(
                embed=MensajeBasico(
                    "**Suaga ahi sog :face_with_diagonal_mouth: **",
                    f"{ctx.author} Necesita estar en un canal de voz para usar este comando!",
                    DARK_RED
                ),
                silent=True,
                delete_after=60
            )
            return
        
        if not queue[idGuild]:
            await ctx.send(
                embed=MensajeBasico(
                    "** Cola Vacia :open_mouth: **",
                    "No hay canciones a las que volver",
                    DARK_RED
                ),
                silent=True,
                delete_after=45
            )
            return

        if cancion is not None:
            index = int(cancion)
            if index >= queueIndex[idGuild]:
                await ctx.send(
                    "** Trateme mas que serio **",
                    "Esa cancion esta sonando o aun no ha sonado",
                    silent=True,
                    delete_after=60
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
                    silent=True,
                    delete_after=30
                )
                # Lo pausé para volver a reproducirlo con reproducir en el indice actual
                isInVc[idGuild].pause()
                await reproducir(ctx)
                return
                #await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion))
            else:
                # Reduciendo el indice si se hizo previus sin numero, y hay al menos una cancion anterior  
                queueIndex[idGuild] -= 1

        if ctx.interaction:
            try:
                await ctx.send(
                    embed=MensajeBasico(
                        titulo=f"Devolviendose a {queue[idGuild][queueIndex[idGuild]][0].get("Titulo")}!",
                        texto=f"Se devolvio a la cancion numero {queueIndex[idGuild]}",
                        color=TEAL
                        ),
                        silent=True,
                        delete_after=30
                    )
            except Exception as e:
                print(f"Fallo el interaction Follow Up previus\nError: {e}")
        
        isInVc[idGuild].pause()
        await reproducir(ctx)
        
    except Exception as e:
        await ctx.send(f"❌ Ocurrió un error", ephemeral=True)
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

async def siguienteCancion(ctx: commands.Context, mensajeAnterior: discord.Message):
    #print("\nEntro a siguiente cancion")
    idGuild = int(ctx.guild.id)

    # print(f"Message ID: {mensajeAnterior.id}\n\t Reactions: {mensajeAnterior.reactions}")
    # Limpio las reacciones del Mensaje Anterior.
    await mensajeAnterior.clear_reactions()
    # Elimino el mensaje anterior
    # await mensajeAnterior.delete()

    if not isPlaying[idGuild]:
        # print("Entro a no esta reproducciendo musica")
        return
    # Si la el indice de la cola actual + 1 es menor a la cantidad de canciones en la cola
    if queueIndex[idGuild] + 1 < len(queue[idGuild]):
        # print("Entro a si hay siguiente cancion")
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

        mensajeEnviado = await mensaje(ctx, cancion)

        await addMusicMessageController(mensaje=mensajeEnviado, idGuild=idGuild)

        # Sobre-escribo/Guardo el Objeto discord.Message en el diccionario de estado musicMensssageController llave idGuild
        musicMensssageController[idGuild] = mensajeEnviado

        #print("anted de await ctx.send en linea 267")
        #await ctx.send(embed= embed_Reproduciendo_Ahora(ctx, cancion))
        #print(f"Source: {cancion['Source']}")
        source = discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS)

        # Checking if the audio source is Opus
        # print(f"Source is opus? {source.is_opus()} \n\tPre-Cambio VOl {type(source)}")

        source = discord.PCMVolumeTransformer(source, volume=volumePreference[idGuild])

        # Checking Volume Changes on the source
        # print(f"Usando source: {type(source)}")
        # if isinstance(source, discord.PCMVolumeTransformer):
        #     print(f"Volumen aplicado: {source.volume}")

        isInVc[idGuild].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(siguienteCancion(ctx, mensajeAnterior=mensajeEnviado), elBulloso.bot_loop))
        #isInVc[idGuild].source = discord.PCMVolumeTransformer(isInVc[idGuild].source, 0.5)
    else:
        # print("Entro a no hay mas canciones")
        # Se supone que ya no hay mas canciones en la cola entonces entra aqui
        # Por eso entonces limpio la cola
        queueIndex[idGuild] = 0
        queue[idGuild] = []
        isPlaying[idGuild] = False
        musicMensssageController[idGuild] = None
        await ctx.send(
            embed=MensajeBasico(
                "**Se termino la cola de reproduccion! :frowning2: **",
                "Limpiando la cola de reproduccion",
                DARK_GREEN
            ),
            silent=True,
            delete_after=100
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
        
        ----------------------------

        [Mas info HybridCommands](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#hybridcommand)

        [Mas info sobre FFmpegPCMAudio](https://discordpy.readthedocs.io/en/stable/api.html#ffmpegpcmaudio)
    """
    idGuild = int(ctx.guild.id)
    # print(f'entro a reproducir queIndex: {queueIndex[idGuild]} queue: {len(queue[idGuild])}, channel: {queue[idGuild][queueIndex[idGuild]][1]}')

    # Maneja el raro caso en donde entre a reproducir pero ya esta reproduciendo audio
    # y los diccionarios de estados no reflajan esto jajaj 😓
    if isInVc[idGuild].is_playing():
        return
    
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

        # Si hay un mensajeAnterior Guardado en la Guild le limpio las reacciones, Si no no hago nada.
        await musicMensssageController[idGuild].clear_reactions() if musicMensssageController[idGuild] else None
        
        # Guardando el Objeto discord.Message que referencia al mensaje de reproduciendo ahora.
        mensajeEnviado = await ctx.send(embed=embed_Reproduciendo_Ahora(ctx, cancion), silent=True)

        await addMusicMessageController(mensaje=mensajeEnviado, idGuild=idGuild)

        # Guardo el Objeto discord.Message en el diccionario de estado musicMensssageController llave idGuild
        musicMensssageController[idGuild] = mensajeEnviado


        source = discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS)

        # Checking if the audio source is Opus
        # print(f"Source is opus? {source.is_opus()} \n\tPre-Cambio VOl {type(source)}")

        ## ******************************* Probando el PCMVolumeTransformer
        source = discord.PCMVolumeTransformer(source, volume=volumePreference[idGuild])
        ## ****************************************************************************
        # Checking Volume Changes on the source
        # print(f"Usando source: {type(source)}")
        # if isinstance(source, discord.PCMVolumeTransformer):
        #     print(f"Volumen aplicado: {source.volume}")

        isInVc[idGuild].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(siguienteCancion(ctx, mensajeAnterior=mensajeEnviado), elBulloso.bot_loop))
        #print(f"Source: {cancion['Source']}")
        #isInVc[idGuild].play(discord.FFmpegPCMAudio(
        #    cancion['Source']), after=lambda e: siguienteCancion(ctx)
        #)
        #isInVc[idGuild].source = discord.PCMVolumeTransformer(isInVc[idGuild].source, 0.5)
        #print("Antes de siguente cancion")
    else:
        await ctx.send(embed=MensajeBasico("**Cola Vacia! :melting_face: **","No hay mas canciones en la cola de reproduccion",DARK_PURPLE), silent=True)
        # Limpio la cola de reproducción y Reinicio el Estado del índice de la Cola a 0, Para que en caso de usar play sin args no intente reproducir nada
        queueIndex[idGuild] = 0
        isPlaying[idGuild] = False
        musicMensssageController[idGuild] = None
        # Esto se cambio en el Commit 5d22e40e54452918a6db1669ed9b0bb3230ef889

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
        try:
            # Estableciendo un tiempo en segundos a esperar que se complete el Handshake o Conexión
            # Activando la flag para reconexión
            isInVc[idGuild] = await channel.connect(timeout=2,reconnect=True)
            em = discord.Embed(
                title=f"**Conectado a {ctx.author.voice.channel}**",
                description=f"Peticion de union hecha por {ctx.author.mention}",
                colour=VERDE
            )
            em.set_footer(icon_url=elBulloso.user.display_avatar)
            await ctx.send(embed=em, silent=True)
            if isInVc[idGuild] == None:
                await ctx.send(
                        embed=MensajeBasico(
                            "**A lo bien :middle_finger: **",
                            "No me pude conectar al canal de voz\nDebe estar en un canal de Voz",
                            ROJO
                        ),
                        silent=True,
                        delete_after=120,
                    )
                return
        except discord.ClientException:
            # En caso de que falle el conectarse, Limpio cualquier posible cache de
            # La Instancia/Objecto discord.VoiceClient usando el metodo `cleanup()`
            # y `disconnect(force=True)`
            if isInVc.get(idGuild):
                try:
                    await isInVc[idGuild].disconnect(force=True)
                except Exception as e:
                    print(f"[ERROR] Fallo la desconexion despues de una excepción en la conexion Error: {e}")

                await isInVc[idGuild].cleanup()
                isInVc[idGuild] = None
            # discord.errors.ConnectionClosed: Shard ID None WebSocket closed with 4006
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
        await ctx.send(user, silent=True, delete_after=420)

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
    await ctx.send(f'{objetoUser.mention}, Id: {objetoUser.id} Nombre: {objetoUser.global_name}', silent=True, delete_after=60)

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
        await ctx.send(embed=MensajeBasico("**Sea serio pa! :clown: **",f'Tiene que estar en un canal de voz para unirme.',ROJO), silent=True, delete_after=60)


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

        await ctx.send(embed=em, silent=True, delete_after=60)
        # Desconectando y Limpiando cualquier posible Cache
        # De la Instancia `discord.VoiceClient`
        try:
            await isInVc[idGuild].disconnect()
        except Exception as e:
            print(f"[Error] Fallo la desconexion del cliente, Error: {e}")

        await isInVc[idGuild].cleanup()

        ctx_por_guild.pop(ctx.guild.id, None)
        isInVc[idGuild] = None
    else:
        await ctx.send(f"❌ No estoy conectado a ningún canal de voz. {ctx.author.mention} Sapa :middle_finger:", silent=True, delete_after=60)


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
            await ctx.send(embed=embed_Añadido_Queue(ctx, cancion), silent=True, delete_after=60)
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

    # Inicializando Cancion para que en el caso de fallo de busqueda y condiciones Exista y tenga un valor de None
    cancion = None

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
        await ctx.send(
            ctx.author.mention,
            embed=em,
            silent=True,
            delete_after=60,
        )
        return
    
    if not search or search is None:
        if len(queue[idGuild]) == 0:
            await ctx.send(
                    embed=MensajeBasico(
                        "**Cola Vacia! :face_with_monocle: **",
                        "No hay canciones en la cola\n\nIngrese un link o una cancion para buscarla",
                        DARK_RED
                    ),
                    silent=True,
                    delete_after=80
                )
            return
        elif not isPlaying[idGuild]:
            if queue[idGuild] == None:
                print("Entro no esta Reproduciendo musica y no hay queue")
                #isPlaying[idGuild] = False       Si se da;a algo activar esto
                if ctx.interaction:
                    await ctx.interaction.followup.send(
                        embed=MensajeBasico(
                            "**No hay canciones en Cola :rage:**",
                            "No hay canciones en la cola\n\nIngrese un link o una cancion para buscarla",
                            DARK_RED
                        ),
                        ephemeral=True, # Solo visible para el usuario
                        silent=True
                    )
                else:
                    await ctx.send(
                        embed=MensajeBasico(
                            "**No hay canciones en Cola :rage:**",
                            "No hay canciones en la cola\n\nIngrese un link o una cancion para buscarla",
                            DARK_RED
                        ),
                        silent=True,
                        delete_after=80
                    )
            elif isInVc[idGuild] == None and len(queue[idGuild]) > 0:
                print("Entro a no esta Reproduciendo y no esta en un Chat de voz y hay almenos una cancion en Queue")
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
                    await ctx.send(embed=MensajeBasico("❌ **No se pudo obtener el track**", "Fallo el buscar la track de Spotify", ROJO), silent=True, delete_after=120)
                    return
            case "youtube_video":
                search = veriSearch[1]
                try:
                    cancion = await obtener_stream(search)
                    if not cancion:
                        raise ValueError("No se encontró la canción")
                except Exception as e:
                    await ctx.send(embed=MensajeBasico("❌ **Error al buscar**", "Fallo el buscar video por link de Youtube", ROJO), silent=True, delete_after=120)
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
                    await ctx.send(embed=MensajeBasico("❌ **Error al buscar**", "Fallo el buscar video por titulo o nombre", ROJO), silent=True, delete_after=120)
            case _:
                await ctx.send(embed=MensajeBasico("**Uy cual es esa :rage: **",f"Que mierda buscate sapa {ctx.author.mention}", ROJO), silent=True, delete_after=60)
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

        # print(f"Play before addMusicMessageController\n\tmusicMessageController? {not musicMensssageController[idGuild]}")

        if not cancion or not isinstance(cancion, dict) or 'Titulo' not in cancion:
            await ctx.send(
                    embed=MensajeBasico(
                        "**Uy cual es esa :rage: **",
                        f"Que mierda buscate sapa {ctx.author.mention}\nVuelva a Intentar Buscar y revise que uso!",
                        ROJO
                    ),
                    silent=True,
                    delete_after=120,
                )
            return
        else:
            if veriSearch and veriSearch[0] in ["spotify_album", "spotify_playlist", "youtube_playlist"]:
                # Ternaria | Bloque_Ejecucion_True if condicion else Bloque_Ejecucion_False
                # Si musicMensssageController[idGuild] es distinto a None True else None
                await addMusicMessageController(musicMensssageController[idGuild], idGuild) if musicMensssageController[idGuild] else None
            else:
                queue[idGuild].append([cancion, channel])
                await addMusicMessageController(musicMensssageController[idGuild], idGuild) if musicMensssageController[idGuild] else None

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
        musicMensssageController[idGuild] = None
        volumePreference[idGuild] = 0.05623413251903491 # ≈ 50%

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
            try:
                await isInVc[idGuild].disconnect()
            except Exception as e:
                print(f"[ERROR] Fallo la desconexion del cliente, Error: {e}")
            # Esto es para que se limpie el cache de la conexion asi tratando de evitar
            # El error de Conexión 4006
            await isInVc[idGuild].cleanup()

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

@elBulloso.listen()
async def on_raw_reaction_add(payload):
    """
    Se encarga de escuchar los mensajes de los canales de texto y si se añade
    una reaccion a un canal de texto se activa

    Payload tiene los siguiente atribs:
        **message_id** `(int)`

        **user_id** `(int)`

        **channel_id** `(int)`

        **guild_id** `(int)`

        **emoji:** 
            animated `(bool)`,
            name `("Emoji Unicode")`,
            id `(IDK returns None)`

        **event_type** `(str ["REACTION_ADD", "REACTION_REMOVE"])`

        **member** `(class discor.Member)` 
            id `(int)`,
            name `(str)`,
            global_name `(str)`,
            bot `(bool)`,
            guild `(class discord.Guild)` 
                id `(int)`,
                name `(str)`,
                shard_id `(int)`,
                chunked `(bool)`,
                member_count `(int)`

        **message_author_id** `(int)`

        **burst** `(bool)`

        **burst_colours** `(list)`

        **type** `(class ReactionType.normal??)` type=<ReactionType.normal: 0>

        ---------------------

        [Mas info sobre este Evento](https://discordpy.readthedocs.io/en/latest/api.html#discord.on_raw_reaction_add)
        [Mas info sobre payload](https://discordpy.readthedocs.io/en/latest/api.html#discord.RawReactionActionEvent)
        [Mas info sobre get_channel](https://discordpy.readthedocs.io/en/latest/api.html#discord.Client.get_channel)
        [Mas info sobre fetch_message](https://discordpy.readthedocs.io/en/latest/api.html?highlight=get%20channel#discord.TextChannel.fetch_message)
        [Mas info sobre los mensajes y las reacciones](https://discordpy.readthedocs.io/en/latest/api.html#message)
    """
    # print(f"Paylaod Event raw reaction add\n Payload: {payload}\n\tMessage ID: {payload.message_id}\n\tuser ID: {payload.user_id}\n\tChannel ID: {payload.channel_id}\n\tEmjoi: {payload.emoji}\n\tEvent Type: {payload.event_type}\n\t")
    # "◀️", "⏯️", "▶️"
    try:
        idGuild = payload.guild_id

        # Si no hay contexto global o no esta en un Canal de voz no haga nada
        if (not isInVc[idGuild] or not ctx_por_guild.get(idGuild)):
            return

        # Obteniendo los datos del mensaje en el cual se añadió una reacción.
        message = await elBulloso.get_channel(payload.channel_id).fetch_message(payload.message_id)
        # print(f"{message.author} | Bot user: {elBulloso.user} | isBOt?: {payload.member.bot} | user_name: {payload.member.name} | user_id: {payload.user_id} | bot_id: {elBulloso.user.id}")
        
        # Si la reaccion biene de un bot o el bulloso no haga nada
        if (payload.member.bot or payload.user_id == elBulloso.user.id):
            return
        
        # Verificando si el autor de ese mensaje fue elBulloso.
        if (message.author == elBulloso.user):
            # Obteniendo el unicode del Emoji el cual se añadio a las reacciones de el mensaje.
            emoji = payload.emoji
            
            # Obteniendo el contexto global almacenado por guild.
            ctx = ctx_por_guild.get(idGuild)

            # Limpiando la reaccion del usuario, Con su argumento member usando el usuario de la reaccion como member
            await message.remove_reaction(emoji, payload.member)
            # \n\t{str(emoji) == "▶️"}
            # print(f"🔔 Se activo el event listener **Se agrego una reaccion**\n\temoji: {emoji}")


            match str(emoji):
                case "◀️":
                    await previus(ctx)
                case "⏯️":
                    if isInVc[idGuild].is_playing():
                        await pause(ctx)
                    else:
                        await resume(ctx)
                case "▶️":
                    await skip(ctx)
                case "🔽":
                    volumen = 40 * log10(volumePreference[idGuild]) + 100

                    if (volumen - 10 < 1):
                        volumen = 0
                    else:
                        volumen = volumen - 10

                    await volume(ctx, volumen)
                case "🔼":
                    volumen = 40 * log10(volumePreference[idGuild]) + 100

                    if (volumen + 10 < 1):
                        volumen = 0
                    else:
                        volumen = volumen + 10
                    await volume(ctx, volumen)
                case _:
                    # Si no esta dentro de estos casos elimino esa reacción del mensaje.
                    # Luego termino la ejecucion. 👍
                    await message.remove_reaction(emoji, payload.member)
                    return
    except Exception as e:
        print("Fallo el listener on add reaction\n",e)
        return
    
    # print(message)

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