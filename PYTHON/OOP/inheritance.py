class Vehicle:
    def __init__(self,company,model,color):
        self.company=company
        self.model=model
        self.color=color
    def start_engine(self):
        print("Starting engine")
    def apply_brakes(self):
        print("Applying brakes")
class Car(Vehicle):
    def __init__(self,company,model,color,fuel):
        self.fuel=fuel
        super().__init__(company,model,color)
    def open_sunroof(self):
        print("Opening sunroof")
c1=Car("BMW","X5","Black","Petrol")
c1.start_engine()
c1.open_sunroof()
c1.apply_brakes()