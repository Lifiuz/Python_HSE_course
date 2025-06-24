import subprocess
import os
import json
import threading
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Токен бота
TOKEN = '8087040319:AAEVnet_HuhgndKneYaTgsH0HOWFPB1FdOU'

# Храним выбор пользователя и подписчиков
user_choices = {}
subscribers = {}
last_known_ids = {}

# Команда /start

def start(update: Update, context: CallbackContext):
    main_menu(update, context)

# Главное меню

def main_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in user_choices:
        user_choices[user_id] = {'rooms': 1}

    text = (
        "Этот бот поможет вам снять квартиру в Перми\n\n"
        "Как известно, самые лучшие варианты на Авито быстро исчезают. Хорошие квартиры сдаются быстрее, чем вы о них узнаёте. "
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
        [InlineKeyboardButton("Создать подписку", callback_data='create_subscription')],
        [InlineKeyboardButton("Отменить подписку", callback_data='cancel_subscription')],
        [InlineKeyboardButton("Начать поиск", callback_data='start_search')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text(text, reply_markup=reply_markup)

# Выбор комнат

def select_rooms(update: Update, context: CallbackContext):
    text = "Выберите, сколько комнат должно быть в квартире."
    keyboard = [
        [InlineKeyboardButton("1 - комнатная + студии", callback_data='room_1')],
        [InlineKeyboardButton("2 - комнатная", callback_data='room_2')],
        [InlineKeyboardButton("3 - комнатная", callback_data='room_3')],
        [InlineKeyboardButton("4 - комнатная", callback_data='room_4')],
        [InlineKeyboardButton("Назад", callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(text, reply_markup=reply_markup)

# Сохраняем выбор комнат

def set_rooms(update: Update, context: CallbackContext, rooms: int):
    user_id = update.effective_user.id
    user_choices[user_id] = {'rooms': rooms}
    update.callback_query.answer(f"Вы выбрали {rooms}-комнатную квартиру")
    main_menu(update, context)

# Старт поиска — читаем 40 строк (5 объявлений по 8 строк)

def start_search(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    rooms = user_choices.get(user_id, {}).get('rooms', 1)

    file_path = f'output_scripts_parsing/parsing_output_{rooms}k.txt'
    id_path = f'id_{rooms}k.json'

    if not os.path.exists(file_path):
        update.callback_query.edit_message_text("Файл с результатами не найден.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() != '']

    with open(id_path, 'r', encoding='utf-8') as f:
        id_list = json.load(f)

    context.user_data['lines'] = lines
    context.user_data['ids'] = id_list
    context.user_data['index'] = 0

    show_ads(update, context)

def show_ads(update: Update, context: CallbackContext, previous=False):
    lines = context.user_data.get('lines', [])
    ids = context.user_data.get('ids', [])
    index = context.user_data.get('index', 0)

    if previous:
        index = max(0, index - 90)

    output_lines = lines[index:index + 50]
    ad_blocks = []
    ad_id_index = index // 8

    for i in range(0, len(output_lines), 8):
        ad_text = '\n'.join(output_lines[i:i + 7])
        link = f"https://avito.ru/{ids[ad_id_index]}" if ad_id_index < len(ids) else ""
        ad_blocks.append(f"{ad_text}\n\n👉 <a href='{link}'>Ссылка на объявление</a>")
        ad_id_index += 1

    if not ad_blocks:
        keyboard = [[InlineKeyboardButton("Главное меню", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text("Объявления закончились.", reply_markup=reply_markup)
        return

    final_text = '\n\n'.join(ad_blocks)
    if len(final_text) > 4000:
        final_text = final_text[:3990] + "… (обрезано)"

    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton("Предыдущие", callback_data='show_previous'))
    if index + 50 < len(lines):
        buttons.append(InlineKeyboardButton("Следующие", callback_data='show_more'))
    buttons.append(InlineKeyboardButton("Главное меню", callback_data='main_menu'))

    context.user_data['index'] = index + 50
    reply_markup = InlineKeyboardMarkup([buttons])

    update.callback_query.edit_message_text(
        text=final_text,
        reply_markup=reply_markup,
        parse_mode='HTML',
        disable_web_page_preview=True
    )

# Подписка

def handle_subscription(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    rooms = user_choices.get(user_id, {}).get('rooms', 1)
    subscribers[user_id] = rooms
    context.bot.send_message(chat_id=user_id, text=f"Вы подписались на уведомления по {rooms}-комнатным квартирам.")

def handle_unsubscribe(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in subscribers:
        del subscribers[user_id]
        context.bot.send_message(chat_id=user_id, text="Ваша подписка отменена.")
    else:
        context.bot.send_message(chat_id=user_id, text="У вас не было активной подписки.")

# Обработка кнопок

def button_handler(update: Update, context: CallbackContext):
    data = update.callback_query.data
    if data == 'main_menu':
        main_menu(update, context)
    elif data == 'select_rooms':
        select_rooms(update, context)
    elif data.startswith('room_'):
        rooms = int(data.split('_')[1])
        set_rooms(update, context, rooms)
    elif data == 'start_search':
        start_search(update, context)
    elif data == 'show_more':
        show_ads(update, context)
    elif data == 'show_previous':
        show_ads(update, context, previous=True)
    elif data == 'create_subscription':
        handle_subscription(update, context)
    elif data == 'cancel_subscription':
        handle_unsubscribe(update, context)

# Фоновый парсинг каждые 10 минут, с задержкой старта в 3 минуты

def run_parsing_scripts():
    scripts = [
        'Script_parsing_1k.py',
        'Script_parsing_2k.py',
        'Script_parsing_3k.py',
        'Script_parsing_4k.py',
    ]
    for script in scripts:
        try:
            subprocess.run(['python', script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении {script}: {e}")

    for rooms in [1, 2, 3, 4]:
        try:
            with open(f'id_{rooms}k.json', 'r', encoding='utf-8') as f:
                ids = json.load(f)
                last_known_ids[rooms] = ids[0] if ids else None
        except Exception as e:
            print(f"Ошибка при чтении id_{rooms}k.json: {e}")

    for user_id, rooms in subscribers.items():
        try:
            with open(f'id_{rooms}k.json', 'r', encoding='utf-8') as f:
                current_ids = json.load(f)
                current_first = current_ids[0] if current_ids else None
                if current_first and current_first != last_known_ids.get(rooms):
                    context_bot.send_message(chat_id=user_id, text=f"🔔 Появились новые объявления по {rooms}-комнатным квартирам! Запустите поиск.")
        except Exception as e:
            print(f"Ошибка при проверке подписки пользователя {user_id}: {e}")

# Поток фонового запуска

def background_runner():
    print("Ждём 3 минуты перед первым запуском парсинга...")
    time.sleep(180)
    while True:
        print("Запуск парсинг-скриптов...")
        run_parsing_scripts()
        time.sleep(600)

# Запуск бота

def main():
    global context_bot
    updater = Updater(TOKEN, use_context=True)
    context_bot = updater.bot
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    threading.Thread(target=background_runner, daemon=True).start()
    main()
