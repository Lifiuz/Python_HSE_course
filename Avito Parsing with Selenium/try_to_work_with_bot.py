
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import subprocess  # Для запуска внешних Python-скриптов

# 🔑 Токен бота
TOKEN = '8087040319:AAEVnet_HuhgndKneYaTgsH0HOWFPB1FdOU'

# Главное меню
def start(update: Update, context: CallbackContext):
    # Описание, которое увидит пользователь при запуске /start
    description = (
        "Это мой первый тестовый бот, созданный с помощью нейросетей.\n\n"
        "Сейчас он умеет делать поиск 1к квартир в Перми и выводить первые 50 результатов\n\n"
    )

    keyboard = [
        [InlineKeyboardButton("Поиск квартир в Перми", callback_data='menu_1')],
        #[InlineKeyboardButton("Меню 2", callback_data='menu_2')],
        #[InlineKeyboardButton("Меню 3", callback_data='menu_3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:  # Для случая команды /start
        update.message.reply_text(description, reply_markup=reply_markup)  # Добавляем описание
    elif update.callback_query:  # Для случая callback_query
        update.callback_query.edit_message_text(description, reply_markup=reply_markup)  # Редактируем сообщение


# Меню 1
def menu_1(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Запустить поиск 1к квартир в Перми", callback_data='run_try3')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text('Меню 1. Выберите действие:', reply_markup=reply_markup)

# Меню 2
def menu_2(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Скрипт 2", callback_data='run_script2')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text('Меню 2. Выберите действие:', reply_markup=reply_markup)

# Меню 3
def menu_3(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Скрипт 3", callback_data='run_script3')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text('Меню 3. Выберите действие:', reply_markup=reply_markup)

# Обработка нажатий кнопок
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'menu_1':
        menu_1(update, context)
    elif query.data == 'menu_2':
        menu_2(update, context)
    elif query.data == 'menu_3':
        menu_3(update, context)
    elif query.data == 'back_to_main':
        start(update, context)  # Возвращаемся в главное меню
    elif query.data == 'run_try3':
        # Запускаем скрипт 1
        subprocess.run(['python', 'try3.py'])
        query.edit_message_text(text="Скрипт запущен!")
    elif query.data == 'run_script2':
        # Запускаем скрипт 2
        subprocess.run(['python', 'script2.py'])
        query.edit_message_text(text="Скрипт 2 запущен!")
    elif query.data == 'run_script3':
        # Запускаем скрипт 3
        subprocess.run(['python', 'script3.py'])
        query.edit_message_text(text="Скрипт 3 запущен!")

# Основная функция
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))  # Начало работы
    dp.add_handler(CallbackQueryHandler(button_handler))  # Обработка нажатий кнопок

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
