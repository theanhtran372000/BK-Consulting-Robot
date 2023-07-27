def decorator(type):
    def wrapper(f):
        def inner(*args, **kwargs):
            print(args)
            print(kwargs)
            print(type)
            
            f(*args, **kwargs)
        return inner
    return wrapper

@decorator(type='Hello')
def f(a, b, c=1, d=2):
    print(a, b, c, d)
    
f(1, 2, c=3, d=4)