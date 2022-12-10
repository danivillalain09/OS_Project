import random
import threading
import concurrent.futures
import time


class Boats:
    def __init__(self, name, port_object):
        # Attributes that make the boat know the other instances.
        self.model = "Cargo"  # Specify that it is a cargo boat
        self.name = name  # Name of the boat
        self.port = port_object  # Port Object

        # Attributes that make the boat know its own state.
        self.size = None  # Size of the boat
        self.cargo = None  # Loading zone that the boat needs
        self.active = False  # If the boat is active or not
        self.gasoline = None  # Gasoline level of the boat

        # Attributes that modify during the execution.
        self.priority = None  # Priority in the queue

    def delay_in_arriving(self):
        while not self.active:
            time.sleep(random.randint(1, 4))
            if random.randint(1, 3) == 2:
                self.active = True
        print(f"Boat {self.name} has arrived.")

    def get_into_queue(self):
        self.port.entrance_queue_locker.acquire()
        self.port.entrance_queue.append(self)
        self.priority = self.port.entrance_queue.index(self)
        self.port.entrance_queue_locker.release()
        print(f"Boat {self.name} has entered the queue.")

    def priority_check(self):  # If it is not the first in line, it is not going in.
        while self.priority != 0:
            time.sleep(3)
            self.priority = self.port.entrance_queue.index(self)

    def out_of_queue(self):
        self.port.entrance_queue_locker.acquire()
        self.port.entrance_queue.remove(self)
        self.port.entrance_queue_locker.release()
        print(f"Boat {self.name} has left the queue.")

    def simulation(self):
        self.delay_in_arriving()
        self.get_into_queue()
        self.priority_check()
        time.sleep(5)
        self.out_of_queue()


class Cranes:
    def __init__(self, name, port):
        self.name = "Crane " + str(name)
        self.port = port
        self.active = False
        self.locker = threading.Lock()

    def simulation(self):
        self.port.crane_list.append(self)


class Transporter(Cranes):
    def __init__(self, name, port):
        Cranes.__init__(self, name, port)
        self.name = "Transporter " + str(name)

    def simulation(self):
        self.port.transporter_list.append(self)


class Port:
    def __init__(self):
        # Attributes to keep track of the workers.
        self.workers_in_crane = 0  # Number of workers in the crane
        self.workers_in_transporter = 0  # Number of workers in the transporter
        self.workers_in_control = 0  # Number of workers in the controlling
        self.crane_list = []  # List of cranes in use
        self.transporter_list = []  # List of transporters in use

        # FOR BOATS
        self.entrance_queue = []
        self.entrance_queue_locker = threading.Lock()


class Worker:
    def __init__(self, name, port_object):
        self.name = "Worker " + str(name)
        self.port = port_object
        self.job = None
        self.active = False
        self.item = None
        self.job_designation()

    def job_designation(self):
        if self.port.workers_in_control == 0:
            self.job = "Control"
            self.port.workers_in_control += 1
            print("A worker has been designated as a controller.")
        elif self.port.workers_in_crane > self.port.workers_in_transporter and self.port.workers_in_transporter < len(self.port.transporter_list):
            self.job = "Transporter"
            self.port.workers_in_transporter += 1
        elif self.port.workers_in_crane <= self.port.workers_in_transporter and self.port.workers_in_crane < len(self.port.crane_list):
            self.job = "Crane"
            self.port.workers_in_crane += 1
        else:
            self.job = None
            print(f"There are no more jobs available for {self.name}.")

    def work(self, start):
        while self.active:
            time.sleep(random.randint(1, 3))
            if time.time() - start >= 20 and time.time() - start <= 22:
                self.active = False
                print(f"{self.name} has taken a break.")
                time.sleep(3)
                print(f"{self.name} has returned to work with {self.item.name}.")
                self.active = True
            if time.time() - start >= 50:
                self.active = False
                print(f"{self.name} has finished working.")
                break

    def simulation(self):
        if self.job == "Crane":
            wanted_list = self.port.crane_list
        elif self.job == "Transporter":
            wanted_list = self.port.transporter_list
        elif self.job == "Control":
            wanted_list = None
            self.active = True
            self.work(time.time())
        else:
            wanted_list = None
            exit()

        for item in wanted_list:
            if item.locker.locked():
                continue  # If the item is locked, it means that it is being used by another worker.

            else:
                item.locker.acquire()
                start = time.time()
                self.active = True
                self.item = item
                self.item.active = True
                print(f"{self.name} has selected {self.item.name} to work with.")
                self.work(start)
                self.item.active = False
                item.locker.release()
                break


number_of_cranes = 3
number_of_transporters = 3
number_of_workers = 10
number_of_boats = 3
port = Port()

with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_cranes) as executor:
    crane_list = [Cranes(i+1, port) for i in range(number_of_cranes)]
    for index, crane in enumerate(crane_list):
        executor.submit(crane.simulation)
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_transporters) as executor:
        transporter_list = [Transporter(i+1, port) for i in range(number_of_transporters)]
        for index, transporter in enumerate(transporter_list):
            executor.submit(transporter.simulation)
        with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
            worker_list = [Worker(i+1, port) for i in range(number_of_workers)]
            for index, worker in enumerate(worker_list):
                executor.submit(worker.simulation)
            with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_boats) as executor:
                boat_list = [Boats(i + 1, port) for i in range(number_of_boats)]
                for index, boat in enumerate(boat_list):
                    executor.submit(boat.simulation)
