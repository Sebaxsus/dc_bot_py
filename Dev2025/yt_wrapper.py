from concurrent.futures import ProcessPoolExecutor
import yt_dlp
from utils import format_audio_seconds # Asegúrate que esté disponible en tu proyecto

# Crea un pool de procesos dedicado para funciones pesadas
yt_dlp_executor = ProcessPoolExecutor(max_workers=2)


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


async def buscar_metadatos(query: str) -> dict:
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, buscar_metadatos_proc, query)


async def obtener_stream(url: str) -> dict:
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(yt_dlp_executor, obtener_stream_proc, url)


def shutdown_executor():
    yt_dlp_executor.shutdown(wait=True)
