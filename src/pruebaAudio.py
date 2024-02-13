import pyaudio, io, sys, pydub, pytube, requests
import numpy as np
import wave
import discord
import re
import time
import spotipy
from dotenv import dotenv_values, load_dotenv
import os, pprint
from subprocess import Popen, PIPE

#:track_previous: :arrow_forward: :pause_button: :track_next:  Emojis

#load_dotenv()

#env = os.getenv('TOKEN') Se usa cuando tenemos el metodo load_dotnev()


#dotenv_values crea un diccionario de las llaves (Varibles del .env) y su Valor (Lo que esta en esa Variable a.k.a Key)

enviromentVariables = dotenv_values("bot_dc_py/src/.env")
spClientId=enviromentVariables['SPOTIPY_CLIENT_ID']
spClientSecret=enviromentVariables['SPOTIPY_CLIENT_SECRET']
spApi = "https://api.spotify.com/v1/"
spEndPoint = "/track/{track_id}"


#https://open.spotify.com/intl-es/track/0F7pTAMyTJFdvveeQ1GfVL?si=177a7d9c30474fea
#https://open.spotify.com/intl-es/track/5TmFTHZp7HjBXjjsFvCY6h?si=92184070569c4e95
#https://api.spotify.com/v1/


#print(enviromentVariables, enviromentVariables['TOKEN'])

def pruebaSpotipy():
    auth_manager = spotipy.oauth2.SpotifyClientCredentials(client_id=spClientId, client_secret=spClientSecret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    spPlaylist = sp.user_playlist(user=sp,playlist_id='4lEJgwqKnjvl4LRFC2Tpp2')
    def pruebaStreamAudio(urlCancion):
        rawCancion = sp.track(urlCancion)
        print(rawCancion)
        None

    def prueba_MusicaSpoti():
        scope = "user-read-playback-state,user-modify-playback-state"
        sp = spotipy.Spotify(client_credentials_manager=spotipy.oauth2.SpotifyOAuth(client_id=spClientId,client_secret=spClientSecret,redirect_uri='http://localhost:3000',scope=scope))
        # Shows playing devices
        res = sp.devices()
        pprint.pprint(res)

        # Change track
        sp.start_playback(uris=['spotify:track:0upFohXrGxIIAjyaJmCkMU'])

        # Change volume
        sp.volume(100)
        time.sleep(2)
        sp.volume(50)
        time.sleep(2)
        sp.volume(100)

    #prueba_MusicaSpoti()

    #print(type(spPlaylist['tracks']['items'][4])) #lista
    def verKeyArtistTrack(artists):
        print('Entro a artistas')
        #print(spPlaylist['tracks']['items'][4]['track']['artists'])
        mensajeArtistas = "|"
        Keys = ['external_urls', 'href', 'id', 'name', 'type', 'uri', 'external_urls', 'href', 'id', 'name', 'type', 'uri']
        for artist in artists:
            #print(f"Nombre de artista: {artist['name']}")
            mensajeArtistas += f" {artist['name']} |"

                
        return mensajeArtistas

    #verKeyArtistTrack(spPlaylist['tracks']['items'][4]['track']['artists'])
    #print(spPlaylist)
    def obtenerDatosDeCadaTrackEnPl(pLTracks):
        Keys = ['album', 'artists', 'disc_number', 'duration_ms', 'episode', 'explicit', 'external_ids', 'external_urls', 'href', 'id'
                , 'is_local','is_playable', 'name', 'popularity', 'preview_url', 'track', 'track_number', 'type', 'uri']
        Canciones = {}
        #cancionIndex = 0
        for trak in range(0, len(pLTracks)):
            Canciones[f'{trak}'] = {
            'nombreCancion' : pLTracks[trak]['track']['name'],
            'href' : pLTracks[trak]['track']['href'],
            'numeroCancion' : pLTracks[trak]['track']['track_number'],
            'idCacion' : pLTracks[trak]['track']['id'],
            'uri' : pLTracks[trak]['track']['uri'],
            'Artista' : verKeyArtistTrack(pLTracks[trak]['track']['artists'])
            }
        return Canciones

    #a = obtenerDatosDeCadaTrackEnPl(spPlaylist['tracks']['items'])
    #for i in range(0, len(a)):
        print(a[f'{i}'])
        print("\n")
                   





    #obtenerDatosDeCadaTrackEnPl(spPlaylist['tracks'])
    #                                                                         Indice de lista de items 
    #obtener dictcionario de una cancion de una playlist spPlaylist['tracks']['items'][4]['track']
    def obetenerIdDeUnaCancionEnPlaylist(dictTrackPL):
        Keys = ['album', 'artists', 'disc_number', 'duration_ms', 'episode', 'explicit', 'external_ids', 'external_urls', 'href', 'id'
                , 'is_local', 'name', 'popularity', 'preview_url', 'track', 'track_number', 'type', 'uri']
        
        #album y artist son diccionarios
        #for i in dictTrackPL:
            #print(i)
        for key in Keys:
            dictTrackPL[key]

        #print(f"nombre: {dictTrackPL['name']} numeroEnPlaylist: {dictTrackPL['track_number']}, {dictTrackPL['track']} id: {dictTrackPL['id']} uri: {dictTrackPL['uri']}")
    
    #obetenerIdDeUnaCancionEnPlaylist(spPlaylist['tracks']['items'][4]['track'])

    def verCadaDatodelasTracks(itemsDict):
        for i in itemsDict:
            #print(i)
            print(f"Tipo de el dato Tracks: {type(itemsDict)}")
            diccionarioTrack =itemsDict['track']
            for j in diccionarioTrack:
                print(f"Key Name: {j} Value: {diccionarioTrack[j]}")
            break
            for dictKey in ['added_at','added_by','is_local','primary_color','track','video_thumbnail']:
                print(f"Key Name: {i} Value: {t[dictKey]}" )
            break

    #verCadaDatodelasTracks(spPlaylist['tracks']['items'][4])

    #ver que tiene cada item
    def verItemDeCadaTrackDeUnaPlayList():
        #['tracks']['items'] = lista, items, so el idex de cada item son, 0 added_at, 1 added_by, 2 is_local, 3 primary_color, 4 track, 5 video_thumbnail,6 added_at

        for t in spPlaylist['tracks']['items']:
            #print(f"Item Name: {t} Value: {t.values()} \n")
            #print(f"Item Name: {t}")
            print(f"tipo de dato de items: {type(t)}")
            for i in t:
                print(f"Item Name: {i}  Value: {t[i]}\n")
            break
        print("\n\n\n ['tracks']['items'] = lista, items, so el idex de cada item son\n0 added_at\n1 added_by\n2 is_local\n3 primary_color\n4 track\n5 video_thumbnail\n6 added_at")
    
    #verItemDeCadaTrackDeUnaPlayList()
    def obtenerItemsDeUnaPl():
        for i in spPlaylist['tracks']:
            print(i, '\t', spPlaylist['tracks'][i], '\n Fin Loop')
        
    def keysDictPlaylist():
        Keys = ['collaborative', 'description', 'external_urls', 'followers', 'href', 'id', 'images', 'name', 'owner', 'primary_color', 'public', 'snapshot_id', 'tracks', 'type', 'uri']
        for i in spPlaylist:
            print(i)
            time.sleep(5)

    #keysDictPlaylist()
    
    #print(spPlaylist['tracks'])
    

#pruebaSpotipy()



#Como busacar y sacar los datos de la busqueda por yt usando Pytube
def buscarVideoYtConPytube():
    buffer = io.BytesIO()

    texto = "velitas - Brytiago"

    ytSearch = pytube.Search(texto)
    ytSearchObj = ytSearch.results


    print(ytSearchObj[0].video_id)
    print(("https://www.youtube.com/watch?v=" + ytSearchObj[0].video_id))
    url = "https://www.youtube.com/watch?v=" + ytSearchObj[0].video_id
    yt = pytube.YouTube("https://www.youtube.com/watch?v=" + ytSearchObj[0].video_id)

    Minutos = int(yt.length / 60)
    Segundos = yt.length % 60

    return {
        'buffer': buffer,
        'link': url,
        'Miniatura': yt.thumbnail_url,
        'Source': url,
        'Titulo': yt.title,
        'Canal' : yt.author,
        'Duracion' : f"{Minutos}:{Segundos}"
    }

#cancion = buscarVideoYtConPytube()
#print(cancion['buffer'] , cancion['link'], cancion['Miniatura'], cancion['Source'], cancion['Titulo'], cancion['Canal'], cancion['Duracion'])


#def pruebaBusqueda(txt):
    #return "https://www.youtube.com/watch?v=" + pytube.Search(txt).results[0].video_id

#print(pruebaBusqueda("Velitas Brytiago"))



txtPrb = "asd asd 2q2123 dggas da we playlist  https://www.youtube.com/playlist?list=PLq4RAMp8kLaKOrMlJf-M82iZWUjzgPzoo"

#Prueba de filtar una url de playlist y sacar solo la url
def esPlaylistYT(texto):
    tmp = False
    texto = texto.split()
    #print(texto)
    for i in texto:
        #if "https://www.youtube.com/playlist?list=" in i:
            #print("Entro Primer IF")
        if i.startswith("https://www.youtube.com/playlist?list=") == True:
            #print(i, " ", tmp)
            texto = i
            tmp = True
            break
    return {
        'bool' : tmp,
        'url' : texto
        }
#aleatoria = esPlaylistYT(txtPrb)
#print(aleatoria)
#print(aleatoria['bool'], aleatoria['url'])

#Como usar la funcion de playlist de pytube y sacar la info de esa playlist
def PruebaDeUsodePlaylistPytube():
    pList = pytube.Playlist("https://www.youtube.com/playlist?list=PLq4RAMp8kLaKOrMlJf-M82iZWUjzgPzoo")

    print(pList)
    print(pList.title)

    for audio in pList.video_urls:
        print(audio)
        ytVid = pytube.YouTube(audio)
        minutos = int(ytVid.length / 60)
        segundos = ytVid.length % 60
        print(f"Titulo: {ytVid.title} Descripcion: {ytVid.description} Duracion: {minutos}:{segundos} ThumbnailLink:{ytVid.thumbnail_url} Author: {ytVid.author}")
        break
 
#PruebaDeUsodePlaylistPytube()
def PruebaDeUsoPytubeConLink():

    buffer = io.BytesIO()

    yt = pytube.YouTube('https://www.youtube.com/watch?v=XYl_SiQM-ww')

    audio_stream = yt.streams.filter(only_audio=True).first()

    audio_data = io.BytesIO(audio_stream.stream_to_buffer(buffer))

    buffer.seek(0)

    print(audio_data, " asd ", audio_data.seekable() , " asd " , buffer.read())
    print(buffer.read())

    audio = pydub.AudioSegment.from_file(buffer, format="mp4")

    print(type(buffer))

    print(type(audio))

    print('Audio raw: ', type(audio.raw_data), "Audio sin el raw: ", type(audio))

    bytesRaw = audio.raw_data



    pcm_audio = discord.AudioSource()

    print('\n Adicosource Dc: ', discord.AudioSource, " buffer con el audiosource: ", )

    print()



    p = pyaudio.PyAudio()

    audio = pydub.AudioSegment.from_file('C:/Users/sebax/Music/Triste.mp3', format="mp3")# Para Local

    sample_width = audio.sample_width
    channels = audio.channels
    framerte = audio.frame_rate
    volumeIndB = audio.rms
    duration = audio.duration_seconds

    print('Sample witdh\t', 'chnnels\t', 'frameRate\t', 'VolumedB\t', 'Duration')
    print(sample_width,'\t', channels,'\t',framerte,'\t',volumeIndB, ' \t ',duration)

    stream = p.open(
            format=p.get_format_from_width(sample_width),
            channels=(channels),
            rate=(framerte),
            output=True
        )

    pcm = discord.PCMAudio(stream)


    print(pcm, type(pcm))

    #Como usar el buffer com ffmpegPcmaudio y que el bot lea el buffer
    print(discord.FFmpegPCMAudio(source=buffer, pipe=True))

    print('audio stream: ', type(stream))

    #data = wf.readframes(1024)
    #while data:
        #stream.write(data)
        #data = wf.readframes(1024)

    stream.write(audio.raw_data)

    stream.stop_stream()

    stream.close()

    p.terminate()


def pruebaDeFiltradoDeUrlYTiempodeProceso():
    cst = time.process_time()
    st = time.time()

    texto = "https://www.youtube.com/watch?v=XYl_SiQM-ww"

    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    url = re.findall(regex, texto)

    tmp = texto.split("https://www.youtube.com/watch?v=")
    tmp = texto.removeprefix("https://www.youtube.com/watch?v=")
    print(tmp)
    for i in tmp:
        if i.startswith("https:"):
            tmp = i

    en = time.time()
    cen = time.process_time()

    print(tmp)
    print(url[0][0])

    print("Tiempor transcurrido ", en - st, " seg")
    print("Tiempor transcurrido Cpu ", cen - cst, " seg")

