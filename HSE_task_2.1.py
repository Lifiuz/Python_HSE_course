
print("Введите 2 целых числа, они не должны быть равны")
a = int(input("Введите число А: "))
b = int(input("Введите число В: "))

if a < b:
    for i in range(a, b + 1):
        print (i)
else:
    for i in range(a, b - 1, -1):
        print(i)
#Rasul