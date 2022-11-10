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

fake = Faker()  # To put a name to the police.


# __ SQL __
def create_tables(input1, input2):
    cnx = mysql.connector.connect(user="root",
                                  password=input1,
                                  host="127.0.0.1",
                                  database=input2)

    cursor = cnx.cursor()

    try:
        cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
        cursor.execute("CREATE TABLE Boats_arrivals (Boat VARCHAR(255), Arrival_time INT, Departure_time INT)")

    except mysql.connector.errors.ProgrammingError:
        print("Creating the table...")
        time.sleep(2)
        print("Creating the table...")
        cursor.execute("DROP TABLE Boats")
        cursor.execute("DROP TABLE Boats_arrivals")
        cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
        cursor.execute("CREATE TABLE Boats_arrivals (Boat VARCHAR(255), Arrival_time INT, Departure_time INT)")
        time.sleep(2)
        print("Table created successfully!")

    return cnx, cursor


def add_all_columns(boat, cursor):
    attributes = vars(boat)
    for keys in attributes:
        format = type(attributes[keys])
        format = str(format)
        if keys == "port" or keys == "active" or keys == "priority" or keys == "name":
            continue
        if format == "<class 'str'>":
            query = "ALTER TABLE Boats ADD {} VARCHAR (255)".format(keys.capitalize())
        elif format == "<class 'datetime.datetime'>" or format == "<class 'datetime.date'>":
            query = "ALTER TABLE Boats ADD {} datetime".format(keys.capitalize())
        else:
            query = "ALTER TABLE Boats ADD {} INT ".format(keys.capitalize())
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
        query = f"INSERT INTO Boats_arrivals (Boat, Departure_time) VALUES ('{boat.name}',{time.time()-start});"
        cursor.execute(query)
        cnx.commit()

    except Exception:
        traceback.print_exc()


def insert_values_initial(boat, cnx, cursor):
    try:
        attributes = vars(boat)
        attributes.pop("port")
        attributes.pop("active")
        attributes.pop("priority")

        query = "INSERT INTO Boats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"  #You need to put %s as much as variables to input in to the dataset.
        values = tuple(attributes.values())
        cursor.execute(query, values)

        cnx.commit()

    except Exception:
        traceback.print_exc()


# __ SIMULATION __
class Boats:  # Initialize the boats class.
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
        self.economic_value = 0
        #self.tax = 0  # Put a 21% of tax in one thing, 10% in another and 5% in another.
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
        if random.randint(1, 20) == 10:
            self.merchandise = "Cocaine"
            self.economic_value = self.containers * 200

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

    def check_if_enter(self):
        while len(self.port.in_port) > (self.port.cargos_each * 3) + 3:
            time.sleep(random.randint(1, 5))
            print("There are too many boats in the loading area.")
            len(self.port.in_port)
        self.port.in_port.append(self.name)

    def out_entrance_queue(self):
        self.port.entrance_queue_locker.acquire()
        self.port.entrance_queue.remove(self.name)
        self.port.entrance_queue_locker.release()

    def into_load_off(self, iterations):
        x = 0
        while x == 0:
            for i in range(iterations):
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

    def out_load_off(self, iterations):
        for i in range(iterations):
            value = self.desired_cargo + "_" + str(i + 1)
            dictionary = self.port.cargo_dictionary.get(value)
            if self not in dictionary["cargo_list"]:
                continue

            dictionary["list_locker"].acquire()
            dictionary["cargo_list"].remove(self)
            self.port.in_port.remove(self.name)
            dictionary["list_locker"].release()
            break


class Ports:
    def __init__(self):
        self.cargos_each = 3
        self.entrance_queue = []
        self.entrance_queue_locker = threading.Lock()
        self.in_port = []
        self.cargo_dictionary = dict()
        self.initialise_queues()

    def initialise_queues(self):
        for x in range(self.cargos_each):
            model = "Small_cargo_" + str(x + 1)
            self.cargo_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock()
            }

        for x in range(self.cargos_each):
            model = "Medium_cargo_" + str(x + 1)
            self.cargo_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock()
            }

        for x in range(self.cargos_each):
            model = "Big_cargo_" + str(x + 1)
            self.cargo_dictionary[(model)] = {
                "cargo_list": list(),
                "list_locker": threading.Lock()
            }


class Police:
    def __init__(self):
        # Put a name to the police and an active attribute to know when the police is occupied.
        self.name = fake.name()
        self.active = True

    def search_boats(self, boat):
        while not self.active:
            time.sleep(3)

        self.active = False
        print(f"Police Detective {self.name} is going to search a boat.")

        time.sleep(2)  # Register the boat
        if boat.merchandise == "Item4":  # Condition if boat is carrying something illegal.
            print(f"Police Detective {self.name} found something illegal.")
            self.active = True
            boat.out_load_off(3)
            exit()  # Break to finalize the boat from the simulation

        else:
            self.active = True
            print("Everything okey!")


port = Ports()  # We create a general instance of the port as we want only 1 port.
police = Police()  # Same happens with the police.

locker_database = threading.Lock()


def main(name):  # This is the beginning of the simulation
    global port, police, database, cursor

    try:
        # A boat comes
        start = time.time()
        boat = Boats(name=name, port=port)
        # Calls the delay to make it random when the boats are arriving.
        boat.delay_in_arriving()
        locker_database.acquire()
        insert_boats_arrivals(start=start, boat=boat, cnx=database, cursor=cursor)
        locker_database.release()
        # Into the big queue
        boat.into_entrance_queue()
        print(f"{boat.name} entered the port queue.")
        # Check the priority of the boat (if it is in front or not).
        boat.priority_check()
        # Check if they can enter the port
        boat.check_if_enter()
        # Out of the big queue
        boat.out_entrance_queue()
        # Goes to the load_off area
        boat.into_load_off(port.cargos_each)
        # Time to get to the loading area
        time.sleep(random.randint(1, 5))
        print(f"{boat.name} entered the loading area.")
        # If police is suspicious, stop the main function and search the boat
        if random.randint(1, 15) == 1:
            police.search_boats(boat=boat)
        # Loads_off
        print(f"{boat.name} is loading off.")
        boat.loading_off()
        # Time to get to the exit.
        #time.sleep(random.randint(1, 5))
        boat.out_load_off(port.cargos_each)
        # Bye.
        locker_database.acquire()
        insert_boats_departures(start=start, boat=boat, cnx=database, cursor=cursor)
        insert_values_initial(boat=boat, cnx=database, cursor=cursor)  # This database is for the boats that are legal and finished the process.
        locker_database.release()

    except Exception:
        traceback.print_exc()


# ___ THIS PART IS WHERE THE CODE RUNS ___

number_of_boats = 10

print(f"{Fore.CYAN}WELCOME TO THE PROGRAM SIMULATION!{Style.RESET_ALL}\n"
      f"Here you will create a database of boat arrivals to an specific port. Let's start!")
print("----------------------------------------------------------------------")
print(f"{Fore.LIGHTWHITE_EX}First, we need to ask a couple of questions ... {Style.RESET_ALL}")


def create_new_tables():
    if str(input("Are you the code developer? ")).lower() == "no":
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
        add_all_columns(Boats(1, 0), cursor)

    else:
        password = str(input("Password: "))
        while password != "123456":
            print("That was incorrect")
            password = str(input("Password: "))

        input1 = "7deJuniode2002"
        input2 = "project"

        if str(input("Do you want to create the tables? ")).lower() == "yes":
            database, cursor = create_tables(input1, input2)
            add_all_columns(Boats(1, 0), cursor)
        else:
            database = mysql.connector.connect(user="root",
                                          password=input1,
                                          host="127.0.0.1",
                                          database=input2)

            cursor = database.cursor()

    return database, cursor

database, cursor = create_new_tables()

print("----------------------------------------------------------------------")
print(f"{Fore.LIGHTYELLOW_EX} __WELCOME TO THE SIMULATION__ {Style.RESET_ALL}")
start = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_boats) as executor:
    executor.map(main, range(number_of_boats))

finish = time.time()
print("----------------------------------------------------------------------")
print(f"The simulation time was {int(finish - start)} seconds.")
print("----------------------------------------------------------------------")
print(f"{Fore.CYAN}{Style.BRIGHT}If you want to take a look at the dataset, open TablePlus.")
print(f"See you next time! :){Style.RESET_ALL}")
