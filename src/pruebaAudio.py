import pyaudio, io, sys, pydub, pytube
import numpy as np
import wave
import discord
import re
import time
#:track_previous: :arrow_forward: :pause_button: :track_next:  Emojis

#buffer = io.BytesIO()

#yt = pytube.YouTube('https://www.youtube.com/watch?v=XYl_SiQM-ww')
cst = time.process_time()
st = time.time()

texto = "https://www.youtube.com/watch?v=XYl_SiQM-ww"

#regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

#url = re.findall(regex, texto)

tmp = texto.split("https://www.youtube.com/watch?v=")
#tmp = texto.removeprefix("https://www.youtube.com/watch?v=")
#print(tmp)
for i in tmp:
    if i.startswith("https:"):
        tmp = i

en = time.time()
cen = time.process_time()

print(tmp)
#print(url[0][0])

print("Tiempor transcurrido ", en - st, " seg")
print("Tiempor transcurrido Cpu ", cen - cst, " seg")

exit(0)

audio_stream = yt.streams.filter(only_audio=True).first()

audio_data = io.BytesIO(audio_stream.stream_to_buffer(buffer))

buffer.seek(0)

#print(audio_data, " asd ", audio_data.seekable() , " asd " , buffer.read())
#print(buffer.read())

audio = pydub.AudioSegment.from_file(buffer, format="mp4")

print(type(buffer))

print(type(audio))

print('Audio raw: ', type(audio.raw_data), "Audio sin el raw: ", type(audio))

bytesRaw = audio.raw_data



#pcm_audio = discord.AudioSource()

print('\n Adicosource Dc: ', discord.AudioSource, " buffer con el audiosource: ", )

print()



p = pyaudio.PyAudio()

#audio = pydub.AudioSegment.from_file('C:/Users/sebax/Music/Triste.mp3', format="mp3") Para Local

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


print(discord.FFmpegPCMAudio(source=buffer, pipe=True))

print('audio stream: ', type(stream))

#data = wf.readframes(1024)
#while data:
#    stream.write(data)
#    data = wf.readframes(1024)

#stream.write(audio.raw_data)

stream.stop_stream()

stream.close()

p.terminate()