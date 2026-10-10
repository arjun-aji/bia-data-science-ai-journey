# method overriding
class A:
    def func1(self):
        print("This is class A function1")
    def func(self):
        print("This is class A function2")

class B(A):
    def func3(self):
        print("This is class B function3")
    def func(self):
        print("This is class B function4")
        super().func() 
obj=B()
obj.func()