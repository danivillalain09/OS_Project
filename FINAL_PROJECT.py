import threading
import time
import random
import concurrent.futures
from colorama import Fore, Style
import mysql.connector
import traceback
from datetime import date
import faker
import copy

fake = faker.Faker()


class SQLConnection:
    def __init__(self):
        self.create_answer = str(input("Do you want to create a new dataset? ")).lower()
        self.cnx = mysql.connector.connect(user="root",
                                           password="7deJuniode2002",
                                           host="127.0.0.1",
                                           database="project")

        self.cursor = self.cnx.cursor()
        self.create_new_tables()
        self.sql_locker = threading.Lock()

    def create_new_tables(self):
        if self.create_answer == "yes":
            try:
                self.cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
                self.cursor.execute(
                    "CREATE TABLE Boats_arrivals (Boat VARCHAR(255), Arrival_time INT, Departure_time INT)")
                self.cursor.execute("CREATE TABLE Machines (Machine VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Employees (Employee VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Storage_Area (Number VARCHAR(255))")

            except mysql.connector.errors.ProgrammingError:
                print("Creating the table...")
                time.sleep(2)
                print("Creating the table...")
                self.cursor.execute("DROP TABLE Boats")
                self.cursor.execute("DROP TABLE Boats_arrivals")
                self.cursor.execute("DROP TABLE Machines")
                self.cursor.execute("DROP TABLE Employees")
                self.cursor.execute("DROP TABLE Storage_Area")
                self.cursor.execute("CREATE TABLE Boats (Boat VARCHAR(255))")
                self.cursor.execute(
                    "CREATE TABLE Boats_arrivals (Boat VARCHAR(255), Arrival_time INT, Departure_time INT)")
                self.cursor.execute("CREATE TABLE Machines (Machine VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Employees (Employee VARCHAR(255))")
                self.cursor.execute("CREATE TABLE Storage_Area (Number VARCHAR(255))")
                time.sleep(2)
                print("Table created successfully!")

    def add_columns(self, boat, container, employee, machine):
        if self.create_answer == "yes":
            boat_attributes = vars(boat)
            for keys in boat_attributes:
                format = type(boat_attributes[keys])
                format = str(format)
                if keys == "sql" or keys == "mediator" or keys == "active" or keys == "priority" or keys == "name" or keys == "start":
                    continue
                if format == "<class 'str'>" or keys == "dock":
                    query = "ALTER TABLE Boats ADD {} VARCHAR (255)".format(keys.capitalize())
                elif format == "<class 'datetime.datetime'>" or format == "<class 'datetime.date'>":
                    query = "ALTER TABLE Boats ADD {} datetime".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Boats ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

            column_list = ["Time_in_queue", "Time_waiting_confirmation", "Time_in_dock", "Time_leaving"]
            for i in column_list:
                query = "ALTER TABLE Boats_arrivals ADD {} INT".format(i.capitalize())
                self.cursor.execute(query)

            machine = vars(machine)
            for keys in machine:
                format = type(machine[keys])
                format = str(format)
                if keys == "locker" or keys == "active" or keys == "name":
                    continue
                if format == "<class 'str'>":
                    query = "ALTER TABLE Machines ADD {} VARCHAR (255)".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Machines ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

            employee = vars(employee)
            for keys in employee:
                format = type(employee[keys])
                format = str(format)
                if keys == "mediator" or keys == "boat" or keys == "active" or keys == "dock" or keys == "finished" or keys == "name":
                    continue
                if format == "<class 'str'>" or keys == "dock" or format == "<class '__main__.Crane'>":
                    query = "ALTER TABLE Employees ADD {} VARCHAR (255)".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Employees ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

            container = vars(container)
            for keys in container:
                format = type(container[keys])
                format = str(format)
                if keys == "number":
                    continue
                if format == "<class 'str'>":
                    query = "ALTER TABLE Storage_Area ADD {} VARCHAR (255)".format(keys.capitalize())
                else:
                    query = "ALTER TABLE Storage_Area ADD {} INT ".format(keys.capitalize())
                self.cursor.execute(query)

    def insert_values_initial(self, boat):
        try:
            copy_boat = copy.copy(boat)
            attributes = vars(copy_boat)
            attributes.pop("sql")
            attributes.pop("mediator")
            attributes.pop("active")
            attributes.pop("priority")
            attributes.pop("start")

            query = "INSERT INTO Boats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = tuple(attributes.values())
            self.cursor.execute(query, values)

            self.cnx.commit()

        except Exception:
            traceback.print_exc()

    def insert_values_employees(self, employee):
        try:
            copy_employee = copy.copy(employee)
            attributes = vars(copy_employee)
            attributes.pop("finished")
            attributes.pop("mediator")
            attributes.pop("active")
            attributes.pop("boat")
            attributes.pop("dock")
            attributes["machine"] = employee.machine.name
            query = "INSERT INTO Employees VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = tuple(attributes.values())
            self.cursor.execute(query, values)

            self.cnx.commit()

        except Exception:
            traceback.print_exc()

    def get_starting_number(self):
        self.cursor.execute("SELECT Boat FROM Boats")
        result = self.cursor.fetchall()
        result_list = []
        for x in result:
            x = x[0]
            x = x.split(" ")
            x = x[1]
            result_list.append(int(x))
        if len(result_list) == 0:
            maximum = 0 + 1
        else:
            maximum = max(result_list) + 1

        return maximum

    def insert_boats_arrivals(self, starting_time, boat):
        try:
            query = f"INSERT INTO Boats_arrivals (Boat, Arrival_time) VALUES ('{boat.name}',{time.time() - starting_time});"
            self.cursor.execute(query)
            self.cnx.commit()

        except Exception:
            traceback.print_exc()

    def insert_boats_departures(self, starting_time, boat):
        try:
            query = f"UPDATE Boats_arrivals SET Departure_time= ({time.time() - starting_time}) WHERE Boat =('{boat.name}');"
            self.cursor.execute(query)
            self.cnx.commit()

        except Exception:
            traceback.print_exc()

    def insert_boats_time(self, column_name, starting_time, boat):
        try:
            self.cursor.execute(
                f"UPDATE Boats_arrivals SET {column_name}=({time.time() - starting_time}) WHERE Boat=('{boat.name}');")
            self.cnx.commit()

        except Exception:
            traceback.print_exc()

    def insert_machines(self, machine):
        try:
            copy_machine = copy.copy(machine)
            attributes = vars(copy_machine)
            attributes.pop("locker")
            attributes.pop("active")
            query = "INSERT INTO Machines VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = tuple(attributes.values())
            self.cursor.execute(query, values)

            self.cnx.commit()

        except Exception:
            traceback.print_exc()

    def insert_containers(self, container):
        try:
            container = copy.copy(container)
            attributes = vars(container)
            query = "INSERT INTO Storage_Area VALUES (%s, %s, %s)"
            values = tuple(attributes.values())
            self.cursor.execute(query, values)

            self.cnx.commit()

        except Exception:
            traceback.print_exc()


class Control:
    def __init__(self, n_boats, n_docks, sql_connection):
        # OVERALL SIMULATION VARIABLES
        self.number_of_boats = n_boats
        self.finished_boats = 0
        self.sql = sql_connection

        # FOR WORKERS
        self.active_workers = []  # This is the list of active workers.
        self.active_workers_locker = threading.Lock()  # Lock for the threads to not collide.
        self.finished = False  # This is the variable that will be used to end the simulation.

        # FOR POLICE
        self.police = Police()

        # FOR BOATS
        self.docks = dict()
        self.add_dock(n_docks)
        self.entrance_queue = []
        self.entrance_queue_locker = threading.Lock()
        self.boat_request = []
        self.boat_request_locker = threading.Lock()
        self.storage_area = []
        self.storage_area_locker = threading.Lock()

    def add_dock(self, n_docks):
        for x in range(n_docks):
            model = "Dock " + str(x + 1)
            self.docks[model] = {
                "Type": random.choice(["Type 1", "Type 2"]),
                "Boat": None,
                "Crane": None,
                "Containers": []
            }

    def entrance_confirmation(self, boat):
        if boat.priority != 0:
            time.sleep(3)
            boat.priority = self.entrance_queue.index(boat)

            return False

        else:
            return True

    def call_police(self, boat):
        if boat.checked_by_police == "No" and self.police.active:
            illegal = self.police.check_boat(boat)
            if illegal:
                return "Alarm"

    def dock_response_entry(self, boat):
        found = False
        allowed = "Yes"
        if random.randint(1, 20) == 1:
            if self.call_police(boat) == "Alarm":
                print(f"Police has been called for {boat.name}")
                allowed = "No"

        if allowed == "Yes":
            while not found:
                for docks in self.docks:
                    if self.docks[docks]["Boat"] is None:
                        self.docks[docks]["Boat"] = boat

                        return docks
                    else:  # If there is no space for the boat.
                        continue
        else:
            return "You are not allowed to enter the port"

    def crane_request(self, job, selected_boat):
        found = False
        for worker in self.active_workers:
            if worker.job == job:
                self.active_workers.remove(worker)
                unloading = worker.work(job, selected_boat)

                while not unloading:
                    time.sleep(2)

                self.active_workers.append(worker)
                found = True
                break
            else:
                continue

        return found

    def dock_response_leave(self, boat, boat_dock):
        self.call_transporter(boat)
        if self.docks[boat_dock]["Boat"] is boat:
            self.docks[boat_dock]["Boat"] = None
        else:
            print("Error: Boat not in dock.")

    def leave_confirmation(self):
        self.finished_boats += 1  # Cada vez que un barco sale, se suma uno a la variable.
        # Si llega a ser igual al número de barcos, se manda un mensaje a los trabajadores para que terminen.
        if self.finished_boats == self.number_of_boats:
            self.finished = True

    def call_transporter(self, boat):
        for worker in self.active_workers:
            if worker.job == "Transporter":
                self.active_workers.remove(worker)
                print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: A transporter has been called to {boat.dock}.")
                worker.work(job="Transporter", boat=boat)
                self.active_workers.append(worker)
                break

    def insert_sql(self, command, column, object, starting_time):
        self.sql.sql_locker.acquire()
        if command == "Arrival":
            self.sql.insert_boats_arrivals(starting_time, object)
        elif command == "Departure":
            self.sql.insert_boats_departures(starting_time, object)
        elif command == "Time":
            self.sql.insert_boats_time(column, starting_time, object)
        elif command == "Initial":
            self.sql.insert_values_initial(object)
        elif command == "Machines":
            self.sql.insert_machines(object)
        elif command == "Machines_Usage":
            self.sql.insert_machines_used(object)
        elif command == "Containers":
            self.sql.insert_containers(object)
        elif command == "Employees":
            self.sql.insert_values_employees(object)
        else:
            print("Error: Command not found.")
        self.sql.sql_locker.release()


class Crane:
    def __init__(self, name):
        self.name = name
        self.locker = threading.Lock()
        self.active = False
        self.speed = random.randint(5, 8)
        self.residual_value = random.randint(10000, 50000)
        self.fuel_consumption = int(self.speed * 1.5)
        self.fuel_capacity = 1000
        self.fuel_level = random.randint(0, self.fuel_capacity)
        self.times_used = 0
        self.bought = random.choice(["Purchased", "Leased"])

    def use_machine(self):
        self.times_used += 1
        time.sleep(self.speed)
        self.fuel_level -= self.fuel_consumption * self.speed
        if self.fuel_level <= 10:
            print(f"WORKER: {Fore.CYAN} Fuel level too low.{Style.RESET_ALL}")
            time.sleep(6)
            self.fuel_level = self.fuel_capacity
            print("WORKER: Refueled.")

        return True


class Transporter(Crane):
    def __init__(self, name):
        Crane.__init__(self, name)

    def use_machine(self):
        self.times_used += 1
        time.sleep(random.randint(10,15))

        return True


class Container:
    def __init__(self, number, weight, origin):
        self.number = number
        self.weight = weight
        self.origin = origin

    def hello(self):
        print("Hello")
        self.number = self.number


class Worker:
    def __init__(self, name, mediator, job):
        self.name = fake.name()
        self.nationality = fake.country()
        self.age = random.randint(18, 45)
        self.address = fake.street_name()

        self.mediator = mediator
        self.job = job

        if self.job == "Crane":
            self.machine = Crane("Crane " + str(name))
        if self.job == "Transporter":
            self.machine = Transporter("Transporter " + str(name))

        self.active = True
        self.dock = None
        self.boat = None
        self.finished = False
        self.salary = random.randint(1000, 2000)
        self.working_time = 0
        self.breaks = 0
        self.time_in_break = 0

    def simulation(self):
        self.mediator.active_workers_locker.acquire()
        self.mediator.active_workers.append(self)
        self.mediator.active_workers_locker.release()
        print(f"- {self.name} has started working: \n"
              f"    Machine: {self.machine.name}")

        start = time.time()
        time_until_break = time.time()
        while self.active:
            if self.breaks <= 1 and time.time() - time_until_break > random.randint(30, 50) and not self.machine.active:
                break_time = time.time()
                self.breaks += 1
                self.mediator.active_workers_locker.acquire()
                self.mediator.active_workers.remove(self)
                self.mediator.active_workers_locker.release()
                print(f"{Fore.LIGHTYELLOW_EX}- {self.name} has stopped working.{Style.RESET_ALL}")
                time.sleep(random.randint(5, 10))
                self.time_in_break += time.time() - break_time
                time_until_break = time.time()
                self.mediator.active_workers_locker.acquire()
                self.mediator.active_workers.append(self)
                self.mediator.active_workers_locker.release()
            try:
                if self.mediator.finished:
                    self.working_time += time.time() - start
                    self.mediator.insert_sql(command="Employees", column=None, object=self, starting_time=self)
                    self.mediator.insert_sql(command="Machines", object=self.machine, column=None, starting_time=None)
                    self.active = False
                    self.finished = True
                    exit()
            except Exception as e:
                traceback.print_exc()

    def work(self, job, boat):
        #print(f"{Fore.LIGHTMAGENTA_EX}- {self.name} is working.{Style.RESET_ALL}")
        self.machine.active = True
        self.boat = boat
        self.dock = self.boat.dock

        if job == "Crane":
            self.mediator.docks[self.dock]["Crane"] = self.machine
            job_finished = self.machine.use_machine()
            while not job_finished:
                time.sleep(2)
            for i in range(boat.containers):
                number = f"{boat.name.split(' ')[1]:0>3}{i:0>3}"
                container = Container(str(number), random.randint(100, 500), boat.place_of_origin)
                #self.mediator.insert_sql(command="Initial", object=container, column=None, starting_time=None)
                self.mediator.docks[self.dock]["Containers"].append(container)

            self.mediator.docks[self.dock]["Crane"] = None

        elif job == "Transporter":
            self.mediator.docks[self.dock]["Transporter"] = self.machine
            finished_transport = self.machine.use_machine()
            while not finished_transport:
                time.sleep(10)
                print(f"Something failed............. {self.name}")
            self.mediator.storage_area_locker.acquire()
            self.mediator.docks[self.dock]["Containers"] = self.mediator.docks[self.dock]["Containers"][:random.randint(1, 60)]
            for container in self.mediator.docks[self.dock]["Containers"]:
                self.mediator.storage_area.append(container)
                self.mediator.insert_sql(command="Containers", object=container, column=None, starting_time=None)
            self.mediator.storage_area_locker.release()
            self.mediator.docks[self.dock]["Containers"] = []
            self.mediator.docks[self.dock]["Transporter"] = None

        #print(f"{Fore.LIGHTMAGENTA_EX}- {self.name} finished transporting.{Style.RESET_ALL}")
        self.machine.active = False
        self.boat = None
        self.dock = None

        return True


class Police:
    def __init__(self):
        self.name = "Detective " + fake.name()
        self.active = True

    def check_boat(self, boat):
        boat.checked_by_police = "Yes"
        self.active = False
        print(f"{Fore.LIGHTRED_EX}POLICE{Style.RESET_ALL}: {self.name} is going to search {boat.name}.")
        time.sleep(5)
        if boat.merchandise == "Cocaine":
            print(f"{Fore.LIGHTRED_EX}POLICE{Style.RESET_ALL}: {self.name} found something illegal in {boat.name}.")
            self.active = True

            return True
        else:
            print(f"{Fore.LIGHTRED_EX}POLICE{Style.RESET_ALL}: {self.name} found nothing.")
            self.active = True

            return False


class Boats:
    def __init__(self, name, port_object, sql_connection, starting_time):
        # Attributes that make the boat know the other instances.
        self.name = "Boat " + str(name)  # Name of the boat
        self.mediator = port_object  # Port Object
        self.sql = sql_connection  # SQL Connection

        # Attributes that make the boat know its own state.
        self.active = False  # If the boat is active or not

        # Attributes that modify during the execution.
        self.priority = None  # Priority in the queue
        self.dock = None  # Dock where the boat is.
        self.start = starting_time

        # Attributes to fill in the table.
        self.place_of_origin = random.choice(
            ["United Kingdom", "Colombia", "Argentina", "Mexico", "England", "Germany", "China", "Thailand", "India"])
        self.departure_date = fake.date_time_between(start_date='-1y', end_date='now')
        self.arrival_date = date.today()
        self.model = random.choice(["Model 1", "Model 2", "Model 3"])
        self.merchandise = "Item1"
        self.containers = 0
        self.checked_by_police = "No"
        self.economic_value = 0
        self.tax = 0
        self.initialise_attributes()

    def initialise_attributes(self):
        if self.model == "Model 1":
            self.containers = random.randint(20, 50)
        elif self.model == "Model 2":
            self.containers = random.randint(51, 150)
        else:
            self.containers = random.randint(151, 250)

        item_list, price_list = ["Fruit", "Vegetables", "Clothes", "Technology", "Construction Material", "Toys"], \
                                [5, 6, 30, 150, 200, 10]
        key_value_of_items = dict(zip(item_list, price_list))
        self.merchandise = random.choice(item_list)
        self.economic_value = self.containers * key_value_of_items[self.merchandise]
        if random.randint(1, 200) == 1:
            self.merchandise = "Cocaine"
            self.economic_value = self.containers * 200

        self.tax = self.economic_value * 0.15

    def delay_in_arriving(self):
        while not self.active:
            time.sleep(5)
            if random.randint(1, 3) == 2:
                self.active = True
        #print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has arrived.")

    def get_into_queue(self):
        self.mediator.entrance_queue_locker.acquire()
        self.mediator.entrance_queue.append(self)
        self.priority = self.mediator.entrance_queue.index(self)
        self.mediator.entrance_queue_locker.release()

    def ask_entry_port(self):
        while not self.mediator.entrance_confirmation(self):
            time.sleep(1)
            continue
        print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has entered the port.")

    def out_of_queue(self):
        time.sleep(3)
        self.mediator.entrance_queue_locker.acquire()
        self.mediator.entrance_queue.remove(self)
        self.mediator.entrance_queue_locker.release()

    def ask_entry_dock(self):
        self.dock = self.mediator.dock_response_entry(self)
        while self.dock is None or self.dock == "You are not allowed to enter the port":
            if self.dock == "You are not allowed to enter the port":
                self.active = False
                self.mediator.leave_confirmation()
                self.mediator.insert_sql(command="Initial", column=None, boat=self, starting_time=None)
                exit()
            print(f"{self.name} cannot enter the port.")

            time.sleep(3)
        else:
            print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has docked in {self.dock}.")
            pass

    def unload_request(self, job):
        while not self.mediator.crane_request(job, selected_boat=self):
            print(f"{Fore.RED}CONTROL: {self.name} did not find a {job}.{Style.RESET_ALL}")
            time.sleep(3)

    def ask_leave_dock(self):
        self.mediator.dock_response_leave(self, self.dock)
        print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has left {self.dock}.")
        time.sleep(random.randint(1, 6))

    def ask_leave_port(self):
        self.mediator.leave_confirmation()
        print(f"{Fore.LIGHTBLUE_EX}CONTROL{Style.RESET_ALL}: {self.name} has left the port.")

    def simulation(self):
        try:
            # self.delay_in_arriving()
            self.mediator.insert_sql(command="Arrival", column=None, object=self, starting_time=self.start)
            activity_time = time.time()
            self.get_into_queue()
            self.ask_entry_port()
            self.out_of_queue()
            self.mediator.insert_sql(command="Time", column="Time_in_queue", object=self, starting_time=activity_time)
            activity_time = time.time()
            self.ask_entry_dock()
            self.mediator.insert_sql(command="Time", column="Time_waiting_confirmation", object=self, starting_time=activity_time)
            activity_time = time.time()
            self.unload_request("Crane")
            self.mediator.insert_sql(command="Time", column="Time_in_dock", object=self, starting_time=activity_time)
            activity_time = time.time()
            self.ask_leave_dock()
            self.ask_leave_port()
            self.mediator.insert_sql(command="Time", column="Time_leaving", object=self, starting_time=activity_time)
            self.mediator.insert_sql(command="Departure", column=None, object=self, starting_time=self.start)
            self.mediator.insert_sql(command="Initial", column=None, object=self, starting_time=None)

        except Exception as e:
            traceback.print_exc()



########################################################################################################################
# input1 = int(input("Hoy many loading areas do you want to simulate? "))
# number_of_boats = int(input("How many boats do you want to simulate? "))
########################################################################################################################
input1 = 8
number_of_boats = 5
number_of_cranes = int(input1/2)
if number_of_cranes == 0:
    number_of_cranes = 1

print("Starting simulation...")
time.sleep(2)
print(f"Number of boats: {number_of_boats}")
print(f"Number of docks: {input1}")
print(f"Number of cranes: {number_of_cranes}")

print("----------------------------------------------------------------------")
sql = SQLConnection()
control = Control(number_of_boats, input1, sql)
sql.add_columns(Boats(1, control, sql, 0), Container(0, 0, "E"), Worker(0, control, "Crane"), Crane("Crane"))
starting_number = sql.get_starting_number()
print("----------------------------------------------------------------------")

with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_cranes) as executor:
    worker_list = [Worker(i + 1, control, "Crane") for i in range(number_of_cranes)]
    for index, worker_list in enumerate(worker_list):
        executor.submit(worker_list.simulation)
        time.sleep(1)


    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        worker_list = [Worker(number_of_cranes + i, control, "Transporter") for i in range(1, 4)]
        for index, worker_list in enumerate(worker_list):
            executor.submit(worker_list.simulation)
            time.sleep(1)

        print("----------------------------------------------------------------------")
        print(f"{Fore.CYAN}WELCOME TO THE PROGRAM SIMULATION!{Style.RESET_ALL}\n"
              f"Here you will create a database of boat arrivals to an specific port. Let's start!")
        print("----------------------------------------------------------------------")
        start = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=int(number_of_boats)) as executor:
            boat_list = [Boats(i, control, sql, start) for i in range(starting_number, starting_number + number_of_boats)]
            for index, boat in enumerate(boat_list):
                executor.submit(boat.simulation)
        finish = time.time()
        print(f"----------------------------------------------------------------------\n"
              f"{Fore.CYAN}SIMULATION FINISHED!{Style.RESET_ALL}\n")
        print(f"Total time: {int(finish - start)} seconds.")