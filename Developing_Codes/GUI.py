import tkinter as tk


class App():
    def __init__(self):
        self.frame = tk.Tk()
        self.show_frame()

    def show_frame(self):
        self.frame.title("Boat_port")
        self.frame.mainloop()

    def print_label(self):
        label = tk.Label(self.frame, text="Sebas es maricon.")
        label.pack()


app = App()