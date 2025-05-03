import discord

# #Colores embed Azul= 0x2c76dd, Rojo= 0xdf1141, Verde= 0x0eaa51
# AZUL,ROJO,VERDE,DARK_PURPLE,DARK_BLUE = 0x2c76dd, 0xdf1141,0x0eaa51,0x71368A,0x206694
# TEAL,DARK_RED,DARK_GREEN = 0x1ABC9C, 0x992D22,0x1F8B4C


def MensajeBasico(titulo: str, texto: str, color: int, icon_Url: str = None) -> discord.embeds.Embed:
    """
    """
    em = discord.Embed(
            title=titulo,
            description=texto,
            colour=color
        )
    
    em.set_footer(icon_url=icon_Url)

    return em

def esUrl(texto):
    tmp = False
    texto = texto.split()
    for i in texto:
        if i.startswith("https:"):
            tmp = True
    return tmp

def format_audio_seconds(seconds):
    if seconds is None:
        return "desconocido"
    mins, secs = divmod(int(seconds), 60)
    return f"{mins}:{secs:02}"