stroka = input("Введите строку из слов разделённых пробелом: \n")+" "

def make_first_letter_capital(stroka):
    slovo = ""
    for i in range(len(stroka)):
            if stroka[i] != " ":
                slovo = slovo + stroka[i] #o
            else:
                print(slovo.capitalize()+" ", end="")
                slovo = ""
"""
если символ в stroka не пробел, мы помещаем его в slovo
если символ в stroka пробел, выводим slovo, то есть то, что было до пробела с большой буквы
но делаем это в одной строке с помощью end="" но чтобы был пробел делаем +" "
"""
make_first_letter_capital(stroka)