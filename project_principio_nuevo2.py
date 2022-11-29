import random
import threading
import concurrent.futures
import time

class Boats:
    def __init__(self, name, port_object):
        # Attributes that make the boat know the other instances.
        self.model = "Cargo"  # Specify that it is a cargo boat
        self.name = "Boat " + str(name)  # Name of the boat
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
        print(f"{self.name} has arrived.")

    def get_into_queue(self):
        self.port.entrance_queue_locker.acquire()
        self.port.entrance_queue.append(self)
        self.priority = self.port.entrance_queue.index(self)
        self.port.entrance_queue_locker.release()
        print(f"{self.name} has entered the queue.")

    def priority_check(self):  # If it is not the first in line, it is not going in.
        # Here you need to ask the control system if the boat can enter the port.
        while self.priority != 0:
            time.sleep(3)
            self.priority = self.port.entrance_queue.index(self)

    def out_of_queue(self):
        self.port.entrance_queue_locker.acquire()
        self.port.entrance_queue.remove(self)
        self.port.entrance_queue_locker.release()
        print(f"{self.name} has left the queue.")

    def simulation(self):
        self.get_into_queue()
        while not self.port.entrance_confirmation(self):
            continue
        self.out_of_queue()


class Cranes:
    def __init__(self, name, port):
        self.name = "Crane " + str(name)
        self.port = port
        self.active = False
        self.locker = threading.Lock()
        self.simulation()

    def simulation(self):
        self.port.crane_list.append(self)


class Transporter(Cranes):
    def __init__(self, name, port):
        Cranes.__init__(self, name, port)
        self.name = "Transporter " + str(name)

    def simulation(self):
        self.port.transporter_list.append(self)


class Control:
    def __init__(self):
        # Attributes to keep track of the workers.
        self.crane_list = []  # List of cranes in use
        self.transporter_list = []  # List of transporters in use

        self.workers_in_crane = 0  # Number of workers in the crane
        self.workers_in_transporter = 0  # Number of workers in the transporter
        self.workers_in_control = 0  # Number of workers in the controlling

        # FOR BOATS
        self.entrance_queue = []
        self.entrance_queue_locker = threading.Lock()
        # _____________________________________________________________________
        self.active_cranes = []
        self.active_transporters = []

    def entrance_confirmation(self, boat) -> bool:
        if boat.priority != 0:
            time.sleep(3)
            boat.priority = self.entrance_queue.index(boat)

            return False

        else:
            return True


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

    def simulation(self):
        if self.job == "Crane":
            wanted_list = self.port.crane_list
        elif self.job == "Transporter":
            wanted_list = self.port.transporter_list
        else:
            wanted_list = None
            exit()

        for item in wanted_list:
            if item.locker.locked():
                continue  # If the item is locked, it means that it is being used by another worker.

            else:
                item.locker.acquire()
                self.active = True
                self.item = item
                self.item.active = True
                print(f"{self.name} will work on {self.item.name}")
                break


control = Control()
number_of_cranes = 3

for i in range(number_of_cranes):
    Cranes(i+1, control)
    Transporter(i+1, control)

number_of_workers = 5
number_of_boats = 1


with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
    worker_list = [Worker(i+1, control) for i in range(number_of_workers)]
    for index, worker in enumerate(worker_list):
        executor.submit(worker.simulation)
    time.sleep(2)
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_boats) as executor:
        boat_list = [Boats(i+1, control) for i in range(number_of_boats)]
        for index, boat in enumerate(boat_list):
            executor.submit(boat.simulation)