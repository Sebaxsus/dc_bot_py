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
echo .


echo Ejecutando bot_Optimizado.py
echo Presiona Ctrl + C para detener la ejecución manualmente.
py bot_Optimizado.py


echo.
echo El script ha terminado. Presiona cualquier tecla para cerrar.
pause >nul