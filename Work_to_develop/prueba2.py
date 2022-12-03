from tkinter import*
import random
import threading


window = Tk()


#Creating a canvas for images
harbour = Canvas(window, width = 1200,  height = 800, bg = "red")
harbour.pack()

# creating a background image
harbour_img = PhotoImage(file ="Background_harbour.png")
harbour_bg = harbour.create_image(0,0, anchor= NW, image= harbour_img )


# placing an image on the background
boat_img = PhotoImage(file ="boat.png")
boatimg = boat_img
boat = harbour.create_image(1100,450, anchor= NW, image= boat_img )

# creating button that starts the harbour thread
button_start = Button(harbour, text= "Start", command= lambda: threading.Thread(target=running_thread(number_of_boats,starting_number)).start())
button_window = harbour.create_window(600,20,anchor = NW,window=button_start)

def move_boat():
    boatx = random.randint(100,1000)
    boaty = random.randint(200,600)
    harbour.coords(boat,boatx,boaty)
    window.after(2000,move_boat)

#move_boat()
#button move boat
button_boat = Button(harbour, text= "move boat around", command= threading.Thread(target=move_boat()).start())
button_boat_win = harbour.create_window(1150,20,anchor = NW,window=button_boat)

#threading.Thread(target=move_boat()).start()
window.mainloop()