import psutil, time, logging, os, pathlib

import subprocess

class test:
    """
    Este modulo se diseña con el fin de probrar y medir
    el rendimiento del bot en los diferentes sistemas
    Obteniendo metricas de:
        **Uso de CPU**
        **Uso de Memoria**
        **Consumo de Red**
        **Tiempo de Ejecución**
    
    Registrando todo en un txt

    ----------------------------

    Utiliza librerias como
        **psutil** - Para medir métricas del sistema.
        **time** - Para medir los tiempos de ejecución.
        **logging** - para matener un log de los test/Pruebas.
    """

    FFMPEG_PATH = "ffmpeg"  # O la ruta completa si es necesario
    STREAM_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # Se puede cambiar las opciones para ver las diferencias
    FFMPEG_OPTIONS = [
        "-vn", "-f", "s16le", "-ar", "48000", "-ac", "2",  # PCM 48kHz estéreo
        "-loglevel", "error",
        "-"
    ]

    LOG_FILE = pathlib.Path(__file__).parent.parent / "test.txt"

    # Configurando el Logger
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger()

    def log_metrics(self, process: psutil.Process, start_time: float):
        mem_info = process.memory_info()
        net_info = psutil.net_io_counters()
        cpu_percent = process.cpu_percent(interval=1.0)

        self.logger.info(f"Uso de la CPU: {cpu_percent}%")
        self.logger.info(f"Memory RSS: {mem_info.rss / (1024 * 1024):.2f} MB")
        self.logger.info(f"Memory VMS: {mem_info.vms / (1024 * 1024):.2f} MB")
        self.logger.info(f"Network: Sent={net_info.bytes_sent} bytes, Recv={net_info.bytes_recv} bytes")

        end_time = time.time()
        self.logger.info(f"Tiempo Transcurrido: {(end_time - start_time):.2f} seconds\n")

    def run_test(self):
        self.logger.info("------ Ejecutando el Test ------")
        # logger.info(f"FFmpeg Options: {' '.join(FFMPEG_OPTIONS)}")

        start_time = time.time()

        # Lanza ffmpeg como subproceso para leer el audio
        process = subprocess.Popen(
            [self.FFMPEG_PATH, '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5',
            '-i', self.STREAM_URL, *self.FFMPEG_OPTIONS],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Obtén proceso del sistema para mediciones
        p = psutil.Process(process.pid)

        try:
            while process.poll() is None:
                self.log_metrics(p, start_time)
                time.sleep(2)  # Cada 2 segundos
        except KeyboardInterrupt:
            self.logger.info("Test cancelled by user.")
        finally:
            process.kill()
            self.logger.info("Process terminated.")
            self.log_metrics(p, start_time)

if __name__ == "__main__":
    test.run_ffmpeg_test()
    print(f"Benchmark completo. Revisa el archivo {test.LOG_FILE}")