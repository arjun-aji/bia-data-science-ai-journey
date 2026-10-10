# abstraction method
from abc import ABC,abstractmethod
class Vehicle(ABC):
    def start_engine(self):
        print("Starting engine")
    def apply_brakes(self):
        print("Applying brakes")
    def stop_engine(self):
        print("Stopping engine")
    @abstractmethod
    def change_gear(self):
        pass
class Car(Vehicle):
    def open_sunroof(self):
        print("Opening sunroof")
    def change_gear(self):
        print("Changing gear in car")
class truck(Vehicle):
    def load_cargo(self):
        print("Loading cargo")
    def change_gear(self):
        print("Changing gear in truck")
c1=Car()
t1=truck()
c1.start_engine()
t1.load_cargo()
c1.change_gear()
t1.change_gear()