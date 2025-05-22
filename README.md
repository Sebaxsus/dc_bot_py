# Documentacion_Tecnica

## Proyecto: ElBulloso - Bot de Música para Discord

---

### Descripción General

ElBulloso es un bot de música para Discord que permite reproducir canciones y playlists desde Spotify y YouTube, gestionando colas, búsquedas y reproducción en canales de voz. Utiliza `discord.py`, `spotipy` y `yt-dlp` para la integración con las APIs de Discord, Spotify y YouTube respectivamente.

---

## Tabla de Contenidos

1. [Dependencias](#dependencias)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Instalación](#instalación)
4. [Configuración](#configuración)
5. [Puesta en Marcha](#puesta-en-marcha)
6. [Principales Componentes y Funciones](#principales-componentes-y-funciones)
7. [Comandos Disponibles](#comandos-disponibles)
8. [Flujo de Funcionamiento](#flujo-de-funcionamiento)
9. [Eventos y Manejo de Errores](#eventos-y-manejo-de-errores)
10. [Notas y Recursos](#notas-y-recursos)

---

## Dependencias

- Python 3.12+
- discord.py
- spotipy
- yt-dlp
- ffmpeg (instalado y en el PATH)
- Otros: asyncio, concurrent.futures, dotenv, etc.

---

## Estructura del Proyecto

```
bot_dc_py/
│
├── Dev2025/
│   ├── bot_Optimizado.py      # Archivo principal del bot
│   ├── requirements.txt       # Dependencias Python
│   ├── Dockerfile             # Soporte para Docker
│   ├── modules/
│   │   ├── utils.py           # Utilidades generales
│   │   ├── yt_wrapper.py      # Funciones para YouTube
|   ├── Test/
|   |   ├── text.txt           # Logs de pruebas
│   └── ...
├── iniciar_bot.cmd            # Script para iniciar el bot en Windows
├── README.md                  # Guía de instalación y 
└── ...
```

---

## Instalación

Opción 1: Python Local

1. **Clona el repositorio**

```bash
git clone https://github.com/Sebaxsus/dc_bot_py.git
cd bot_dc_py/Dev2025
```

2. **Crea un entorno virtual (opcional pero recomendado)**
> [!TIP]
> Esta opcion es mas recomendable ya que las librearias se instalan dentro de el entorno virtual y no en de manera global en Python

```bash
python -m venv Nombre_del_entorno venv 
Nombre_del_entorno\Scripts\activate
```

3. **Instala las dependencias**

```bash
pip install -r requirements.txt
```

Opción 2: Docker

1. **Construye la imagen**

```bash
docker build -t elbulloso-bot .
```

---

## Configuración

Debes definir las siguientes variables en tu archivo `.env` o en `settings.py`:

- `DISCORD_TOKEN`: Token de tu bot de Discord.
- `SPOTIFY_CLIENT_ID`: Client ID de tu app de Spotify.
- `SPOTIFY_CLIENT_SECRET`: Client Secret de tu app de Spotify.

---

## Puesta en Marcha

Opción 1: Python Local

- **Ejecuta el bot**

```bash
python bot_Optimizado.py
```

Opción 2: Docker

- **Ejecuta el contenedor**

```
docker run --env-file .env elbulloso-bot
```

Opción 3: Script Windows

- **Ejecuta el Script de Windows**

> [!IMPORTANT]
>**Se debe configurar las rutas del Script**
>
> Se debe cambiar las rutas del script para que usa la ruta de `bot_Optimizado.py` y el inteprete de `Python` preferido **(venv o local)**

```cmd
run iniciar_bot.cmd
```

---

## Principales Componentes y Funciones

### Inicialización

- **thread_pool**: Pool de hilos para tareas pesadas (búsquedas, streams).
- **auth_manager**: Maneja la autenticación con Spotify usando PKCE.
- **cliente**: Cliente de Spotipy autenticado.

### Diccionarios de Estado

- **isPlaying, isPaused, queue, queueIndex, isInVc**: Controlan el estado de reproducción y la cola por servidor.
- **desconectado_por_codigo, ctx_por_guild**: Controlan desconexiones y contexto por servidor.
- **autocomplete_cache**: Cache para autocompletado de búsquedas.

### Funciones Clave

- **verificarTokenSpotify**: Renueva el token de Spotify si es necesario.
- **MensajeBasico**: Crea un embed básico para Discord.
- **procesarBloqueStream / guardarStreamUrls**: Procesan bloques de canciones para obtener sus stream URLs.
- **guardarCancionesSpList / guardaCancionesSpAlbum**: Añaden canciones de una playlist/álbum de Spotify a la cola.
- **busquedaPlaylist / busquedaAlbum**: Orquestan la búsqueda y carga de playlists/álbumes.
- **getStream**: Obtiene la URL de stream de un video de YouTube.
- **embed_Reproduciendo_Ahora / embed_Añadido_Queue / embed_Eliminado_Queue**: Embeds personalizados para feedback visual.
- **reproducir / siguienteCancion / conectarse**: Controlan la reproducción y conexión a canales de voz.

**modules/yt_wrapper.py**

- **buscar_metadatos:** Busca metadatos de canciones en YouTube.
- **buscar:** Realiza búsquedas directas en YouTube.
- **obtener_stream:** Obtiene la URL de stream de una canción.

**modules/utils.py**

- **esUrl:** Valida si un string es una URL y la clasifica segun el tipo.

---

## Comandos Disponibles

- `/play <nombre o link>`: Busca y reproduce una canción.
- `/pause`: Pausa la reproducción.
- `/resume`: Reanuda la reproducción.
- `/skip [cancion]`: Salta la canción actual o a una específica.
- `/cola`: Muestra la cola de canciones.
- `/limpiar`: Limpia la cola excepto la canción actual.
- `/eliminar [cancion]`: Elimina una canción de la cola.
- `/unirse`: Une el bot al canal de voz actual.
- `/salir`: Saca al bot del canal de voz y limpia la cola.
- `/info`: Muestra información del servidor.
- `/usuarios`: Lista los usuarios visibles por el bot.
- `/sebax`: Menciona a Sebax (comando de ejemplo).
- `/ping <nombre>`: Menciona a un usuario por nombre global.

---

## Flujo de Funcionamiento

1. **Usuario ejecuta comando** (`/play`, `/playlist`, etc.)
2. **El bot valida el comando y argumentos**
3. **Si es búsqueda de Spotify:**
   - Obtiene metadatos de la playlist/álbum.
   - Divide en bloques de 5 canciones.
   - Busca metadatos y URLs de stream para cada canción (asincrónicamente).
   - Añade canciones a la cola.
4. **Si es búsqueda de YouTube:**
   - Busca metadatos y URL de stream.
   - Añade canción a la cola.
5. **Si no hay reproducción activa:**
   - Inicia reproducción en el canal de voz.
6. **Durante la reproducción:**
   - Escucha comandos de control (`pause`, `skip`, etc.)
   - Actualiza la cola y el estado.
7. **Al finalizar la cola o recibir `/salir`:**
   - Limpia recursos y desconecta del canal de voz.

---

## Eventos y Manejo de Errores

- **on_ready**: Inicializa variables y sincroniza comandos al conectar el bot.
- **on_voice_state_update**: Desconecta el bot si se queda solo en el canal de voz o reconecta si fue desconectado inesperadamente.
- **on_app_command_error**: Maneja errores de comandos slash y responde en Discord.
- **on_close**: Libera recursos al cerrar el bot.

---

## Notas y Recursos

> [!IMPORTANT]
> **FFmpeg**
>
> debe estar instalado y en el PATH del sistema.

> [!NOTE]
>
> El bot utiliza asincronía y un pool de hilos para evitar bloqueos y mejorar el rendimiento.

> [!TIP]
>
> La documentación de cada función está en formato docstring en el código fuente.

> [!NOTE]
>
> Para más detalles sobre comandos y configuración, consulta el [README.md](README.md).

### Recursos Externos

- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- [spotipy](https://spotipy.readthedocs.io/en/2.22.1/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)

---

**Autor:** [Sebaxsus](https://github.com/Sebaxsus)  
**Contacto:** sebastiangarcia1198@gmail.com
