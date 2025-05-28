lesenka = ""
n = int(input("Введите число больше нуля "))
print()
while n == 0:
    print ("Введите что нибудь больше нуля ")
    input(n)
for i in range (1, n+1):
    lesenka += str(i)
    print (lesenka)
