# Polymorphism Example overloading
class A:
    def find_sum(self,a,b,c=None):
        if c is not None:
            print(a+b+c)
        else:
            print(a+b)
obj=A()
obj.find_sum(10,20)