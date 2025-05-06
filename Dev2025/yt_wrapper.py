from concurrent.futures import ProcessPoolExecutor
import yt_dlp
from typing import TypedDict, Optional
from utils import format_audio_seconds # Asegúrate que esté disponible en tu proyecto

# Crea un pool de procesos dedicado para funciones pesadas
yt_dlp_executor = ProcessPoolExecutor(max_workers=2)

class VideoMetada(TypedDict):
    Titulo: Optional[str]
    link: str
    streamUrl: Optional[str]
    Canal: Optional[str]
    Duracion: Optional[str]
    Miniatura: Optional[str]


def buscar_metadatos_proc(query: str) -> dict:
    opciones = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        video = info['entries'][0]
        return {
            'Titulo': video.get('title'),
            'link': video.get('url') or f"https://www.youtube.com/watch?v={video.get('id')}",
            'streamUrl': None,
            'Canal': video.get("uploader"),
            'Duracion': format_audio_seconds(info.get('duration')),
            'Miniatura': f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg",
        }


def obtener_stream_proc(url: str) -> dict:
    opciones = {
        'quiet': True,
        'skip_download': True,
        'format': 'bestaudio/best',
        'extract_flat': False,
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'Titulo': info.get('title'),
            'link': f"https://www.youtube.com/watch?v={info.get('id')}",
            'streamUrl': info['url'],
            'Canal': info.get('uploader'),
            'Duracion': info.get('duration_string'),
            'Miniatura': info['thumbnail'],
        }

def buscar_proc(search):
    opciones = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'default_search': 'ytsearch1',
        'extract_flat': False,
        'noplaylist': True,
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(f"ytsearch1:{search}", download=False)
        entries = info['entries'][0]
        return {
            'Titulo': entries.get('title'),
            'link': f"https://www.youtube.com/watch?v={entries.get('id')}",
            'streamUrl': entries.get('url'),
            'Canal': entries.get('uploader'),
            'Duracion': entries.get('duration_string'),
            'Miniatura': entries.get('thumbnail'),
        }

async def buscar_metadatos(query: str) -> dict:
    """
        ## Esta funcion se ejecuta dentro de un proceso independiente
        ## Con sus propios procesos de interprete para evitar GIL (Global Interpreter Lock)

        ---------------------

        **Busca los metadatos de un video de Youtube usando un texto como un titlo o artista**

        ---------------------

        ### Recibe Args:
        
        **url (str):** `Url de youtube`
        
        ---------------------

        ### Devuelve Returns:
        
        **dict:** un Diccionario con los siguientes campos
                - **Titulo (str | None):** `Titulo del Video/Audio`,
                - **link (str):** `Link/Url al Video/Audio`,
                - **steramUrl (None):** `Link/Url al stream de bits del Video/Audio | Como la busqueda debe ser ligera se omite el URl del Stream`,
                - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`,
                - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`,
                - **Minuatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`,

    """
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, buscar_metadatos_proc, query)


async def obtener_stream(url: str) -> dict:
    """
        ## Esta funcion se ejecuta dentro de un proceso independiente
        ## Con sus propios procesos de interprete para evitar GIL (Global Interpreter Lock)

        ---------------------

        **Busca el Link/Url de stream de bits de Youtube usando un Link/Url de video de Youtube**

        ---------------------

        ### Recibe Args:
        
        **url (str):** `Url de youtube`
        
        ---------------------

        ### Devuelve Returns:
        
        **dict:** un Diccionario con los siguientes campos
                - **Titulo (str | None):** `Titulo del Video/Audio`,
                - **link (str):** `Link/Url al Video/Audio`,
                - **steramUrl (str | None):** `Link/Url al stream de bits del Video/Audio`,
                - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`,
                - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`,
                - **Minuatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`,

    """
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, obtener_stream_proc, url)

async def buscar(query: str) -> dict:
    """
        ## Esta funcion se ejecuta dentro de un proceso independiente
        ## Con sus propios procesos de interprete para evitar GIL (Global Interpreter Lock)

        ---------------------

        **Busca un video de Youtube usando un texto como un titlo o artista**

        ---------------------

        ### Recibe Args:
        
        **url (str):** `Url de youtube`
        
        ---------------------

        ### Devuelve Returns:
        
        **dict:** un Diccionario con los siguientes campos
                - **Titulo (str | None):** `Titulo del Video/Audio`,
                - **link (str):** `Link/Url al Video/Audio`,
                - **steramUrl (str | None):** `Link/Url al stream de bits del Video/Audio`,
                - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`,
                - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`,
                - **Minuatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`,

    """
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, buscar_proc, query)

def shutdown_executor():
    """
        ## Se encarga de terminar los procesos creados
    """
    yt_dlp_executor.shutdown(wait=True)
