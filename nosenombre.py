import threading


class Cranes:
    def __init__(self, name, mediator):
        self.name = "Crane " + str(name)
        self.active = False
        self.locker = threading.Lock()
        self.mediator = mediator
        self.append_to_list()

    def append_to_list(self):
        self.mediator.machines.append(self)


class Transporter(Cranes):
    def __init__(self, name, control):
        Cranes.__init__(self, name, control)
        self.name = "Transporter " + str(name)


class Worker:
    def __init__(self, name, mediator):
        self.name = "Worker " + str(name)
        self.mediator = mediator
        self.item = None

    def ask_machinery(self):
        self.mediator.machinery(self)
        if self.item == "None":
            print(f"No work for {self.name}")
        else:
            print(f"{self.name} is working at {self.item.name}")


class Control:
    def __init__(self):
        self.machines = []
        self.active_machines = self.machines

    def machinery(self, worker):
        for machine in self.machines:
            if not machine.locker.locked():
                worker.item = machine
                self.active_machines.remove(machine)
                break


control_section = Control()

for i in range(3):
    Cranes(i+1, control_section)
    Transporter(i+1, control_section)

for i in range(10):
    worker = Worker(i+1, control_section)
    worker.ask_machinery()

