import os, pathlib, sys
from dotenv import load_dotenv
# No se como usar el logger, pero lo dejo comentado por si acaso
# import logging # No se usa en este momento
# from logging.handlers import RotatingFileHandler

# # Configuración del logger
# LOG_FILE = pathlib.Path(__file__).parent.parent / 'Dev2025/logs/bot.log'
# LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
# logger = logging.getLogger(__name__)

# Agregando el path de la carpeta modules para importar los modulos
sys.path.append(str(pathlib.Path(__file__).parent.parent / "Dev2025/modules"))

# Load environment variables from .env file
DOTENV_PATH = pathlib.Path(__file__).parent / '.env'
load_dotenv(DOTENV_PATH)

# Get the environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')