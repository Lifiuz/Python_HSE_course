input_string = input("введите слово а я проверю, палиндром ли это\n")

def palindrom(stroka):
    reversed_word = stroka.lower()
    return reversed_word == stroka[::-1]

print(palindrom(input_string))