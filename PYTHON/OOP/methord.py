class A:
    def __init__(self,name,price):
        self.name=name
        self.price=price
    def __add__(self,other):
        total=p1.price+p2.price
        print(total)
p1=A("pen",10)
p2=A("pencil",20)
p1+p2