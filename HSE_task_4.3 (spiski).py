counter = 0
track_list = input("Введите список треков: ").lower()
search_word = input("По какому слову? ").lower()
for track in track_list.split(","):
    for word in track.split(" "):
        if search_word in word:
            counter += 1
            break
        elif word == "|":
            break
print(counter)
