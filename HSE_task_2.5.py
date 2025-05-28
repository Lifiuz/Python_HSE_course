counf_of_zero = 0
n = int(input("Сколько чисел будем вводить "))
while n == 0:
    print ("Введите что нибудь больше нуля ")
    input(n)
for i in range (1,n + 1):
    m = int(input(f"Введите {i} число: "))
    if m == 0:
        counf_of_zero += 1
print (f"Количество введеных чисел равных нулю = {counf_of_zero}")