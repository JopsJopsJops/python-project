import yt_dlp
import tkinter as tk
from tkinter import filedialog

def download_video(url, save_path):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # pick best video + best audio, merge them
            'merge_output_format': 'mp4',          # final output in mp4
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'nopart': True,
            'overwrites': False,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("Video downloaded successfully!")

    except Exception as e:
        print("Error:", e)


url = "https://movies2watch.tv/watch-tv/watch-the-office-hd-39383.4891987"
save_path = "D:/downloads"

download_video(url, save_path)