class Car:
    def __init__(self,name,year):
        self.name=name
        self.year=year

    def start_engine(self):
        print("vroom vroom")
c1=Car("bmw","2010")
c2=Car("swift","2011")
print(c1)
print(c2)
print(c1.name)

