import math

x1 = int(input("Введите x1: "))
y1 = int(input("Введите y1: "))
x2 = int(input("Введите x2: "))
y2 = int(input("Введите y2: "))

def distance(x,y,xx,yy):
    return math.sqrt((xx - x)**2 + (yy - y)**2)

print(f"Расстояние между точками ({x1},{y1}) и ({x2},{y2}) равняется {distance(x1,y1,x2,y2)}")

"""
AB = √(x2 - x1)2 + (y2 - y1)2 - Расстояние между двумя точками d вычисляется как
квадратный корень из суммы квадратов разностей их координат: distance это считает

"""