import subprocess
import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import threading
import time

TOKEN = 'token'

# Глобальные переменные
user_choices = {}  # Формат: {user_id: {'rooms': X, 'line_index': Y, 'ads_lines': []}}
subscribers = {}  # Формат: {user_id: rooms}


def start(update: Update, context: CallbackContext):
    """Обработка команды /start - показывает главное меню"""
    user_id = update.effective_user.id
    if user_id not in user_choices:
        user_choices[user_id] = {'rooms': 1, 'line_index': 0, 'ads_lines': []}
    main_menu(update, context)


def main_menu(update: Update, context: CallbackContext):
    """Показывает главное меню с основными опциями"""
    user_id = update.effective_user.id
    if user_id not in user_choices:
        user_choices[user_id] = {'rooms': 1, 'line_index': 0, 'ads_lines': []}

    text = (
        "Этот бот поможет вам снять квартиру в Перми\n\n"
        "Как известно, самые лучшие варианты на Авито быстро исчезают. Хорошие квартиры сдаются быстрее, чем вы о них узнаёте. "
        "Но теперь вы можете оформить подписку и получать уведомления, когда на Авито появляются новые объявления. "
        "Достаточно просто выбрать количество комнат, которое вам нужно и нажать оформить подписку\n\n"
        "Также вы можете прямо в боте посмотреть новые объявления. Для этого выберите количество комнат и нажмите начать поиск\n"
        "\nПоиск осуществляется по следующим параметрам: \n"
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
        [InlineKeyboardButton("Начать поиск", callback_data='start_search')],
        [InlineKeyboardButton("Отменить подписку", callback_data='cancel_subscription')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text(text, reply_markup=reply_markup)


def select_rooms(update: Update, context: CallbackContext):
    """Показывает меню выбора количества комнат"""
    text = "Выберите, сколько комнат должно быть в квартире."
    keyboard = [
        [InlineKeyboardButton("1 - комнатная", callback_data='room_1')],
        [InlineKeyboardButton("2 - комнатная", callback_data='room_2')],
        [InlineKeyboardButton("3 - комнатная", callback_data='room_3')],
        [InlineKeyboardButton("4 - комнатная", callback_data='room_4')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(text, reply_markup=reply_markup)


def set_rooms(update: Update, context: CallbackContext, rooms: int):
    """Устанавливает выбранное количество комнат для пользователя"""
    user_id = update.effective_user.id
    if user_id not in user_choices:
        user_choices[user_id] = {'rooms': rooms, 'line_index': 0, 'ads_lines': []}
    else:
        user_choices[user_id]['rooms'] = rooms
        user_choices[user_id]['line_index'] = 0

    print(f"Пользователь {user_id} выбрал {rooms}-комнатную квартиру")
    update.callback_query.answer(f"Вы выбрали {rooms}-комнатную квартиру")
    main_menu(update, context)


def start_search(update: Update, context: CallbackContext):
    """Начинает поиск объявлений по выбранному фильтру"""
    user_id = update.effective_user.id
    if user_id not in user_choices:
        user_choices[user_id] = {'rooms': 1, 'line_index': 0}

    rooms = user_choices[user_id]['rooms']
    file_path = f'output_scripts_parsing/parsing_output_{rooms}k.txt'

    print(f"Открываем файл: {file_path}")

    if not os.path.exists(file_path):
        update.callback_query.edit_message_text(
            f"Файл с результатами для {rooms}-комнатных квартир не найден: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines if line.strip()]
    user_choices[user_id]['ads_lines'] = lines
    user_choices[user_id]['line_index'] = 0
    show_next_block(update, context)


def show_next_block(update: Update, context: CallbackContext):
    """Показывает следующую порцию объявлений (5 штук)"""
    user_id = update.effective_user.id
    rooms = user_choices[user_id]['rooms']
    line_index = user_choices[user_id].get('line_index', 0)
    lines = user_choices[user_id].get('ads_lines', [])
    id_file = f'id_{rooms}k.json'

    # Берем блок из 40 строк (5 объявлений * 8 строк)
    next_block = lines[line_index:line_index + 40]

    try:
        with open(id_file, 'r', encoding='utf-8') as f:
            id_list = json.load(f)
    except:
        id_list = []

    ads = []
    current_ad = []
    ad_count = 0

    for line in next_block:
        # Пропускаем строки с дефисами
        if set(line.strip()) == {'-', ' '}:
            if current_ad:  # Если есть накопленное объявление
                # Обрабатываем описание (6-я строка)
                if len(current_ad) >= 6 and len(current_ad[5]) > 500:
                    current_ad[5] = current_ad[5][:497] + "..."

                # Добавляем ссылку и разделитель
                if ad_count < len(id_list):
                    current_ad.append(f"👉 Ссылка на объявление (https://avito.ru/{id_list[ad_count]})")
                    current_ad.append("- " * 50)
                ads.append('\n'.join(current_ad))
                current_ad = []
                ad_count += 1
            continue

        current_ad.append(line)

    # Добавляем последнее объявление
    if current_ad and ad_count < len(id_list):
        if len(current_ad) >= 6 and len(current_ad[5]) > 500:
            current_ad[5] = current_ad[5][:497] + "..."

        current_ad.append(f"👉 Ссылка на объявление (https://avito.ru/{id_list[ad_count]})")
        if (line_index + 40) < len(lines):
            current_ad.append("-" * 50)
        ads.append('\n'.join(current_ad))

    final_text = f"<b>Просмотр объявлений по фильтру:</b> {rooms}-комнатная\n\n" + '\n\n'.join(ads)

    # Формируем клавиатуру
    keyboard = []
    has_next = (line_index + 40) < len(lines)
    has_prev = line_index > 0

    if has_prev and has_next:
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='prev_block'),
                         InlineKeyboardButton("➡️ Дальше", callback_data='next_block')])
    elif has_prev:
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='prev_block')])
    elif has_next:
        keyboard.append([InlineKeyboardButton("➡️ Дальше", callback_data='next_block')])

    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(text=final_text[:4000], reply_markup=reply_markup, parse_mode='HTML')


def button_handler(update: Update, context: CallbackContext):
    """Обработчик всех callback-запросов от кнопок"""
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
    elif data == 'next_block':
        user_id = update.effective_user.id
        user_choices[user_id]['line_index'] += 40
        show_next_block(update, context)
    elif data == 'prev_block':
        user_id = update.effective_user.id
        user_choices[user_id]['line_index'] = max(user_choices[user_id]['line_index'] - 40, 0)
        show_next_block(update, context)
    elif data == 'create_subscription':
        handle_subscription(update, context)
    elif data == 'cancel_subscription':
        handle_unsubscribe(update, context)
    elif data == 'back_to_main':
        main_menu(update, context)


def handle_subscription(update: Update, context: CallbackContext):
    """Оформляет подписку на уведомления"""
    user_id = update.effective_user.id
    rooms = user_choices.setdefault(user_id, {'rooms': 1}).get('rooms', 1)

    subscribers[user_id] = rooms
    print(f"Пользователь {user_id} подписался на {rooms}-комнатные квартиры")

    context.bot.send_message(
        chat_id=user_id,
        text=f"✅ Вы подписались на уведомления по {rooms}-комнатным квартирам.\n"
             f"Бот будет проверять новые объявления каждые 10 минут."
    )


def handle_unsubscribe(update: Update, context: CallbackContext):
    """Отменяет подписку на уведомления"""
    user_id = update.effective_user.id
    if user_id in subscribers:
        del subscribers[user_id]
        print(f"Пользователь {user_id} отменил подписку")
        context.bot.send_message(chat_id=user_id, text="❌ Ваша подписка отменена.")
    else:
        context.bot.send_message(chat_id=user_id, text="ℹ️ У вас нет активной подписки.")


def run_parsing_scripts():
    """Запускает все скрипты парсинга по очереди"""
    scripts = [
        'Script_parsing_1k.py',
        'Script_parsing_2k.py',
        'Script_parsing_3k.py',
        'Script_parsing_4k.py'
    ]

    for script in scripts:
        try:
            print(f"Запускаем {script}...")
            result = subprocess.run(['python', script], check=True, capture_output=True, text=True)
            print(f"{script} выполнен успешно")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка в {script}: {e.stderr}")
        except Exception as e:
            print(f"Неожиданная ошибка при выполнении {script}: {e}")


def background_checker(bot):
    """Фоновая проверка обновлений (запускается в отдельном потоке)"""
    # Задержка перед первым запуском
    time.sleep(180)

    # Храним последние известные первые строки
    prev_first_lines = {1: None, 2: None, 3: None, 4: None}

    while True:
        print("\n=== Запуск проверки обновлений ===")

        # 1. Запускаем все скрипты парсинга
        run_parsing_scripts()

        # 2. Проверяем изменения для каждого типа квартир
        for rooms in range(1, 5):
            path = f'output_scripts_parsing/parsing_output_{rooms}k.txt'

            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        current_first_line = f.readline().strip()

                        # Если есть изменения
                        if prev_first_lines[rooms] and current_first_line != prev_first_lines[rooms]:
                            print(f"Найдены новые {rooms}-комнатные квартиры!")

                            # Отправляем уведомления подписчикам
                            for user_id, subscribed_rooms in subscribers.items():
                                if subscribed_rooms == rooms:
                                    try:
                                        bot.send_message(
                                            chat_id=user_id,
                                            text=f"🔔 Появились новые {rooms}-комнатные квартиры!\n"
                                                 f"Нажмите 'Начать поиск' чтобы посмотреть."
                                        )
                                        print(f"Уведомление отправлено {user_id}")
                                    except Exception as e:
                                        print(f"Ошибка отправки для {user_id}: {e}")

                        # Обновляем значение для следующей проверки
                        prev_first_lines[rooms] = current_first_line
                except Exception as e:
                    print(f"Ошибка чтения {path}: {e}")

        print("=== Следующая проверка через 10 минут ===")
        time.sleep(600)  # 10 минут


if __name__ == '__main__':
    print("Запуск бота...")
    print("Первая проверка через 3 минуты")

    # Запускаем фоновую проверку
    threading.Thread(
        target=lambda: background_checker(Updater(TOKEN, use_context=True).bot),
        daemon=True
    ).start()

    # Настраиваем и запускаем бота
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    print("Бот запущен и работает")
    updater.idle()