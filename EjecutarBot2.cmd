@echo off
title Bot de Discord - Ejecutando

REM Abriendo el directorio del proyecto.
cd /d "c:\Users\sebax\Desktop\Universidad\Proyectos_aleatorios\bot_dc_py\Dev2025"

REM Activando el entorno virtual con "call"
echo Activando el entorno virtual
echo .
call "c:\Users\sebax\Desktop\Universidad\Proyectos_aleatorios\bot_dc_py\Libs__\Scripts\activate.bat"

echo Actualizando pip...
pip install --upgrade pip

echo .
echo Buscando actualizaciones en yt-dlp y discord.py

REM Lista de Paquetes
set PACKAGES=yt-dlp discord.py


REM Actualizar cada paquete
for %%p in (%PACKAGES%) do (
	echo Actualizando %%p...
	pip install --upgrade %%p
)

echo Paquetes Actualizados, Actualizando el requirements.txt.
pip freeze > requirements.txt
echo requirements.txt actualizado.


echo Ejecutando bot_Optimizado.py
echo Presiona Ctrl + C para detener la ejecución manualmente.
py bot_Optimizado.py


echo.
echo El script ha terminado. Presiona cualquier tecla para cerrar.
pause >nul
exit /b

:: No debe ejecutarse
set RETRIES=0
set MAX_RETRIES=5

REM ----- Funcion para esperar Internet -----
:wait_net
echo Verificando conexion a internet...
ping 8.8.8.8 -n 1 >nul
if errorlevel 1 (
    echo No hay internet. Reintentando en 10 segundos...
    timeout /t 10 >nul
    goto wait_net
)
echo Conexion establecida.
echo.
goto runbot

REM ----- Ejecucion principal del bot -----
:runbot
echo Ejecutando bot_Optimizado.py...
py bot_Optimizado.py
set EXIT_CODE=%errorlevel%

if %EXIT_CODE%==0 (
    echo Bot terminado sin errores.
    exit /b
)

echo Error detectado. Codigo: %EXIT_CODE%

set /a RETRIES=%RETRIES%+1
echo Intento fallido %RETRIES% de %MAX_RETRIES%.

if %RETRIES% GTR %MAX_RETRIES% (
    echo Se alcanzó el maximo de reintentos. Abortando.
    exit /b
)

echo Esperando 10 segundos antes de reintentar...
timeout /t 10 >nul

goto wait_net