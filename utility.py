# Импортируем необходимые компоненты
from telegram import ReplyKeyboardMarkup, KeyboardButton


# функция создает клавиатуру и ее разметку
def get_keyboard():
    contact_button = KeyboardButton('Отправить контакты', request_contact=True)
    location_button = KeyboardButton('Отправить геопозицию', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([['Начать', 'Анекдот'],
                                       [contact_button, location_button],
                                       ['Заполнить анкету', 'Картинки']
                                       ], resize_keyboard=True)  # добавляем кнопки
    return my_keyboard

