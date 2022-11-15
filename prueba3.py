import tkinter as tk
from PIL import ImageTk, Image


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulation")
        self.master.geometry('1300x1300')

        self.image = Image.open('Background_harbour.png')
        self.render = ImageTk.PhotoImage(self.image)

        self.label_img = tk.Label(self.master, image=self.render)
        self.label_img.grid(row=1, column=1, padx=10, pady=10)


def main():
    root = tk.Tk()
    main_window = GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()