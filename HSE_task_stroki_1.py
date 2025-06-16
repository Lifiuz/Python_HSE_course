first_string = input("Введите слово \n")
second_string = input("Введите последовательность букв, а я посмотрю есть ли она в слове\n")
if first_string.find(second_string) == 0 and len(first_string) > 5:
    print ("Подходит")
else:
    print("Что то не так")