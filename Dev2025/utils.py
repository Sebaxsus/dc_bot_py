import discord

# #Colores embed Azul= 0x2c76dd, Rojo= 0xdf1141, Verde= 0x0eaa51
# AZUL,ROJO,VERDE,DARK_PURPLE,DARK_BLUE = 0x2c76dd, 0xdf1141,0x0eaa51,0x71368A,0x206694
# TEAL,DARK_RED,DARK_GREEN = 0x1ABC9C, 0x992D22,0x1F8B4C


def MensajeBasico(titulo: str, texto: str, color: int, icon_Url: str = None) -> discord.embeds.Embed:
    """
    - Devuelve un objecto discord.Embed

    ---------------------

    **Parameters:**
        **titulo:** `(str)`
        **texto:** `(str)`
        **color:** `(int)`
        **icon_Url:** `(str) | url de la foto de perfil del bot`

    ---------------------    

    **Returns**
        `discord.embeds.Embed`
    """
    em = discord.Embed(
            title=titulo,
            description=texto,
            colour=color
        )
    
    em.set_footer(icon_url=icon_Url)

    return em

def esUrl(texto: str) -> tuple[str, str]:
    """
    - Pide un texto y la clasifica si es una url o no\n
     y devuelve una url formateada si es url

    ---------------------

    **Clasifica los siguientes tipos de links:**
        - `yotube_video - 0`
        - `yotube_playlist - 1`
        - `spotify_track - 2`
        - `spotify_playlist - 3`
        - `spotify_album - 4`
        - `url_generica - 5`
        - `texto - 6'

    ---------------------

    **Parameters**
        **texto:** `str`
    
    ---------------------
    
    **Returns:**
        `tuple(type: str, url: str)`
    """
    # *Returns:*
    #     - tuple(isUrl: bool, tuple(type: str, url: str) )
    texto = texto.strip()
    tipo = "texto"
    isUrl = False

    # Verificando si el texto es un link
    if texto.startswith('https://') or texto.startswith("http://"):
        isUrl = True
        tipo = "url_generica"
        # Youtube playlist
        if "youtube.com/playlist?list=" in texto:
            texto = texto.split("&")[0]
            tipo = "youtube_playlist"
        # Video de Youtube
        if "youtube.com/watch" in texto:
            texto = texto.split("&")[0]
            tipo = "youtube_video"
        # Spotify Playlist
        if "spotify.com/playlist/" in texto:
            texto = texto.split("?")[0]
            tipo = "spotify_playlist"
        # Spotify Track
        if "spotify.com/intl-es/track/" in texto or "spotify.com/track/" in texto:
            # Si por algun motivo el link no contiene el "intl-es" pueda igual parsear la ID del link
            prefix = "https://open.spotify.com/intl-es/track/" if "intl-es" in texto else "https://open.spotify.com/track/"
            texto = texto.split("?")[0].removeprefix(prefix)
            tipo = "spotify_track"
        # Spotify Album
        if "spotify.com/album/" in texto or "spotify.com/intl-es/album/" in texto:
            # texto = texto.split("?")[0].removeprefix('https://open.spotify.com/intl-es/album/')
            texto = texto.split("?")[0]
            tipo = "spotify_album"
    # En el caso de que no este dentro de ninguno de los anteriores
    # Devolvera isUrl Flase y el texto original
    print("Fin modulo utils.esUrl" ,(tipo, texto))
    return (tipo,texto)
        
        

def format_audio_seconds(seconds: str | int) -> str:
    """
    - Convierte un string de segundos a formato `Minutos:Segundos`

    ---------------------

    **Parameters:**
        **Segundos** `(int)`
    
    ---------------------

    **Returns:**
        `(str)`
    """
    if seconds is None:
        return "desconocido"
    mins, secs = divmod(int(seconds), 60)
    return f"{mins}:{secs:02}"