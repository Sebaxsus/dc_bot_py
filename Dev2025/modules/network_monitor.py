import asyncio
import socket
import time
from typing import Optional

# Se asume que el proyecto ya tiene un logger configurado.
# Aquí simplemente lo importas.
# from modules.logger import logger


async def hay_internet(timeout: float = 3.0) -> bool:
    """
    Verifica conectividad real sin bloquear el event loop
    mediante asyncio.to_thread()
    """
    def _check():
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except Exception:
            return False

    return await asyncio.to_thread(_check)


async def esperar_internet(
    retry_delay: float = 180.0,
    warn_every: int = 1
):
    """
    Espera hasta que vuelva la conexión a Internet.
    Nunca bloquea el event loop.
    
    retry_delay: segundos entre reintentos (3m | 180s)
    warn_every: cada cuántos reintentos emitir el log de warning
    """
    intentos = 0

    while True:
        if await hay_internet():
            print("Conexión a Internet restaurada.")
            return
        if intentos >= 5:
            print("No se pudo reconectar, Cerrando programa.")
            return
        
        intentos += 1
        if intentos % warn_every == 0:
            print("No hay conexión a Internet. Reintentando...")

        await asyncio.sleep(retry_delay)


async def monitor_heartbeat(
    client,
    timeout: float = 60.0,
    check_interval: float = 10.0,
):
    """
    Monitorea el heartbeat de discord.py para detectar congelamientos.
    
    client.latency devuelve la latencia WS en segundos (float).
    Si .latency se queda indefinido o por encima de un umbral prolongado,
    se considera que la conexión está congelada.
    """
    while True:
        latency = client.latency  # segundos

        # Si la latencia es None o se dispara demasiado
        if latency is None or latency > timeout:
            print(
                f"Heartbeat sospechoso. Latencia={latency}. " +
                f"Timeout={timeout}. Intentando reconectar."
            )
            try:
                await client.close()  # fuerza reconexión del WS
            except Exception as e:
                print(f"No se pudo cerrar el cliente para reconexión: {e}")

        await asyncio.sleep(check_interval)
