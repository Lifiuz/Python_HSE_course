"""
Реализуйте следующую программу: Считывается строка, где слова разделены пробелом.
Программа проверяет, есть ли в этой строке слова с буквами в верхнем регистре.
Если такие слова есть, то программа приводит все буквы в таких словах к нижнему регистру и сохраняет в отдельный список.
В конце программа печатает отсортированный по алфавиту список со словами, которые были туда сохранены.
Если таких слов нет, программа печатает пустой список.
"""

new_string = []
input_string = input("Введите строку: ")
for word in input_string.split(" "):
    for char in word:
        if char.isupper():
            new_string.append(word.lower())
            break
new_string.sort()
print(new_string)