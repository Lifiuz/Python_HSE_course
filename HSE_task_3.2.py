a = int(input("Введите основание Δ: "))
b = int(input("Введите высоту Δ: "))
triangle_square = lambda a, b: (a*b)/2
print(f"Площадь Δ это основание на высоту попалам = {triangle_square(a,b)}")