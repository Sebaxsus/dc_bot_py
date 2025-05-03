import tkinter as tk
from tkinter import ttk, messagebox
import threading
import yt_dlp
import pyaudio
import subprocess
import time

search_results = []

# Parámetros generales
BUFFER_SIZE = 8192
FFMPEG_RECONNECT_FLAGS = ['-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '2']

def buscar_videos():
    query = entry.get()
    if not query:
        messagebox.showwarning("Advertencia", "Ingresa un título.")
        return

    listbox.delete(0, tk.END)
    formats_combo['values'] = []
    search_results.clear()
    status_label.config(text="🔍 Buscando...")

    def run_search():
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                for entry_info in info['entries']:
                    # print("Entry: ", entry_info)
                    title = entry_info.get('title', 'Sin título')
                    duration = entry_info.get('duration', 0)
                    search_results.append(entry_info)
                    listbox.insert(tk.END, f"{title} ({duration // 60}:{duration % 60:02} min)")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        status_label.config(text="✅ Búsqueda completada")

    threading.Thread(target=run_search).start()

def cargar_formatos(event):
    index = listbox.curselection()
    if not index:
        return
    video_info = search_results[index[0]]
    audio_formats = [f for f in video_info['formats'] if f['vcodec'] == 'none'and f['audio_ext'] in ['m4a', 'webm']]
    formats_combo['values'] = [
        f"{f['format_id']} - {f['ext']} - {f['acodec']} - {f.get('abr', '?')}kbps"
        for f in audio_formats
    ]
    formats_combo.current(0)

def reproducir_stream():
    index = listbox.curselection()
    if not index:
        messagebox.showwarning("Selecciona un video", "Debes seleccionar un video.")
        return

    format_id = formats_combo.get().split(" - ")[0]
    video_info = search_results[index[0]]

    audio_format = next((f for f in video_info['formats'] if f['format_id'] == format_id), None)
    if not audio_format:
        messagebox.showerror("Error", "No se encontró el formato seleccionado.")
        return

    stream_url = audio_format['url']
    title = video_info.get('title', 'Desconocido')
    uploader = video_info.get('uploader', 'Canal desconocido')
    duration = video_info.get('duration', 0)

    status_label.config(text=f"▶️ Reproduciendo: {title} - {uploader}")

    def stream_audio():
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True)

        ffmpeg_cmd = [
            'ffmpeg',
            *FFMPEG_RECONNECT_FLAGS,
            '-i', stream_url,
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            '-'
        ]

        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        start = time.time()
        try:
            while True:
                data = process.stdout.read(BUFFER_SIZE)
                if not data:
                    break
                stream.write(data)
        except Exception as e:
            messagebox.showerror("Error en reproducción", str(e))
        finally:
            elapsed = int(time.time() - start)
            mins, secs = divmod(elapsed, 60)
            stream.stop_stream()
            stream.close()
            p.terminate()
            process.kill()
            messagebox.showinfo("🎧 Finalizado", f"Reproducción terminada.\n\n"
                                                f"📌 Título: {title}\n"
                                                f"📺 Canal: {uploader}\n"
                                                f"⏱️ Duración esperada: {duration // 60}:{duration % 60:02}\n"
                                                f"🕒 Tiempo reproducido: {mins}:{secs:02}")
            status_label.config(text="✅ Reproducción finalizada")

    threading.Thread(target=stream_audio).start()

# GUI
root = tk.Tk()
root.title("YouTube Stream Player 🎧")
root.geometry("640x580")

tk.Label(root, text="🔎 Buscar video:").pack(pady=5)
entry = tk.Entry(root, width=60)
entry.pack()

tk.Button(root, text="Buscar", command=buscar_videos).pack(pady=5)

listbox = tk.Listbox(root, width=80, height=6)
listbox.pack(pady=5)
listbox.bind('<<ListboxSelect>>', cargar_formatos)

tk.Label(root, text="🎚️ Formato de audio:").pack()
formats_combo = ttk.Combobox(root, state='readonly', width=50)
formats_combo.pack(pady=5)

tk.Button(root, text="🎵 Reproducir", command=reproducir_stream).pack(pady=10)

status_label = tk.Label(root, text="Estado: Esperando búsqueda...")
status_label.pack(pady=10)

root.mainloop()
