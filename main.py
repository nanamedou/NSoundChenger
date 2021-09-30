#!/usr/bin/env python3
# -*- coding: utf-8 -*-

FFMPEG_PATH = 'I:\\ffmpeg'

import sys

import os
from uuid import SafeUUID

from graph_frame import GraphFrame
import tkinter as tk
from jukebox import *

OPENFILE = 0
SAVEFILE = 'hogehoge.mp3'

if len(sys.argv) >= 2:
    OPENFILE = sys.argv[1]
else:
    OPENFILE='./sounds/British_Grenadiers.ogg.mp3'

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="green")
        self.master = master
        self.pack(side=tk.TOP ,fill=tk.BOTH, expand=1)

        self.create_widgets()

    def create_widgets(self):

        self.jukebox = Jukebox()

        self.jukebox.select_music(False, OPENFILE)

        # 入力選択メニュー
        input_menu_frame = tk.Frame(self)
        input_menu_frame.pack(side=tk.TOP)
        record_btn = tk.Button(input_menu_frame,text='●',fg='red')
        record_btn.pack(side=tk.LEFT)
        def openfile():
            typ = [("音声ファイル",".wav .mp3 .mp4 .ogg"),("","*")]
            dir = os.path.abspath(os.path.dirname(__file__))
            OPENFILE = tk.filedialog.askopenfilename(filetypes = typ,initialdir = dir)
            self.jukebox.select_music(False, OPENFILE)
        openfile_btn = tk.Button(input_menu_frame,text=u'OpenFile', command=openfile)
        openfile_btn.pack(side=tk.LEFT)

        def savefile():
            if(self.jukebox.is_recording):
                self.jukebox.record_stop()
                self.jukebox.record_save(SAVEFILE)
            else:
                self.jukebox.record_start()
        savefile_btn = tk.Button(input_menu_frame,text=u'SaveFile', command=savefile)
        savefile_btn.pack(side=tk.LEFT)

        # 再生選択メニュー
        play_menu_frame = tk.Frame(self)
        play_menu_frame.pack(side=tk.TOP, fill=tk.X)
        rewind_btn = tk.Button(play_menu_frame,text='◀', command=lambda:self.jukebox.select_music(False, OPENFILE))
        rewind_btn.pack(side=tk.LEFT)
        start_btn = tk.Button(play_menu_frame,text=u'▶', fg='red', command=self.jukebox.play)
        start_btn.pack(side=tk.LEFT)
        stop_btn = tk.Button(play_menu_frame,text=u'■', fg='black', command=self.jukebox.stop)
        stop_btn.pack(side=tk.LEFT)

        self.gain_bar = tk.Scale(play_menu_frame,orient=tk.HORIZONTAL, fg='black', from_ = 0.0, to = 2.0, resolution=0.1,command=self.jukebox.set_gain)    # 音量変更バー
        self.gain_bar.set(1.0)
        self.gain_bar.pack(side=tk.TOP, fill=tk.X)

        self.spshift_bar = tk.Scale(play_menu_frame,orient=tk.HORIZONTAL, fg='black', from_ = -30, to = 30, resolution=1,command=self.jukebox.set_spshift)    # 音色変更バー
        self.spshift_bar.set(0)
        self.spshift_bar.pack(side=tk.TOP, fill=tk.X)

        # オシロ画面
        wave_graph = GraphFrame(self)
        wave_graph.pack(side = tk.TOP)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
