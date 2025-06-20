from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import subprocess
import os

# Токен бота
TOKEN = '8087040319:AAEVnet_HuhgndKneYaTgsH0HOWFPB1FdOU'

# Храним выбор пользователя (в реальных проектах — лучше использовать context.user_data)
user_choices = {}

# Команда /start: приветствие и кнопка перехода в главное меню
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Начать поиск квартир", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text("Добро пожаловать!", reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text("Добро пожаловать!", reply_markup=reply_markup)

# Главное меню: выбор комнат и запуск поиска
def main_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_choices[user_id] = {'rooms': 1}  # значение по умолчанию — 1 комната

    text = (
        "Этот бот поможет вам снять квартиру в Перми\n\n"
        "Как известно, самые лучше варианты на Авито быстро исчезают. Хорошие квартиры сдаются быстрее, чем вы о них узнаёте. "
        "Но теперь вы можете оформить подписку и получать уведомления, когда на Авито появляются новые объявления"
        "Достаточно просто выбрать количество комнат, которое вам нужно и нажать оформить подписку\n\n"
        "Также вы можете прямо в боте посмотреть новые объявления. Для этого выберите количество комнат и нажмите начать поиск\n"
        "Поиск осуществляется по следующим параметрам: \n"
        "+ Длительность: ищем на долгий срок (без посуточных)\n"
        "+ Город: Пермь\n"
        "+ Район: все 7 районов\n"
        "+ Арендадатели: только частные\n"
        "+ Тип жилья: только квартиры (не апартаменты)\n"
        "+ Сортировка: по свежести (новые вверху)\n"
        "Эти фильтры нельзя изменить!\n"
        "\nДля того чтобы начать работу:\n"
        "1. Выберите количество комнат в квартире\n"
        "2. Начните поиск и посмотрите что есть на авито\n"
        "3. Оформите подписку, чтобы не пропустить новые объявления\n"
        "\nАвтор: @pasta159"
    )
    keyboard = [
        [InlineKeyboardButton("Выбрать количество комнат", callback_data='select_rooms')],
        [InlineKeyboardButton("Создать подписку на новые объявления", callback_data='create_subscription')],
        [InlineKeyboardButton("Отменить подписку", callback_data='cancel_subscription')],
        [InlineKeyboardButton("Начать поиск квартир", callback_data='start_search')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(text, reply_markup=reply_markup)

# Меню выбора количества комнат
def select_rooms(update: Update, context: CallbackContext):
    text = (
        "Выберите, какие квартиры вам интересны?\n"
    )
    keyboard = [
        [InlineKeyboardButton("1 - комнатная + студии", callback_data='room_1')],
        [InlineKeyboardButton("2 - комнатная", callback_data='room_2')],
        [InlineKeyboardButton("3 - комнатная", callback_data='room_3')],
        [InlineKeyboardButton("4 - комнатная", callback_data='room_4')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(text, reply_markup=reply_markup)

# Устанавливает выбранное пользователем количество комнат и возвращает в главное меню
def set_rooms(update: Update, context: CallbackContext, rooms: int):
    user_id = update.effective_user.id
    user_choices[user_id]['rooms'] = rooms
    update.callback_query.answer(f"Вы выбрали {rooms}-комнатную квартиру")
    main_menu(update, context)

# Запускает соответствующий скрипт и показывает результат парсинга
def start_search(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    rooms = user_choices.setdefault(user_id, {'rooms': 1}).get('rooms', 1)

    # Сопоставление количества комнат со скриптом и файлом результатов
    script_map = {
        1: ('script1.py', 'file1.txt'),
        2: ('script2.py', 'file2.txt'),
        3: ('script3.py', 'file3.txt'),
        4: ('script4.py', 'file4.txt')
    }

    script_name, result_file = script_map.get(rooms, ('script1.py', 'file1.txt'))
    subprocess.run(['python', script_name])  # запуск скрипта

    # Проверяем наличие и читаем результат
    if os.path.exists(result_file):
        with open(result_file, 'r', encoding='utf-8') as f:
            content = f.read()
            text = (
                f"Вы выбрали {rooms}-комнатную квартиру."
                "Парсинг завершился успешно."
                "Ниже первые 5 объявлений. Напомню, что вывод отфильтрован по дате публикации.\n\n"
                f"{content}"
            )
    else:
        text = f"Вы выбрали {rooms}-комнатную квартиру."


# Обрабатывает все действия пользователя по callback_data
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == 'main_menu':
        main_menu(update, context)
    elif data == 'select_rooms':
        select_rooms(update, context)
    elif data == 'room_1':
        set_rooms(update, context, 1)
    elif data == 'room_2':
        set_rooms(update, context, 2)
    elif data == 'room_3':
        set_rooms(update, context, 3)
    elif data == 'room_4':
        set_rooms(update, context, 4)
    elif data == 'start_search':
        start_search(update, context)
    elif data == 'create_subscription':
        handle_subscription(update, context)
    elif data == 'cancel_subscription':
        handle_unsubscribe(update, context)
    elif data == 'back_to_main':
        main_menu(update, context)

def handle_subscription(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    rooms = user_choices.setdefault(user_id, {'rooms': 1}).get('rooms', 1)
    subscribers[user_id] = rooms  # добавляем в список подписчиков
    context.bot.send_message(chat_id=user_id, text=f"Вы подписались на уведомления по {rooms}-комнатным квартирам. Проверка будет происходить каждые 10 минут.")


import threading
import time

# Храним подписчиков: user_id -> rooms
subscribers = {}

def handle_unsubscribe(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in subscribers:
        del subscribers[user_id]
        context.bot.send_message(chat_id=user_id, text="Ваша подписка отменена.")
    else:
        context.bot.send_message(chat_id=user_id, text="У вас не было активной подписки.")


# Фоновый цикл, проверяющий подписки каждые 10 минут
def background_subscription_checker(bot):
    while True:
        for user_id, rooms in subscribers.items():
            script_map = {
                1: 'script5.py',
                2: 'script6.py',
                3: 'script7.py',
                4: 'script8.py'
            }
            script_name = script_map.get(rooms, 'script5.py')

            try:
                result = subprocess.check_output(['python', script_name], stderr=subprocess.STDOUT, text=True).strip().lower()
                if result == 'true':
                    bot.send_message(chat_id=user_id, text="По вашей подписке есть новые объявления! Скорее запускайте поиск")
            except subprocess.CalledProcessError as e:
                bot.send_message(chat_id=user_id, text="Ошибка в фоновом процессе подписки:" + e.output)
        time.sleep(600)  # каждые 10 минут

# Запуск бота и регистрация обработчиков
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))  # команда /start
    dp.add_handler(CallbackQueryHandler(button_handler))  # кнопки

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    threading.Thread(target=lambda: background_subscription_checker(Updater(TOKEN, use_context=True).bot), daemon=True).start()
    main()
