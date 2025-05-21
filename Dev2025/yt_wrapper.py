from concurrent.futures import ProcessPoolExecutor
import yt_dlp
from typing import TypedDict, Optional
from utils import format_audio_seconds # Asegúrate que esté disponible en tu proyecto

# Crea un pool de procesos dedicado para funciones pesadas
yt_dlp_executor = ProcessPoolExecutor(max_workers=2)

class VideoMetada(TypedDict):
    """
        Esta clase es un TypedDict que define la estructura de los metadatos de un video
        de Youtube. Se utiliza para proporcionar una mejor autocompletación y verificación
        de tipos en el código.

        ---------------------

        **Campos:**
            - **Titulo (str | None):** `Titulo del Video/Audio`,
            - **link (str):** `Link/Url al Video/Audio`,
            - **steramUrl (None):** `Link/Url al stream de bits del Video/Audio | Como la busqueda debe ser ligera se omite el URl del Stream`,
            - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`,
            - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`,
            - **Miniatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`,

        ---------------------

        **Ejemplo:**
        ```python
        {
            'Titulo': 'Ejemplo de Titulo',
            'link': 'https://www.youtube.com/watch?v=ejemplo',
            'streamUrl': None,
            'Canal': 'Nombre del Canal',
            'Duracion': '3:45',
            'Miniatura': 'https://i.ytimg.com/vi/ejemplo/hqdefault.jpg'
        }
        ```

        ---------------------

        **Nota:**
            - `streamUrl` es `None` en la búsqueda de metadatos porque no se necesita el URL del stream
            - `link` es la URL del video en Youtube.
            - `Duracion` es un string formateado en `Minutos:Segundos`
            - `Miniatura` es la URL de la miniatura del video.
            - `Canal` es el nombre del canal que subió el video.
            - `Duracion` es la duración del video en formato `Minutos:Segundos`
            - `Miniatura` es la URL de la miniatura del video.

        ---------------------

        [*Nota: Esta clase es solo un ejemplo y puede no reflejar la estructura real de los metadatos de Youtube.]*
        [*Nota: Asegúrate de que la librería yt-dlp esté instalada y configurada correctamente en tu entorno de desarrollo.*]

        [Mas info sobre yt-dlp](https://github.com/yt-dlp/yt-dlp)

    """
    Titulo: Optional[str]
    link: str
    streamUrl: Optional[str]
    Canal: Optional[str]
    Duracion: Optional[str]
    Miniatura: Optional[str]


def buscar_metadatos_proc(query: str) -> dict:
    """
    Esta funcion se ejecuta dentro de un proceso independiente
    Con sus propios recursos de interprete para evitar **GIL (Global Interpreter Lock)**

    ---------------------

    **Parametros:**
        **query (str):** `Texto a buscar en Youtube`

    ---------------------

    **Devuelve Retorna:**
        **dict:** un Diccionario con los siguientes campos
            - **Titulo (str | None):** `Titulo del Video/Audio`.
            - **link (str):** `Link/Url al Video/Audio`.
            - **streamUrl (None):** `Link/Url al stream de bits del Video/Audio | Como la busqueda debe ser ligera se omite el URl del Stream`.
            - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`.
            - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`.
            - **Miniatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`.

    [Mas info sobre yt-dlp](https://github.com/yt-dlp/yt-dlp)\n
    [Mas info sobre asyncio](https://docs.python.org/3/library/asyncio.html)

    """
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
    """
    Esta funcion se ejecuta dentro de un proceso independiente
    Con sus propios recursos de interprete para evitar **GIL (Global Interpreter Lock)**
    
    ---------------------
    
    **Recibe Args:**
        **url (str):** `Url de youtube`
        
    ---------------------
    
    **Devuelve Returns:**
        **dict:** un Diccionario con los siguientes campos
            - **Titulo (str | None):** `Titulo del Video/Audio`.
            - **link (str):** `Link/Url al Video/Audio`.
            - **streamUrl (None):** `Link/Url al stream de bits del Video/Audio | Como la busqueda debe ser ligera se omite el URl del Stream`.
            - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`.
            - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`.
            - **Miniatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`.    

    [Mas info sobre yt-dlp](https://github.com/yt-dlp/yt-dlp)\n
    [Mas info sobre asyncio](https://docs.python.org/3/library/asyncio.html)\n
    [Mas info sobre ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor)\n
    [Mas info sobre GIL (Global Interpreter Lock)](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)        
    """
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

def buscar_proc(search: str) -> dict:
    """
    Esta funcion se ejecuta dentro de un proceso independiente
    Con sus propios recursos de interprete para evitar **GIL (Global Interpreter Lock)**
    Se encarga de buscar los metadatos de un video de youtube usando un texto como un titlo
    
    ---------------------
    
    **Recibe Args:**
        **search (str):** `Url de youtube`
        
    ---------------------
    
    **Devuelve Returns:**
        **dict:** un Diccionario con los siguientes campos
            - **Titulo (str | None):** `Titulo del Video/Audio`.
            - **link (str):** `Link/Url al Video/Audio`.
            - **streamUrl (None):** `Link/Url al stream de bits del Video/Audio | Como la busqueda debe ser ligera se omite el URl del Stream`.
            - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`.
            - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`.
            - **Miniatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`.    

    [Mas info sobre yt-dlp](https://github.com/yt-dlp/yt-dlp)\n
    [Mas info sobre asyncio](https://docs.python.org/3/library/asyncio.html)\n
    [Mas info sobre ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor)\n
    [Mas info sobre GIL (Global Interpreter Lock)](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)        
    """
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
        Esta funcion se ejecuta dentro de un proceso independiente
        Con sus propios procesos de interprete para evitar **GIL (Global Interpreter Lock)**

        ---------------------

        **Busca los metadatos de un video de Youtube usando un texto como un titlo o artista**

        ---------------------

        **Recibe Args:**
            **url (str):** `Url de youtube`
        
        ---------------------

        **Devuelve Returns:**
            **dict:** un Diccionario con los siguientes campos
                - **Titulo (str | None):** `Titulo del Video/Audio`.
                - **link (str):** `Link/Url al Video/Audio`.
                - **streamUrl (None):** `Link/Url al stream de bits del Video/Audio | Como la busqueda debe ser ligera se omite el URl del Stream`.
                - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`.
                - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`.
                - **Miniatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`.

        [Mas info sobre yt-dlp](https://github.com/yt-dlp/yt-dlp)
        [Mas info sobre asyncio](https://docs.python.org/3/library/asyncio.html)
        [Mas info sobre ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor)
        [Mas info sobre GIL (Global Interpreter Lock)](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)
    """
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, buscar_metadatos_proc, query)


async def obtener_stream(url: str) -> dict:
    """
        Esta funcion se ejecuta dentro de un proceso independiente
        Con sus propios procesos de interprete para evitar **GIL (Global Interpreter Lock)**

        ---------------------

        **Busca el Link/Url de stream de bits de Youtube usando un Link/Url de video de Youtube**

        ---------------------

        **Recibe Args:**
            **url (str):** `Url de youtube`
        
        ---------------------

        **Devuelve Returns:**
            **dict:** un Diccionario con los siguientes campos
                - **Titulo (str | None):** `Titulo del Video/Audio`.
                - **link (str):** `Link/Url al Video/Audio`.
                - **streamUrl (str | None):** `Link/Url al stream de bits del Video/Audio`.
                - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`.
                - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`.
                - **Miniatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`.

        [Mas info sobre yt-dlp](https://github.com/yt-dlp/yt-dlp)
        [Mas info sobre asyncio](https://docs.python.org/3/library/asyncio.html)
        [Mas info sobre ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor)
        [Mas info sobre GIL (Global Interpreter Lock)](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)
    """
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, obtener_stream_proc, url)

async def buscar(query: str) -> dict:
    """
        Esta funcion se ejecuta dentro de un proceso independiente
        Con sus propios procesos de interprete para evitar **GIL (Global Interpreter Lock)**

        ---------------------

        **Busca un video de Youtube usando un texto como un titlo o artista**

        ---------------------

        **Recibe Args:**
            **url (str):** `Url de youtube`

        ---------------------

        **Devuelve Returns:**
            **dict:** un Diccionario con los siguientes campos
                - **Titulo (str | None):** `Titulo del Video/Audio`.
                - **link (str):** `Link/Url al Video/Audio`.
                - **streamUrl (str | None):** `Link/Url al stream de bits del Video/Audio`.
                - **Canal (str | None):** `Nombre del canal de youtube que subio el Video/Audio`.
                - **Duracion (str | None):** `Duracion del Video/Audio Formateada en Minutos:Segundos`.
                - **Miniatura (str | None):** `Link/Url a la miniatura/Thumbnail del Video/Audio`.

        [Mas info sobre yt-dlp](https://github.com/yt-dlp/yt-dlp)
        [Mas info sobre asyncio](https://docs.python.org/3/library/asyncio.html)
        [Mas info sobre ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor)
        [Mas info sobre GIL (Global Interpreter Lock)](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)
    """
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, buscar_proc, query)

def shutdown_executor():
    """
        Se encarga de terminar los procesos creados
        por el ProcessPoolExecutor

        [Mas info sobre ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor)
    """
    yt_dlp_executor.shutdown(wait=True)
