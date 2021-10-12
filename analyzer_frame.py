import threading as th

import tkinter as tk

import numpy as np

from jukebox import Jukebox


class AnalyzerFrame(tk.Frame):
    def __init__(self, master, jukebox: Jukebox):
        super().__init__(master, bg="orange")
        self.master = master
        self.create_widgets()
        self.jukebox = jukebox

        self._is_live = True

        self.after(100, self.draw_figs)

    def destroy(self):
        self._is_live = False
        return super().destroy()

    def create_widgets(self):
        self.canvas = tk.Canvas(master=self, width=600,
                                height=300, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=1)

    def draw_figs(self):

        self.canvas.delete("line")

        spec = self.jukebox.analyzer_spectrum()
        data_len = len(spec)
        if(data_len >= 1):
            height = self.canvas.winfo_height()
            width = self.canvas.winfo_width()

            spec = np.concatenate((spec[data_len//2:-1], spec[0:data_len//2]))

            spec = np.abs(spec)

            x = width * np.arange(len(spec)-1) // len(spec)-1
            y = height - 1 - spec * 10

            self.canvas.create_line(*zip(x, y), tag="line")

        if(self._is_live):
            self.after(50, self.draw_figs)


class OscilloFrame(tk.Frame):
    def __init__(self, master, jukebox: Jukebox):
        super().__init__(master, bg="orange")
        self.master = master
        self.create_widgets()
        self.jukebox = jukebox

        self._is_live = True

        self.after(100, self.draw_figs)

    def destroy(self):
        self._is_live = False
        return super().destroy()

    def create_widgets(self):
        self.canvas = tk.Canvas(master=self, width=600,
                                height=300, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=1)

    def draw_figs(self):

        self.canvas.delete("line")

        spec = self.jukebox.analyzer_oscillo()
        data_len = len(spec)
        if(data_len >= 1):
            height = self.canvas.winfo_height()
            width = self.canvas.winfo_width()

            spec = np.concatenate((spec[data_len//2:-1], spec[0:data_len//2]))

            spec = np.abs(spec)

            x = width * np.arange(len(spec)-1) // len(spec)-1
            y = height - 1 - spec * height

            self.canvas.create_line(*zip(x, y), tag="line")

        if(self._is_live):
            self.after(50, self.draw_figs)
