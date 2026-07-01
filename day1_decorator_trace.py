def deco(func):
    print("A")
    def wrapper():
        print("B")
        return func()
    print("C")
    return wrapper


@deco
def f():
    print("D")


print("---")
f()
