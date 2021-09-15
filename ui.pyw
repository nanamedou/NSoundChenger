import tkinter as tk
from graph_frame import GraphFrame
from scrollable_frame import ScrollableFrame

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="green")
        self.master = master
        self.pack(side=tk.TOP ,fill=tk.BOTH, expand=1)

        self.create_widgets()

    def create_widgets(self):
        self.garphs = []
        self.add_graph()

    def add_graph(self):
        new_graph = GraphFrame(self)
        new_graph.pack(fill=tk.BOTH, expand=1)
        self.garphs.append(new_graph)


root = tk.Tk()
#main_wnd = ScrollableFrame(root)
#main_wnd.pack(fill=tk.BOTH, expand=1)
app = Application(master=root)
#app = Application(master=main_wnd.scrollable_frame)
app.mainloop()