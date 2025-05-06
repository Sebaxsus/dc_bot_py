import yt_dlp, time
start = time.time()
# Configuración de yt_dlp
ydl_opts = {
    'extract_flat': False,
    'quiet': True,  # Para evitar logs en consola
    'skip_download': True,  # No descarga nada
    'format': 'bestaudio/best',
}

ydl_opts_meta = {
    'extract_flat': True,
    'quiet': True,  # Para evitar logs en consola
    'skip_download': True,  # No descarga nada
}
# archivo = open("datosBusquedaLink.txt", "a")

# archivo.write(f"\n\n\t****Busqueda de metadatos****\n\n")

url = 'https://www.youtube.com/playlist?list=PL9tY0BWXOZFtq_zg-8BiQjJJ8LUV6j3Zt'  # Ejemplo: una playlist
def buscar(busqueda: str):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'ytsearch1:{busqueda}', download=False)
        # Revisa si es una playlist u otro tipo con múltiples entradas
        # for i in info:
        #     if i == "entries":
        #         archivo.write(f"{i}:\n")
        #         for entry in info[i][0]:
        #             archivo.write(f"\t{entry}:\n\t\t{info[i][0][entry]}\n")
        #     else:
        #         archivo.write(f"{i}:\n\t{info[i]}\n")

        
        if 'entries' in info:
            print("Lista de resultados")
            for entry in info['entries']:
                print(f"Title: {entry.get('title')}")
                print(f"Video ID: {entry.get('id')}")
                print(f"URL: https://www.youtube.com/watch?v={entry.get('id')}")
                print(f"StreamURl: {entry.get('url')}")
                print('---')
        else:
            print("Un solo resultado")
            # Si es un solo video
            print(f"Title: {info.get('title')}")
            print(f"Video ID: {info.get('id')}")
            print(f"URL: https://www.youtube.com/watch?v={info.get('id')}")

def buscarUrl(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=False)

        # for i in info:
        #     archivo.write(f"{i},\n\t{info[i]}\n")
        
        print("Url?: ", info.get('url'))

def buscarMetaDatos(busqueda: str):
    with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl:
        info = ydl.extract_info(f'ytsearch1:{busqueda}', download=False)
        # for i in info:
        #     if i == "entries":
        #         archivo.write(f"{i}:\n")
        #         for entry in info[i][0]:
        #             archivo.write(f"\t{entry}:\n\t\t{info[i][0][entry]}\n")
        #     else:
        #         archivo.write(f"{i}:\n\t{info[i]}\n")
        info = info['entries'][0]
        print({
            'Titulo': info.get('title'),
            'link': info.get('url') or f"https://www.youtube.com/watch?v={info.get('id')}",
            'streamUrl': None,
            'Canal': info.get("uploader"),
            'Duracion': info.get('duration'), # Devuelve el tiempo de duracion ya formateado
            'Miniatura': f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig",
        })

# for i in ["Rain - Trueno", "Sleeping town (feat. yama) - whaledontsleep yama", "Movimiento de Caderas - Rayo & Toby", "Pop Smoke - Hello (Audio) ft. A Boogie wit da Hoodie"]:
#     archivo.write("\n")
#     buscar(i)

# buscar("Sleeping town (feat. yama) - whaledontsleep yama")

# archivo.write("\n\n\t***BUSQUEDA POR URL***\n\n")

# buscarUrl("https://www.youtube.com/watch?v=fazMSCZg-mw")

buscarMetaDatos("Sleeping town (feat. yama) - whaledontsleep yama")

print("Termino", time.time() - start)