import random

guess_number = random.randint(1, 2)
guessed = int(input("Попробуйте угадать число от 1 до 10. Угадали с первого раза - 10 баллов. С десятого раза - 0\n"))
score = 10
while guessed != guess_number:
    if guessed > guess_number:
        print(f"Не угадали, меньше")
    else:
        print(f"Не угадали, больше")
    guessed = int(input("Попробуйте ввести число снова: "))
    score = score - 1
print(f"Да, было загадано {guess_number}. \nПопыток угадать: {11 - score}\nИгра окончена, вы набрали {score}/10 очков")
