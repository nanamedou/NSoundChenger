from math import trunc
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np


class GraphFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="orange")
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(1,1,1)
        self.line, = self.ax.plot(np.random.rand(100))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH ,expand=1)
        self.movie = ani.FuncAnimation(self.fig, self.draw_figs, interval=1000)
        

       # self.v_x = tk.DoubleVar(value=0)
       # self.x_var = tk.Scale(self,variable=self.v_x,orient=tk.HORIZONTAL, from_=-0.3, to=0, resolution=0.01,command=lambda e: self.draw_figs())
       # self.x_var.pack(fill=tk.X )

    def draw_figs(self, deta):
        

        self.line.set_ydata(np.random.rand(100))

        return self.line,
