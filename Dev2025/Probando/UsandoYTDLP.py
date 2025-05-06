import yt_dlp, io, asyncio, pyaudio, ffmpeg, pygame, pycurl, subprocess, time


# Tamaño de buffer (ajustable para evitar cuellos de botella)
BUFFER_SIZE = 8192
MAX_RETRIES = 1

def buscar(busqueda):
    search_results = []
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(f"ytsearch5:{busqueda}", download=False)
            for entry_info in info['entries']:
                title = entry_info.get('title', 'Sin título')
                duration = entry_info.get('duration', 0)
                search_results.append(entry_info)
                print(f"Resultado: {title} ({duration // 60}:{duration % 60:02} min)")
    except Exception as e:
        print("Error", str(e))
    print("✅ Búsqueda completada")

def format_audio_seconds(seconds):
    if seconds is None:
        return "desconocido"
    mins, secs = divmod(int(seconds), 60)
    return f"{mins}:{secs:02}"

def get_audio_info(youtube_url):

    # Configurando yt_dlp
    ydl_opt = {
        'format': 'bestaudio/best', # Selecciono el mejor formato de audio disponible
        'quiet': True, # Silencia el log de yt_dlp
        'no_warnings': True, # Silencia las advertencias en consola de yt_dlp
        'skip_download': True, # No descarga el archivo
    }

    with yt_dlp.YoutubeDL(ydl_opt) as ydl:
        info = ydl.extract_info(youtube_url, download=False) # Aqui extraigo la informacion (Metadatos) del video
        # El atributo url me da la url del stream (player.js de yt/GoogleVideo)
        # El .get me pide al atribuo que busco como llave
        # title me devuelve el titulo del video de yt
        # uploader me devuelve el nombre del canal que subio el video
        # duration me devuelve la duracion del video en segundos
        return info
        # return {
        #     'url': info['url'],
        #     'title': info.get('title'),
        #     'uploader': info.get('uploader'),
        #     'duration': info.get('duration'),
        #     'info': info,
        # }

def select_audio_format(info):
    # for i in info:
    #     (f"Atributo info: {i}")
    print("🎚️ Formatos de audio disponibles:\n")
    audio_formats = [f for f in info['formats'] if f['vcodec'] == 'none'and f['audio_ext'] in ['m4a', 'webm'] ]

    # with open("./NuevoDesarrollo2025/info.txt", "a") as file:
    #     for i in info:
    #         file.write(f"Info atrib: {i}\n")
    #         file.write(f"\tAudio Formats: {info[i]} \n")
    #     file.close()

    # print("Info: ", audio_formats)
    for idx, f in enumerate(audio_formats):
        print(f"{idx}: ID={f['format_id']} | ext={f['ext']} | codec={f['acodec']} | {f['abr']}bps")
        # print(f"{idx}: ID={f['format_id']} | ext={f['ext']} | codec={f['acodec']} | {f.get('abr', "??")}bps")


    try:
        choice = input("🟢 Elige el número del formato deseado: ")
        selected = audio_formats[int(choice)]

        return selected['url'], selected['format_id']
    except:
        print("❌ Opción inválida, usando el mejor disponible.")
        return audio_formats[0]['url'], audio_formats[0]['format_id']


    
def stream_audio(stream_url, audio_info, format_id=None):
    print(f"🎵 Reproduciendo: {audio_info['title']} — {audio_info['uploader']}")
    print(f"⏱️ Duración estimada: {format_audio_seconds(audio_info['duration'])}")

    # Inicializo PyAudio
    p = pyaudio.PyAudio()
    # Configurando PyAudio
    stream = p.open(
        format=pyaudio.paInt16, # Establezco el formato de pyaudio a audio PCM 16-bit (estandar de CD)
        channels=2, # Establezco el audio en estereo (2 canales) (mono = 1 canal)
        rate=44100, # Frecuencia de Muestreo a 44.1 kHz que determina la calidad en este caso calidad estandar
        output=True, # Que reproduzca el audio
    )

    # Lista que le voy a pasar al subproceso (Linea de Comandos AKA CMD) para que ejecute como comando
    # se traduce como ffmpeg -i https://www.youtube.com/watch?v=0af9b1lyzWg -f s16le -acodec pcm_s16le -ar 44100 -ac 2 -
    # argumentos
    # -i (input): en este caso es el stream de youtube (playes.js de yt/Googlevideo)
    # -f (formato de salida): en este caso formato PCM sin encabezado (raw audio)
    # -acodec (codificacion de audio): en esta caso audio PCM de 16-bit little endian (s16le)
    # -ar (Audio rate - frecuencia de muestreo): en este caso 44.1 kHz o 44100
    # -ac (Audio Channel - Canales de audio): en este caso 2 (estereo)
    # - : Manfa la salida a stdout
    ffmpeg_cmd = [
        'ffmpeg',
        '-reconnect', '1',               # permite reconexión
        '-reconnect_streamed', '1',      # permite reconectar durante el streaming
        '-reconnect_delay_max', '2',     # tiempo máximo entre reconexiones
        '-i', stream_url,
        '-f', 's16le', # Salida sib encabezado, PCM
        '-acodec', 'pcm_s16le', # codec PCM
        '-ar', '44100', # Audio Rate (Frecuencia de Muestreo)
        '-ac', '2', # Audio Channels
        '-vn',
        '-' # Salida a stdout
    ]
    
    # subprocess.Popen (Process open): ejecuta ffmpeg y redirige su salida al programa
    # sdtout=PIPE: La salida binaria se lee desde python
    # stderr=DEVNULL: Se ignoran los errores de consola de ffmpeg (Esto para no mostrar el error al terminar la cancion/stream)
    start_time = time.time()
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # last = time.time()
    try:
        while True:
            # Se guardan pequeños bloques de 4096 bytes del audio almacenado en el stdout (Lo que convierte ffmpeg y saca al stdout con el arg -)
            data = process.stdout.read(BUFFER_SIZE)    
            # Verificacion de buffer
            # now = time.time()
            # print(f"⏳ Intervalo: {now - last:.4f}s, Bytes leídos: {len(data)}")
            # last = now
            # En caso de que los intervalos crecen mucho o se "congela", el buffer esta fallando.

            # Si data no contiene nada salga del bucle
            if not data:
                break
            # Mientras data sea algo distinto a null, none.
            # stderr_data = process.stderr.read(2048).decode('utf-8', errors='ignore')
            # if "Unable to read from socket" in stderr_data:
            #     print("⚠️ Se interrumpió el stream. Reintentando con otro formato...")
            # Envia el bloque a la salida de audio del sistema
            stream.write(data)
    except KeyboardInterrupt:
        print("\n⛔ Reproducción interrumpida por el usuario.")
    finally:
        elapsed = time.time() - start_time
        # Terminamos el stream de Pyaudio (stream)
        stream.stop_stream()
        # Cerramos Pyaudio
        stream.close()
        # Terminamos/Matamos Pyaudio
        p.terminate()
        # Matamos el proceso de ffmpeg
        process.kill()

        print(f"\n✅ Reproducción finalizada.")
        print(f"📌 Título: {audio_info['title']}")
        print(f"📺 Canal: {audio_info['uploader']}")
        print(f"🕒 Duración esperada: {format_audio_seconds(audio_info['duration'])}")
        print(f"⏳ Tiempo reproducido: {format_audio_seconds(elapsed)}")

def main():
    url = input("Ingrese una URL de Youtube: ")

    for attempt in range(MAX_RETRIES):
        try:
            print("Obteniendo URL de audio...")
            audio_info = get_audio_info(url)
            stream_url, format_id = select_audio_format(audio_info)
            print(f"Url: {stream_url}\nFormat: {format_id}")
            stream_audio(stream_url, audio_info, format_id)
        except Exception as e:
            print(f"⚠️ Error durante la reproducción: {e}")
            if attempt + 1 < MAX_RETRIES:
                print("🔁 Reintentando con el mismo formato...")
            else:
                print("❌ Falló después de varios intentos.")

# Se ejecuta al inciar el Script (.py)
if __name__ == '__main__':
    main()

# Mas info sobre los CODECS, BIT-RATE y INFORMACION SOBRE LOS AUDIOS y las reproducciones

# Que es CD
# CD es Compact Disc de Audio, introducido en 1982, estableció el primer estándar digital de audio de alta fidelidad para el consumo masivo

# Especificaciones del CD de audio

# Parametró             |   Valor estándar en CD

# Formato               |   PCM (Pulse-Code Modulation)
# Profundidad de bits   |   16 bits por muestra
# Frecuencia de muestreo|   44.1 kHz
# Canales               |   2 (Estéreo)

# ¿Por qué PCM 16-bit y 44.1 kHz?
# 16-bit → permite 65,536 niveles de amplitud (2^16), lo que representa un amplio rango dinámico (~96 dB).

# 44.1 kHz → cumple con el Teorema de Nyquist, que dice que necesitas el doble de la frecuencia máxima audible (20 kHz) para capturarla correctamente.

# PCM es sin compresión, ideal para máxima fidelidad.

# 2. Frecuencias de muestreo y formatos comunes
# Frecuencia (Hz)	Aplicación común
# 8000	Telefonía (voz)
# 16000	Reconocimiento de voz
# 22050	Audio de baja calidad (YouTube antiguo)
# 32000	FM, Broadcast
# 44100	Estándar de CD
# 48000	Audio profesional / video
# 88200 / 96000	Audio de alta resolución
# 192000	Masterización, estudio