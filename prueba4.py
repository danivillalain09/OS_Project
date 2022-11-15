import tkinter as tk
from PIL import ImageTk, Image
import random
from faker import Faker
from datetime import date
import time
import threading

fake = Faker()
class Boats1:  # Initialize the boats class.
    def __init__(self, name, port):
        self.name = "Boat " + str(name)
        self.port = port
        # Starting here, these are the attributes for each of the boats created.
        self.active = False  # If the boat is not active, then it means that it is not in the simulation.
        self.place_of_origin = random.choice(
            ["United Kingdom", "Colombia", "Argentina", "Mexico", "England", "Germany", "China", "Thailand", "India"])
        self.departure_date = fake.date_time_between(start_date='-1y', end_date='now')
        self.arrival_date = date.today()
        self.priority = 0
        self.model = random.choice(["Small", "Medium", "Big"])
        self.gasoline = random.choice(["Yes", "No", "No", "No", "No", "No"])
        self.desired_cargo = self.model + str("_cargo")
        # To know what cargo it wants depending on the model (This can be changed).
        self.merchandise = "Item1"
        self.containers = 0
        self.checked_by_police = "No"
        self.economic_value = 0
        self.tax = 0  # Put a 21% of tax in one thing, 10% in another and 5% in another.
        self.initialise_attributes()

    def initialise_attributes(self):
        if self.model == "Small":
            self.containers = random.randint(20, 50)
        elif self.model == "Medium":
            self.containers = random.randint(51, 150)
        else:
            self.containers = random.randint(151, 250)

        item_list, price_list = ["Fruit", "Vegetables", "Clothes", "Technology", "Construction Material", "Toys"], \
                                [5, 6, 30, 150, 200, 10]
        key_value_of_items = dict(zip(item_list, price_list))
        self.merchandise = random.choice(item_list)
        self.economic_value = self.containers * key_value_of_items[self.merchandise]
        if random.randint(1, 50) == 10:
            self.merchandise = "Cocaine"
            self.economic_value = self.containers * 200

        self.tax = self.economic_value * 0.15

    def delay_in_arriving(self):
        while not self.active:
            time.sleep(random.randint(1, 4))
            if random.randint(1, 3) == 2:
                self.active = True

    def into_entrance_queue(self):
        self.port.entrance_queue_locker.acquire()
        self.port.entrance_queue.append(self.name)
        self.priority = self.port.entrance_queue.index(self.name)
        self.port.entrance_queue_locker.release()

    def priority_check(self):  # If it is not the first in line, it is not going in.
        while self.priority != 0:
            time.sleep(3)
            self.priority = self.port.entrance_queue.index(self.name)

    def refuel(self):
        if self.gasoline == "Yes":
            print(f"{self.name} needs gasoline.")
            time.sleep(random.randint(5, 10))
            self.out_entrance_queue()
            self.into_entrance_queue()

    def check_if_enter(self):
        while len(self.port.in_port) > (self.port.cargos_each * 3):
            time.sleep(random.randint(1, 5))
            print("There are too many boats in the loading area.")
            len(self.port.in_port)
        self.port.in_port.append(self.name)

    def out_entrance_queue(self):
        self.port.entrance_queue_locker.acquire()
        self.port.entrance_queue.remove(self.name)
        self.port.entrance_queue_locker.release()

    def into_load_off(self):
        x = 0
        while x == 0:
            for i in range(self.port.cargos_each):
                value = self.desired_cargo + "_" + str(i + 1)
                dictionary = self.port.cargo_dictionary.get(value)
                if dictionary["list_locker"].locked() or len(dictionary["cargo_list"]) > 0:
                    continue

                # print("The cargo is not locked or without any boat. Appending to it.")

                dictionary["list_locker"].acquire()
                dictionary["cargo_list"].append(self)
                dictionary["list_locker"].release()
                x = 1
                break

    def loading_off(self):
        if self.model == "Small":
            time.sleep(self.containers / 5)
        elif self.model == "Medium":
            time.sleep(self.containers / 10)
        elif self.model == "Medium":
            time.sleep(self.containers / 10)

    def out_load_off(self):
        for i in range(self.port.cargos_each):
            value = self.desired_cargo + "_" + str(i + 1)
            dictionary = self.port.cargo_dictionary.get(value)
            if self not in dictionary["cargo_list"]:
                continue

            dictionary["list_locker"].acquire()
            dictionary["cargo_list"].remove(self)
            self.port.in_port.remove(self.name)
            dictionary["list_locker"].release()
            break


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulation")

        self.harbour = tk.Canvas(self.master, width=1200, height=800, bg="white")
        self.harbour.pack(pady=20, padx=20)

        self.background = Image.open('Background_harbour.png')
        self.render_background = ImageTk.PhotoImage(self.background)
        self.harbour.create_image(0, 0, anchor="nw", image=self.render_background)
        #

        #self.boat_image = Image.open('boat.png')
        #self.render_boat = ImageTk.PhotoImage(self.boat_image)
        #self.boat = self.harbour.create_image(1000, 650, anchor="center", image=self.render_boat)
        #print("Boat created.")

    def init_boat(self):
        time.sleep(5)
        self.move_boat(self.boat)
        print("Boat moved.")

    def move_boat(self, boat):
        self.harbour.move(boat, 100, 100)


def main():
    window = tk.Tk()
    application = GUI(window)
    window.mainloop()
    application.init_boat()


if __name__ == '__main__':
    main()