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
10. [Descripción de utilidades](#manejo-del-entorno-cmd-variables-y-supervisión-del-bot)
11. [Notas y Recursos](#notas-y-recursos)

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

![Imagen del diagrama de Flujo](./Archivos/Diagrama%20de%20Flujo%20ElBulloso.webp)

---

## Eventos y Manejo de Errores

- **on_ready**: Inicializa variables y sincroniza comandos al conectar el bot.
- **on_voice_state_update**: Desconecta el bot si se queda solo en el canal de voz o reconecta si fue desconectado inesperadamente.
- **on_app_command_error**: Maneja errores de comandos slash y responde en Discord.
- **on_close**: Libera recursos al cerrar el bot.

## Manejo del Entorno CMD, Variables y Supervisión del Bot

Este documento describe el uso de ciertos comandos de Windows CMD, el propósito de las construcciones `call`, `set`, `%%p`, `%var%`, y detalla la arquitectura implementada para la supervisión del bot, incluyendo el módulo `network_monitor`, así como la transición del antiguo mecanismo `client.run()` a un modelo controlado mediante `asyncio.run()` y `client.start()`.

1. ### Comandos esenciales de Windows CMD utilizados en los scripts
   1. ### `call` 
   `call` permite ejecutar otro archivo `.bat` o `.cmd` **sin abandonar** el proceso actual.
   Es indispensable cuando se activa un entorno virtual en Windows:
   ```cmd
      call ruta\al\entorno\Scripts\activate.bat
   ```
   Si se ejecuta un batch sin `call`, el script principal se detiene y el control **no vuelve** al archivo original.
   1. ### `set`
   `set` permite definir variables de entorno dentro del script CMD:
   ```cmd
      set PACKAGES=yt-dlp discord.py
   ```
   Estas variables son temporales y solo existen durante la ejecución del script.
   1. ### `%var%`
   Sintaxis de lectura de variables en CMD:
   ```cmd
      echo %PACKAGES%
   ```
   Siempre se evalúan de forma inmediata durante la lectura del script.
   1. ### `%%p`
   Los ciclos `for` de un `.cmd` utilizan **doble porcentaje** cuando se ejecutan dentro de un archivo `.cmd`:
   ```cmd
      for %%p in (%PACKAGES%) do (
         pip install --upgrade %%p
      )
   ```
   La diferencia es:
      - En **consola interactiva** → `%p`
      - En **archivos .cmd/.bat** → `%%p`
   Esto se debe al mecanismo de escape de CMD.
1. ### Módulo `network_monitor`
   El proyecto incorpora un módulo asincrónico llamado `network_monitor.py` diseñado para:
      1. Verificar conexión real a Internet sin bloquear el event loop.
      1. Esperar la restauración de Internet mediante reintentos controlados.
      1. Monitorear el heartbeat de Discord para detectar congelamientos del WebSocket.
      1. Generar mensajes de log con niveles apropiados cuando la red falla o el bot queda en estado inconsistente.
   ### Verificación de Internet
   ```python
      async def hay_internet(timeout=3.0) -> bool:
      # Usa asyncio.to_thread para no bloquear el event loop.
   ```
   Se utiliza un intento de conexión TCP a 8.8.8.8:53, lo cual es un método fiable y universal para verificar conectividad.
   ### Espera asíncrona hasta restaurar conexión
   ```python
      async def esperar_internet(retry_delay=10.0):
       # Reintentos con logs de advertencia
   ```
   Esta función permite suspender el inicio o la reconexión del bot hasta que se detecte que Internet está disponible nuevamente.
   ### Monitor de Heartbeat
   ```python
      async def monitor_heartbeat(client, timeout=60.0):
      # Observa client.latency y fuerza reconexión si se congela
   ```
   Discord puede dejar de enviar frames sin cerrar el WebSocket.
   En tales casos:
      - El bot sigue “vivo”.
      - El event loop sigue funcionando.
      - Pero el socket queda muerto (estado zombie).
   Este monitor detecta esa condición y obliga un reinicio del WebSocket mediante:
   ```python
      await client.close()
   ```
   ### Cambio arquitectónico: de `client.run()` a `client.start()` + `asyncio.run()`
   Discord.py proporciona tradicionalmente:
   ```python
      client.run(TOKEN)
   ```
   Sin embargo, este método:
      - Crea internamente un event loop.
      - Lo controla totalmente.
      - Cierra el loop al terminar.
      - No permite implementar supervisión avanzada.
      - No permite recovery robusto en caídas de red.
      - No permite reiniciar la sesión WebSocket de forma programática.
   En este proyecto se reemplaza por:
   ```python
      await client.start(TOKEN)
   ```
   Este método:
      - No crea un new event loop.
      - Permite controlar las reconexiones.
      - Permite cerrar la sesión sin matar el proceso.
      - Es compatible con supervisión externa (safe_main, watchdogs, heartbeat monitor).
   ### Event Loop principal administrado mediante `asyncio.run()`
   El event loop del proceso completo es gestionado explícitamente:
   ```python
      if __name__ == "__main__":
         asyncio.run(safe_main())
   ```
   Ventajas:
      - Permite correr tareas de fondo (monitores, watchdogs, supervisión).
      - Permite implementar un bucle supervisor:
      ```python
         while True:
            try:
               await client.start(TOKEN)
            except Exception:
               # recuperación, verificación de red, espera y reintento
      ```
      - Permite cerrar recursos en un bloque finally.
      - Permite manejar señales (ej. KeyboardInterrupt) sin colapsar el event loop.
   ### Patrón final de arranque seguro (safe_main)
   El arranque del bot sigue el patrón:
   ```python
      async def safe_main():

         await esperar_internet()
         
         asyncio.create_task(monitor_heartbeat(bot))

         while True:
            try:
                  await bot.start(TOKEN)
            except Exception:
                  await bot.close()
                  await esperar_internet()
                  await asyncio.sleep(3)
                  continue
            finally:
                  await bot.close()
   ```
   Este patrón garantiza:
      - Supervisión continua.
      - Recuperación de caídas inesperadas.
      - Reinicio automático ante fallos de red.
      - Cierre limpio del WebSocket.
      - No bloqueos del event loop.
      - Integración con ProcessPoolExecutor mediante shutdown_executor().

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
