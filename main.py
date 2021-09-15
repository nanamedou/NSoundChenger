#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from graph_frame import GraphFrame
import tkinter as tk
from jukebox import *

import sys

OPENFILE = 0

if len(sys.argv) >= 2:
    OPENFILE = sys.argv[1]
else:
    OPENFILE = './sounds/sin.wav'

#OPENFILE='./British_Grenadiers.ogg.mp3'
#OPENFILE='./doremi.wav'

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
            self.jukebox.select_music(False, OPENFILE)
        openfile_btn = tk.Button(input_menu_frame,text=u'OpenFile', command=openfile)
        openfile_btn.pack(side=tk.LEFT)

        # 再生選択メニュー
        play_menu_frame = tk.Frame(self)
        play_menu_frame.pack(side=tk.TOP)
        rewind_btn = tk.Button(play_menu_frame,text='◀')
        rewind_btn.pack(side=tk.LEFT)
        start_btn = tk.Button(play_menu_frame,text=u'▶', fg='red', command=self.jukebox.play)
        start_btn.pack(side=tk.LEFT)
        stop_btn = tk.Button(play_menu_frame,text=u'■', fg='black', command=self.jukebox.stop)
        stop_btn.pack(side=tk.LEFT)

        # オシロ画面
        wave_graph = GraphFrame(self)
        wave_graph.pack(side = tk.TOP)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
