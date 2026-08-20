import discord 
from discord import app_commands
from discord.ext import commands
import spotipy, dotenv, yt_dlp, asyncio, functools, datetime, os, sys, pathlib


## import cog

from MusicCog import Music

sys.path.append(str(pathlib.Path(__file__).parent.parent / "Dev2025/modules"))

DOTENV_PATH = pathlib.Path(__file__).parent / '.env'

dotenv.load_dotenv(DOTENV_PATH)

env = dotenv.load_dotenv("bot_dc_py/src/.env")

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/authorize"

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

#enviromentVariables = dotenv_values("bot_dc_py/src/.env")
spClientId= SPOTIFY_CLIENT_ID
spClientSecret= SPOTIFY_CLIENT_SECRET
spApi = "https://api.spotify.com/v1/"
spEndPoint = "/track/{track_id}"
spURI = REDIRECT_URI
spUricall = 'http://google.com/callback/'
tokenBot = DISCORD_TOKEN

scope = """ugc-image-upload,user-read-playback-state,user-modify-playback-state,user-read-currently-playing,
app-remote-control,streaming,playlist-read-private,playlist-modify-public,playlist-read-collaborative,user-read-email,user-read-private
"""

auth_manager = spotipy.oauth2.SpotifyPKCE(client_id=spClientId,redirect_uri=spUricall,scope=scope)
#auth_manager = spotipy.oauth2.SpotifyClientCredentials(client_id=spClientId, client_secret=spClientSecret)
token = auth_manager.get_access_token()
#token = token_dict['access_token']
#cliente = spotipy.Spotify(auth_manager=auth_manager)

try:
    #print(token)
    cliente = spotipy.Spotify(auth=token)
    user_name = cliente.current_user() 
except:
    print("Fallo token")
else:
    #print(json.dumps(user_name, sort_keys=True, indent=4))
    #print(f'token: {token}')
    print('token correcto')


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



@elBulloso.event
async def on_ready():
    try:
    #   print(token)
        cliente = spotipy.Spotify(auth=token)
        user_name = cliente.current_user() 
    except:
        print("Fallo token SpotiPy")
    else:
        #print(json.dumps(user_name, sort_keys=True, indent=4))
        #print(f'token: {token}')
        print('token correcto Spotipy')
    
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

async def main():
    await elBulloso.add_cog(Music(elBulloso))
    await elBulloso.start(tokenBot)

asyncio.run(main())

# elBulloso.add_cog(Music(elBulloso))

# elBulloso.run(tokenBot)