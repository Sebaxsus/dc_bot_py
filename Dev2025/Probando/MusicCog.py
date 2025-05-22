import discord
from discord import app_commands
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio

# Clases/Modulos 
from modules.utils import MensajeBasico, format_audio_seconds, esUrl

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

#Colores embed Azul= 0x2c76dd, Rojo= 0xdf1141, Verde= 0x0eaa51
AZUL,ROJO,VERDE,DARK_PURPLE,DARK_BLUE = 0x2c76dd, 0xdf1141,0x0eaa51,0x71368A,0x206694
TEAL,DARK_RED,DARK_GREEN = 0x1ABC9C, 0x992D22,0x1F8B4C

class Music(commands.Cog):
    def __init__(self, bot):
        print("Inicio Cog", bot.user)
        self.bot = bot
        self.isPlaying = {}
        self.isInVc = {}
        self.isPaused = {}
        self.queue = {}
        self.queueIndex = {}
        # self.bot_pfp = bot.user.display_avatar
    
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

    def search_youtube(self, query):

        with YoutubeDL(ydl_options) as ydl:
            data = ydl.extract_info(query, download=False)

            if 'entries' in data:
                return data['entries'][:5]
            return [data]
        
    def extract_playlist(self, url):

        with YoutubeDL(ydl_options) as ydl:

            info = ydl.extract_info(url, download=False)
            return info['entries']
        
    def buscar(search):
        print("Buscando...")
        with YoutubeDL(ydl_options) as ydl:
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
        print("Buscando url...")
        with YoutubeDL(ydl_options) as ydl:

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
        
    async def youtube_autocomplete(self, interaction: discord.Interaction, current: str):
        results = await asyncio.to_thread(self.search_youtube, current)

        return [
            app_commands.Choice(name=result['title'][:100], value=result['title']) for result in results[:3]
        ]
    
    async def conectarse(self, ctx, channel):
        idGuild = int(ctx.guild.id)
        print("Entro a conectarse, ", channel, idGuild)

        if self.isInVc[idGuild] == None or not self.isInVc[idGuild].is_connected():
            print("Conectando...")
            self.isInVc[idGuild] = await channel.connect()

            await ctx.send(
                embed=MensajeBasico(
                    f"Conectado a {ctx.author.voice.channel}",
                    f"Peticion de union hecha por {ctx.author.mention}",
                    VERDE,
                    self.bot.user.display_avatar
                ),
                silent=True
            )

            if self.isInVc[idGuild] == None:

                await ctx.send(
                    embed=MensajeBasico(
                        "A lo bien :middle_finger:",
                        "No me pude conectar al canal de voz\nDebe estar en un canal de Voz",
                        ROJO,
                        self.bot.user.display_avatar
                    ),
                    silent=True
                )

                return
            else:
                print("Moviendo...")
                await self.isInVc[idGuild].move_to(channel)

    async def siguienteCancion(self, ctx):

        idGuild = int(ctx.guild.id)
        if not self.isPlaying[idGuild]:
            return
        if self.queueIndex[idGuild] + 1 < len(self.queue[idGuild]):
            self.isPlaying[idGuild] = True
            self.queueIndex[idGuild] += 1

            cancion = self.queue[idGuild][self.queueIndex[idGuild]][0]
            await ctx.send(
                embed=self.embed_Reproduciendo_Ahora(ctx, cancion),
                silent=True
            )

            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS), 0.7)

            self.isInVc[idGuild].play(source, after= lambda e: asyncio.run_coroutine_threadsafe(self.siguienteCancion(ctx), self.bot.loop))
        else:
            self.queueIndex[idGuild] += 1
            self.isPlaying[idGuild] = False

    

    # Funcion para reproducir la Musica
    # Se encarga de conectar el bot al canal de voz del usuario
    # Mandar mensajes para darle contexto al usuario de lo que esta pasando
    # Si hay canciones en la cola reproducir la siguiente al terminar la actual
    #
    async def reproducir(self, ctx):
        
        idGuild = int(ctx.guild.id)

        if self.queueIndex[idGuild] < len(self.queue[idGuild]):
            self.isPlaying[idGuild] = True
            self.isPaused[idGuild] = False

            await self.conectarse(ctx, self.queue[idGuild][self.queueIndex[idGuild]][1])

            cancion = self.queue[idGuild][self.queueIndex[idGuild]][0]

            await ctx.send(embed=self.embed_Reproduciendo_Ahora(ctx, cancion), silent=True)

            source = discord.FFmpegPCMAudio(cancion['streamUrl'], **FFMPEG_OPTIONS)
            print("Reproduciendo...",cancion['titulo'])
            source = discord.PCMVolumeTransformer(source, 0.7)

            self.isInVc[idGuild].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.siguienteCancion(ctx), self.bot.loop))
        else:
            await ctx.send(
                embed=MensajeBasico(
                    "Cola Vacia! :melting_face: ",
                    "No hay mas canciones en la cola de reproduccion",
                    DARK_PURPLE,
                    self.bot.user.display_avatar
                ),
                silent=True
            )
            self.queueIndex[idGuild] += 1
            self.isPlaying[idGuild] = False


    @commands.command(
        name="skip",
        aliases=["s", "S", "SKIP"],
        help="Comando para saltar a la siguiente canción en la cola de reproducción"
    )
    async def skip(self, ctx, *arg):
        arg = " ".join(arg)
        idGuild = int(ctx.guild.id)

        if self.isInVc[idGuild] == None:
            await ctx.send(
                ctx.author.mention,
                embed=MensajeBasico(
                    "No se pudo skipear :nerd: ",
                    f"{ctx.author.mention} El bulloso Necesita estar en un canal de voz para usar ester comando!",
                    DARK_RED,
                    self.bot.user.display_avatar
                ),
                silent=True
            )
            return
        
        if self.queueIndex.get(idGuild, 0) >= len(self.queue.get(idGuild, [])) - 1:
            await ctx.send(
                embed=MensajeBasico(
                    "Saltando la canción :face_with_diagonal_mouth:",
                    "No hay más canciones en la cola de reproducción\n\n\tQuitando la canción",
                    DARK_BLUE,
                    self.bot.user.display_avatar
                ),
                silent=True
            )

            self.isInVc[idGuild].stop()
            await self.siguienteCancion(ctx)
            return
        
        if not arg:
            if self.isInVc[idGuild]:
                self.isInVc[idGuild].pause()
                self.queueIndex[idGuild] += 1
                await self.reproducir(ctx)
        else:
            try:
                salto = int(arg)
                if salto > len(self.queue[idGuild]):
                    await ctx.send(
                        embed=MensajeBasico(
                            "No hay canciones en la cola! :dizzy_face:",
                            f"No puede saltar mas canciones de las que hay en la cola\nCanciones en cola: {len(self.queue[idGuild])}",
                            DARK_PURPLE,
                            self.bot.user.display_avatar
                        ),
                        silent=True
                    )
                else:
                    if self.isInVc[idGuild] != None and self.isInVc[idGuild]:
                        self.isInVc[idGuild].pause()
                        self.queueIndex[idGuild] += salto
                        await self.reproducir(ctx)
            except ValueError:
                await ctx.send(
                    embed=MensajeBasico(
                        "Error en el Valor",
                        "El valor proporcionado no es un numero valido",
                        DARK_RED,
                        self.bot.user.display_avatar
                    ),
                    silent=True
                )
    
    @commands.hybrid_command(
        name="play",
        aliases=["p", "P", "PLAY"],
        help="Comando para buscar en YouTube una canción con el nombre o URL",
        usage="$p <nombre o link>",
        description="Ejecuta una canción por nombre o link",
    )
    @app_commands.describe(busqueda="Titulo o enlace de la cancion")
    @app_commands.autocomplete(busqueda=youtube_autocomplete)
    async def play(self, ctx: commands.Context, *, busqueda: str = None):
        for guild in self.bot.guilds:
            idGuild = int(guild.id)
            self.queue[idGuild] = []
            self.queueIndex[idGuild] = 0
            self.isInVc[idGuild] = None
            self.isPlaying[idGuild] = False
            self.isPaused[idGuild] = False


        search = busqueda or " ".join(busqueda)
        idGuild = int(ctx.guild.id)

        channel = ctx.author.voice.channel
        print(channel, ctx, search)
        await self.conectarse(ctx, channel)
        # try:
        # except Exception as e:
        #     print(e)
        #     await ctx.send(
        #         ctx.author.mention,
        #         embed=MensajeBasico(
        #             "No me pude conectar",
        #             "Para conectarme debe estar en un canal de voz",
        #             ROJO,
        #             self.bot.user.display_avatar
        #         ),
        #         silent=True
        #     )
        #     return
        
        if not search:
            if len(self.queue[idGuild]) == 0:
                await ctx.send(
                    embed=MensajeBasico(
                        "Cola Vacia! :face_with_monocle:",
                        "No hay canciones en la cola\n\nIngrese un link o una cancion para buscarla",
                        DARK_RED,
                        self.bot.user.display_avatar
                    ),
                    silent=True
                )
                return
            elif not self.isPlaying[idGuild]:
                if self.queue[idGuild] == None or self.isInVc[idGuild] == None:
                    await self.reproducir(ctx)
                else:
                    print("Entro else not args play")
                    self.isPaused[idGuild] = False
                    self.isPlaying[idGuild] = True
                    self.isInVc[idGuild].resume()
            return
        
        cancion = None
        # if search.startswith("https://open.spotify.com/") == True:
        #     self.verificarTokenSpotify()
        #     search = search.split('?')[0]
        #     if search.startswith('https://open.spotify.com/playlist/') == True:
        #         cancion = await busquedaPlaylist(ctx, channel, search)
        #         print("Spotify playlis, termino la cancion ", cancion['Titulo'])
        #     else:
        #         search = search.removeprefix('https://open.spotify.com/intl-es/track/')
        #         cancion = await asyncio.to_thread(self.buscar, nombreArtiCancionPlaylistTrack(cliente.track(search)))
        if esUrl(search) == True:
            print("Entro a es url")
            cancion = await asyncio.to_thread(self.getStream, search)
        else:
            print("Entro a busqueda por nombre")
            cancion = self.buscar(search)
        
        if isinstance(cancion, bool):
            await ctx.send(
                embed=MensajeBasico(
                    "Uy cual es esa :rage:",
                    f"Que mierda buscaste sapa {ctx.author.mention}",
                    ROJO,
                    self.bot.user.display_avatar
                ),
                silent=True
            )
            return
        else:
            print("Paso el check de cancion")
            self.queue[idGuild].append([cancion, channel])

            if not self.isPlaying[idGuild]:
                print("Entro a reproducir")
                await self.reproducir(ctx)
            else:
                await  ctx.send(
                    embed=self.embed_Añadido_Queue(ctx, cancion),
                    silent=True
                )
        
        if not ctx.author.voice:
            await ctx.send(
                embed=MensajeBasico(
                    "A lo bien :middle_finger:",
                    "No me pude conectar al canal de voz\nDebe estar en un canal de Voz",
                    ROJO,
                    self.bot.user.display_avatar
                ),
                silent=True
            )
            return
        


# async def setup(bot):
#     await bot.add_cog(Music(bot))