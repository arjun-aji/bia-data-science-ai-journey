class Employee:
    def __init__(self,name,jobtitle,salary):
        self.name=name
        self.jobtitle=jobtitle
        self.salary=salary
        self.__bonus=5000

    def display_info(self):
        print(f"name:{self.name} jobtitle:{self.jobtitle} salary:{self.salary}")
    def print_bonus(self):
        print(self.__bonus)

emp1=Employee("Arjun","Data Scientist","15LPA")
emp1.display_info()
emp1.print_bonus()