import tkinter as tk
from PIL import ImageTk, Image

window = tk.Tk()


#Creating a canvas for images
harbour = tk.Frame(window, width=1200,  height=800, bg="red")

# creating a background image
harbour_img = ImageTk.(file="Background_harbour.png")
harbour.ImageTk(0, 0, anchor=NW, image= harbour_img )
harbour.pack()


window.mainloop()