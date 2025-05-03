import yt_dlp

def buscar(busqueda):
    search_results = []
    try:
        with yt_dlp.YoutubeDL({'quiet': True, "format": "bestaudio/best", "extract_flat": False, "default_search": "ytsearch5"}) as ydl:
            info = ydl.extract_info(f"ytsearch5:{busqueda}", download=False)
            for entry_info in info['entries']:
                title = entry_info.get('title', 'Sin título')
                duration = entry_info.get('duration', 0)
                search_results.append(entry_info)
                print(f"Resultado: {title} ({duration // 60}:{duration % 60:02} min) url: {entry_info.get("url")}")
    except Exception as e:
        print("Error", str(e))
    print("✅ Búsqueda completada")
    return search_results

for i,cancion in enumerate(buscar(input("Escriba el titulo del cancion a buscar: "))):
    print(f"{i+1}. {cancion['title']} - {cancion['url']}")