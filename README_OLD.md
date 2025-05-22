# Bienvenido al proyecto Elbulloso
## Antes de empezar hay dos formas de instalacion y uso del bot.
 1. Usando tu maquina principal con [Python](https://www.python.org/) y [FFmpeg](https://ffmpeg.org/).
 2. Usando [Docker](https://www.docker.com/).
---
### Instalando el bot usando Python y FFmpeg
> [!NOTE]
> 🔔 **Si no tiene FFmpeg instalado en tu Maquina y en las Variables de entorno LEE ESTO**
>
> Para que el bot pueda reproducir la musica proviniente de un **stream de bits** \
(Esto se hace para no descargar la cancion en tu maquina) \
> Por esto es importante tener instalado y configurado [FFmpeg](https://ffmpeg.org/)


Para empezar si ves esto en el navegador clona el repositorio dentro de tu maquina usando 
~~~bash
git clone https://github.com/Sebaxsus/dc_bot_py.git
~~~
Luego de clonarlo entra en la carpeta `BOT_DC_PY` y crea un **Entorno Virtual** o Entra a la carpeta `Dev2025` si no vas a crear uno.
> [!NOTE]
> 🔔 **Si vas a crear un entorno virtual LEE ESTO** 
>Como el encargado de ejecutar python va a ser el entorno virtual incluyendo las dependencias el `Python.exe` Debe ser el que se crea **Dentro de la carpeta de entorno Virtual**.\
\
> **[Como crear un entorno Virtual en Python 3.12.0](https://docs.python.org/es/3.12/tutorial/venv.html)**
>
>El ejecutable de python del entorno virtual suele estar la siguiente ruta:
> ~~~cmd example-good
> /EntornoVirtual/Scripts/python.exe
> ~~~

- abre una consola con `Python 3.12.0^` para instalar las dependecias necesarias usando el siguiente comando
~~~python example-good
pip install requirements.txt
~~~
- Depues de obtener la direccion de instalación crea un archivo .txt en el lugar que prefieras para crear el script de inicializacion del bot.
- El script consiste en:
  1. Desactivar los logs inecesarios de `echo` usando `@echo off`.
  2. Establecerle un titulo a la ventana de `cmd` usando `title` seguido de **El Titulo - Que quieras**
  3. Movemos el directorio activo de la ventana a la carpeta `Dev2025` usando
        - `cd` mueve el directorio de trabajo de la ventana a una ruta especificada
        > [!WARNING]
        > ⚠️ \
        > **Dentro de la unidad actual de la ventana**
        - `/d` se encarga de cambiar la unidad a la especificada en la ruta \
         **Es decir** que si tengo dos unidades de almacenamiento `C: | E:` y tengo mi carpeta instalada en:
            ~~~powershell
            c:\Users\sebax\Desktop\Universidad\Proyectos_aleatorios\bot_dc_py\Dev2025
            ~~~
          Y por alguna razon mi ventana de `cmd` abre en la unidad `E:` entonces mi comando:
            ~~~cmd
            cd /d "c:\Users\sebax\Desktop\Universidad\Proyectos_aleatorios\bot_dc_py\Dev2025"
            ~~~
          Movera la unidad de la ventana a la unidad `C:` en el directorio `\Users\sebax\Desktop\Universidad\Proyectos_aleatorios\bot_dc_py\Dev2025`
        - En conclusion el tercer comando en nuestro script `cmd` debe quedar
          ~~~cmd
            cd /d "c:\Users\sebax\Desktop\Universidad\Proyectos_aleatorios\bot_dc_py\Dev2025"
          ~~~
  4. Para mostrar mas contexto de lo que esta pasando en script mandamos dos "**Logs/echo**"
        - El primero es para mostrar que se va a ejecutar el bot en python \
        Usando `echo Ejecutando El bot en Python`
        - El segundo echo es para indicar como terminar el proceso del bot \
        Esto es util al momento de dejar de usar el bot. \
        `echo Presiona Ctrl + C para detener la ejecución manualmente.`
  5. Para obligar a que la ventana se quede abierta al momento de ejecutar el script si ocurre un error se usa:
      - ~~~cmd
        echo .
        ~~~
  6. Por ultimo agregamos un mensaje de salida al momento de terminar la ejecucion del script
      - ~~~cmd
        echo El script ha terminado. Presiona cualquier tecla para cerrar.
        pause >nul
        ~~~
### El script deberia quedar asi:
~~~bash
@echo off
title Bot de Discord - Ejecutando
cd /d "c:\Directorio_de_instalacion\bot_dc_py\Dev2025"

echo Ejecutando bot_Optimizado.py
echo Presiona Ctrl + C para detener la ejecución manualmente.
"c:\Directorio_de_instalacion\bot_dc_py\EntornoVirtual\Scripts\python.exe" bot_Optimizado.py

:: Opcionalmente, puedes dejar esto si quieres que la ventana permanezca abierta si el script termina por error.
echo.
echo El script ha terminado. Presiona cualquier tecla para cerrar.
pause >nul

~~~

> [!IMPORTANT]
> **Como actualizar las librerias con pip**
>
> Para actualizar las librerias instaladas con pip se usa
> ~~~bash
> python.exe -m pip install --upgrade pip yt-dlp
> ~~~
> este comando se encarga de actualizar si se puede pip y en este caso tambien se agrego la dependencia yt-dlp.
>
> **Para revisar que dependencias se pueden actualizar usando pip se usa**
> ~~~
> python.exe pip install pip-review
> ~~~
> [Explicacion](https://stackoverflow.com/questions/47071256/how-to-update-upgrade-a-package-using-pip)