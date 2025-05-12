# Usando una imagen de python 
FROM python:3.12.10-slim

# Pisando la Build jsjs
LABEL maintainer="Sebastian Garcia [Sebaxsus](https://github.com/Sebaxsus) <sebastiangarcia1198@gmail.com>"
# Creando el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar librerías nativas
RUN apt-get update && apt-get install -y \
    build-essential \
    libcurl4-openssl-dev \
    libssl-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiando los archivos necesarios
COPY bot_Optimizado.py .
COPY utils.py .
COPY yt_wrapper.py .
COPY requirements.txt .
COPY test.txt .
COPY .cache .

# Instalando las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponiendo un puerto a la app (No se si me sirva de algo)
# EXPOSE 5000

# Comando a ejecutar por defecto
CMD ["python", "bot_Optimizado.py"]