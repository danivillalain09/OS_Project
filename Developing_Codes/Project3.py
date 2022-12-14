import concurrent.futures
import time
import threading
import random
from colorama import Fore
import traceback
from colorama import Style
from faker import Faker
from datetime import date
import mysql.connector
import tkinter as tk
from PIL import ImageTk, Image

fake = Faker()  # To put a name to the police.

# __ SQL __
def create_new_database():
    #x = str(input("Are you the code developer? ")).lower()
    x = "yes"
    if x == "no":
        input1 = str(input("What is your password for SQL? "))
        print(f"{Fore.RED}NOTE: THIS CAN ONLY BE DONE ONCE. IF ERROR RERUN AND CHECK DATABASE:{Style.RESET_ALL} Boat_Simulation")
        question1 = str(input("Do you want to create a database? "))
        if question1 == "yes":
            database = mysql.connector.connect(user="root",
                                               password=input1,
                                               host="127.0.0.1")
            cursor = database.cursor()
            query = "CREATE database Boat_Simulation"
            cursor.execute(query)
            input2 = "Boat_Simulation"
            print("Database Name: Boat_Simulation")
        else:
            input2 = str(input("What is the name of you database? "))

        database, cursor = create_tables(input1, input2)
        add_all_columns(BoatSQL(), cursor)

    else:
        #password = str(input("Password: "))
        password = "123456"
        while password != "123456":
            print("That was incorrect")
            password = str(input("Password: "))

        input1 = "7deJuniode2002"
        input2 = "project"
        #y = str(input("Do you want to create the tables? ")).lower()
        y = "yes"
        if y == "yes":
            database, cursor = create_tables(input1, input2)
            add_all_columns(Boats(1, 0), cursor)
        else:
            database = mysql.connector.connect(user="root",
                                          password=input1,
                                          host="127.0.0.1",
                                          database=input2)

            cursor = database.cursor()

    return database, cursor


def create_tables(input1, input2):
    cnx = mysql.connector.connect(user="root",
                                  password=input1,
                                  host="127.0.0.1",
                                  database=input2)

    cursor = cnx.cursor()

    try:
        cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
        cursor.execute("CREATE TABLE Boats_Arrivals (Boat VARCHAR(255), Arrival_time INT, Departure_time INT)")
        cursor.execute("CREATE TABLE Boats_Guilty (Boat VARCHAR(255))")

    except mysql.connector.errors.ProgrammingError:
        print("Creating the table...")
        time.sleep(2)
        print("Creating the table...")
        cursor.execute("DROP TABLE Boats")
        cursor.execute("DROP TABLE Boats_Arrivals")
        cursor.execute("DROP TABLE Boats_Guilty")
        cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
        cursor.execute("CREATE TABLE Boats_Arrivals (Boat VARCHAR(255), Arrival_time INT, Departure_time INT)")
        cursor.execute("CREATE TABLE Boats_Guilty (Boat VARCHAR(255))")
        time.sleep(2)
        print("Table created successfully!")

    return cnx, cursor


def add_all_columns(boat, cursor):
    attributes = vars(boat)
    for keys in attributes:
        format = type(attributes[keys])
        format = str(format)
        if keys in ["port", "active", "priority", "name", "render", "boat", "boat_image", "position_x", "position_y", "in_cargo"]:
            continue
        if format == "<class 'str'>":
            query = "ALTER TABLE Boats ADD {} VARCHAR (255)".format(keys.capitalize())
            query2 = "ALTER TABLE Boats_Guilty ADD {} VARCHAR (255)".format(keys.capitalize())
        elif format == "<class 'datetime.datetime'>" or format == "<class 'datetime.date'>":
            query = "ALTER TABLE Boats ADD {} datetime".format(keys.capitalize())
            query2 = "ALTER TABLE Boats_Guilty ADD {} datetime".format(keys.capitalize())
        else:
            query = "ALTER TABLE Boats ADD {} INT".format(keys.capitalize())
            query2 = "ALTER TABLE Boats_Guilty ADD {} INT".format(keys.capitalize())
        cursor.execute(query)
        cursor.execute(query2)

    column_list = ["time_waited_entrance_area", "time_loading_off_area"]
    for i in column_list:
        query = "ALTER TABLE Boats_arrivals ADD {} INT".format(i.capitalize())
        cursor.execute(query)


def insert_boats_arrivals(start, boat, cnx, cursor):
    try:
        query = f"INSERT INTO Boats_arrivals (Boat, Arrival_time) VALUES ('{boat.name}',{time.time()-start});"
        cursor.execute(query)
        cnx.commit()

    except Exception:
        traceback.print_exc()


def insert_boats_departures(start, boat, cnx, cursor):
    try:
        query = f"UPDATE Boats_arrivals SET Departure_time= ({time.time()-start}) WHERE Boat=('{boat.name}');"
        cursor.execute(query)
        cnx.commit()

    except Exception:
        traceback.print_exc()


def insert_boats_time(column_name, first_time,  boat, cnx, cursor):
    try:
        cursor.execute(f"UPDATE Boats_arrivals SET {column_name}=({time.time() - first_time}) WHERE Boat=('{boat.name}');")
        cnx.commit()

    except Exception:
        traceback.print_exc()


def insert_values_initial(boat, cnx, cursor):
    try:
        attributes = boat.__dict__
        value_list = []

        for i in attributes:
            if i not in ["port", "active", "priority", "boat", "render", "boat_image", "position_x", "position_y", "in_cargo"]:
                value_list.append(attributes[i])

        query = "INSERT INTO Boats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"  #You need to put %s as much as variables to input in to the dataset.
        values = tuple(value_list)
        cursor.execute(query, values)

        cnx.commit()

    except Exception:
        traceback.print_exc()


def get_starting_number(cursor):
    cursor.execute("SELECT Boat FROM Boats_arrivals")
    result = cursor.fetchall()
    result_list = []
    for x in result:
        x = x[0]
        x = x.split(" ")
        x = x[1]
        result_list.append(int(x))
    if len(result_list) == 0:
        maximum = 0
    else:
        maximum = max(result_list) + 1

    return maximum


def insert_boats_guilty(boat, cnx, cursor):
    try:
        attributes = vars(boat)

        query = "INSERT INTO Boats_Guilty VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"  # You need to put %s as much as variables to input in to the dataset.
        values = tuple(attributes.values())
        cursor.execute(query, values)

        cnx.commit()

    except Exception:
        traceback.print_exc()


# __ SIMULATION __
# We do this class to have a class that when changed, it does not affect the database.
class BoatSQL:
    def __init__(self):
        self.name = "Boat " + str(0)
        self.port = 0
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


class Boats:  # Initialize the boats class.
    def __init__(self, name, port):
        self.name = "Boat " + str(name)
        self.port = port
        self.position_x = 0
        self.position_y = 0
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
        self.in_cargo = "None"
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
                self.in_cargo = value
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
        print(f"{self.name} is going home.")
        dictionary = self.port.cargo_dictionary.get(self.in_cargo)

        dictionary["list_locker"].acquire()
        dictionary["cargo_list"].remove(self)
        self.port.in_port.remove(self.name)
        dictionary["list_locker"].release()

    def create_image(self, app):
        """
        self.boat_image = Image.open('CargoShip.png')
        self.boat_image= self.boat_image.resize((60, 60))
        self.render = ImageTk.PhotoImage(self.boat_image)
        self.boat = app.create_image(1050, 200 + (self.priority*80), anchor='nw', image=self.render)
        """
        image = Image.open("boat.png")
        tk_image = ImageTk.PhotoImage(image)
        label = tk.Label(app, text=self.name, image=tk_image, compound='top')
        label.pack()

    def move_boat(self, app, x_position, y_position):
        """
        self.boat_image = Image.open('CargoShip.png')
        self.boat_image= self.boat_image.resize((60, 60))
        self.render = ImageTk.PhotoImage(self.boat_image)
        self.boat = app.create_image(x_position, y_position, anchor='nw', image=self.render)
        """
        self.boat_image = tk.Label(app, text=f"{self.name} moved. Finished!")
        self.boat_image.pack()

    def move_boat_cargo(self, app):
        dictionary = self.port.cargo_dictionary.get(self.in_cargo)
        self.boat_image = Image.open('CargoShip.png')
        self.boat_image = self.boat_image.resize((60, 60))
        self.render = ImageTk.PhotoImage(self.boat_image)
        x_position = dictionary["position_x"]
        y_position = dictionary["position_y"]
        self.boat = app.create_image(x_position, y_position, anchor='nw', image=self.render)

        """
        self.boat_image = tk.Label(app, text=f"{self.name} moved. Position {self.in_cargo}")
        self.boat_image.pack()
        """


class Ports:
    def __init__(self):
        self.cargos_each = 1
        self.people_cargos = 1
        self.entrance_queue = []
        self.entrance_queue_locker = threading.Lock()
        self.in_port = []
        self.in_port_people = []
        self.cargo_dictionary = dict()
        self.people_dictionary = dict()
        self.initialise_queues()
        # self.initialise_people()

    def initialise_queues(self):
        for x in range(self.cargos_each):
            model = "Small_cargo_" + str(x + 1)
            self.cargo_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock(),
                "position_x": 600,  # If i = 0, then 600 + i*30 = 600. BUT If i = 1, then 600 + i*30 = 630. ALL.
                "position_y": 200
            }

        for x in range(self.cargos_each):
            model = "Medium_cargo_" + str(x + 1)
            self.cargo_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock(),
                "position_x": 600,
                "position_y": 400
            }

        for x in range(self.cargos_each):
            model = "Big_cargo_" + str(x + 1)
            self.cargo_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock(),
                "position_x": 600,
                "position_y": 600
            }

    def initialise_people(self):
        for x in range(self.people_cargos):
            model = "Small_cargo_" + str(x + 1)
            self.people_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock()
            }

        for x in range(self.people_cargos):
            model = "Medium_cargo_" + str(x + 1)
            self.people_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock()
            }

        for x in range(self.people_cargos):
            model = "Big_cargo_" + str(x + 1)
            self.people_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock()
            }


class Police:
    def __init__(self):
        # Put a name to the police and an active attribute to know when the police is occupied.
        self.name = "Detective " + fake.name()
        self.active = True

    def search_boats(self, boat):
        while not self.active:
            time.sleep(3)

        self.active = False
        print(f"{self.name} is going to search a boat.")
        boat.checked_by_police = "Yes"

        time.sleep(2)  # Register the boat
        if boat.merchandise == "Cocaine":  # Condition if boat is carrying something illegal.
            print(f"{self.name} found something illegal.")
            self.active = True
            boat.out_load_off(3)
            locker_database.acquire()
            insert_values_initial(boat=boat, cnx=database, cursor=cursor)
            insert_boats_guilty(boat=boat, cnx=database, cursor=cursor)
            locker_database.release()
            exit()  # Break to finalize the boat from the simulation

        else:
            self.active = True
            print("Everything okey!")


class Window(tk.Frame):
    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):
        # parameters that you want to send through the Frame class.
        tk.Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        # with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("GUI")
        # allowing the widget to take the full space of the root window
        self.pack(fill="both", expand=1)

    def first_create_boats(self, boat):
        load = Image.open("boat.png")
        render = ImageTk.PhotoImage(load)

        # labels can be text or images
        boat.boat_image = tk.Label(self, image=render, text=boat.name, compound="top")
        boat.boat_image.image = render
        boat.boat_image.place(x=900, y=200 + (boat.priority*80))

    def show_boat(self, boat):
        load = Image.open("boat.png")
        render = ImageTk.PhotoImage(load)

        # labels can be text or images
        boat.boat_image = tk.Label(self, image=render, text=boat.name, compound="top")
        boat.boat_image.image = render
        boat.boat_image.place(x=random.randint(200, 900), y=random.randint(200, 900))

    def boat_destroy(self, boat):
        boat.boat_image.destroy()


port = Ports()  # We create a general instance of the port as we want only 1 port.
police = Police()  # Same happens with the police.
root = tk.Tk()
root.geometry("1200x1200")

# creation of an instance
application = Window(root)

finished_boats = 0
locker_database = threading.Lock()
movement_lock = threading.Lock()


def main(name):  # This is the beginning of the simulation
    global port, police, database, cursor, application, finished_boats

    try:
        # A boat comes
        start = time.time()
        boat = Boats(name=name, port=port)
        # Calls the delay to make it random when the boats are arriving.
        boat.delay_in_arriving()
        # Into the big queue
        first_time = time.time()
        locker_database.acquire()
        insert_boats_arrivals(start=start, boat=boat, cnx=database, cursor=cursor)
        locker_database.release()
        print(f"{boat.name} entered the port.")
        boat.into_entrance_queue()
        time.sleep(2)
        application.first_create_boats(boat)
        time.sleep(5)
        # Check if the boat needs gasoline
        #boat.refuel()
        # Check the priority of the boat (if it is in front or not).
        boat.priority_check()
        # Check if they can enter the port
        boat.check_if_enter()
        # Out of the big queue
        boat.out_entrance_queue()
        locker_database.acquire()
        insert_boats_time(column_name="Time_waited_entrance_area", first_time=first_time, boat=boat, cnx=database,
                          cursor=cursor)
        locker_database.release()
        # Goes to the load_off area
        first_time = time.time()
        boat.into_load_off()
        application.boat_destroy(boat)
        time.sleep(2)
        application.show_boat(boat)
        # Time to get to the loading area
        time.sleep(random.randint(1, 5))
        print(f"{boat.name} entered the loading area.")
        # If police is suspicious, stop the main function and search the boat
        if random.randint(1, 10) == 1:
            police.search_boats(boat=boat)
        # Loads_off
        print(f"{boat.name} is loading off.")
        boat.loading_off()
        # Time to get to the exit.
        #time.sleep(random.randint(1, 5))
        boat.out_load_off()
        # Bye.
        locker_database.acquire()
        insert_boats_time(column_name="Time_loading_off_area", first_time=first_time, boat=boat, cnx=database,
                          cursor=cursor)
        insert_boats_departures(start=start, boat=boat, cnx=database, cursor=cursor)
        insert_values_initial(boat=boat, cnx=database, cursor=cursor)
        locker_database.release()
        application.boat_destroy(boat)
        finished_boats += 1

        if finished_boats == number_of_boats:
            exit()

    except Exception:
        traceback.print_exc()


# ___ THIS PART IS WHERE THE CODE RUNS ___
number_of_boats = 5

print(f"{Fore.CYAN}WELCOME TO THE PROGRAM SIMULATION!{Style.RESET_ALL}\n"
      f"Here you will create a database of boat arrivals to an specific port. Let's start!")
print("----------------------------------------------------------------------")
print(f"{Fore.LIGHTWHITE_EX}First, we need to ask a couple of questions ... {Style.RESET_ALL}")
database, cursor = create_new_database()
starting_number = get_starting_number(cursor=cursor)
print("----------------------------------------------------------------------")
print(f"{Fore.LIGHTYELLOW_EX} __WELCOME TO THE SIMULATION__ {Style.RESET_ALL}")
start = time.time()


with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(main, range(starting_number, starting_number + number_of_boats))
    root.mainloop()

finish = time.time()
print("----------------------------------------------------------------------")
print(f"The simulation time was {int(finish - start)} seconds.")
print("----------------------------------------------------------------------")
print(f"{Fore.CYAN}{Style.BRIGHT}If you want to take a look at the dataset, open TablePlus.")
print(f"See you next time! :) {Style.RESET_ALL}")