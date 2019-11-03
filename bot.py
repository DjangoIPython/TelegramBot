# Импортируем необходимые компоненты
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from settings import TG_TOKEN, TG_API_URL
from bs4 import BeautifulSoup
import requests


# функция sms() будет вызвана пользователем при отправке команды start,
# внутри функции будет описана логика при ее вызове
def sms(bot, update):
    print('Кто-то отправил команду /start. Что мне делать?')  # вывод сообщения в консоль при отправки команды /start
    bot.message.reply_text('Здравствуйте, {}! \nПоговорите со мной!'
                           .format(bot.message.chat.first_name), reply_markup=get_keyboard())  # отправляем ответ


# функция парсит анекдоты
def get_anecdote(bot, update):
    receive = requests.get('http://anekdotme.ru/random')  # отправляем запрос к странице
    page = BeautifulSoup(receive.text, "html.parser")  # подключаем html парсер, получаем текст страницы
    find = page.select('.anekdot_text')  # из страницы html получаем class="anekdot_text"
    for text in find:
        page = (text.getText().strip())  # из class="anekdot_text" получаем текс и убираем пробелы по сторонам
    bot.message.reply_text(page)  # отправляем один анекдот, последний


# функция parrot() отвечает темже сообщением которое ему прислали
def parrot(bot, update):
    print(bot.message.text)  # печатаем на экран сообщение пользователя
    bot.message.reply_text(bot.message.text)  # отправляем обратно текс который пользователь послал


# функция печатает и отвечает на полученный контакт
def get_contact(bot, update):
    print(bot.message.contact)
    bot.message.reply_text('{}, мы получили ваш номер телефона!'.format(bot.message.chat.first_name))


# функция печатает и отвечает на полученные геоданные
def get_location(bot, update):
    print(bot.message.location)
    bot.message.reply_text('{}, мы получили ваше местоположение!'.format(bot.message.chat.first_name))


# функция создает клавиатуру и ее разметку
def get_keyboard():
    contact_button = KeyboardButton('Отправить контакты', request_contact=True)
    location_button = KeyboardButton('Отправить геопозицию', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([['Начать', 'Анекдот'],
                                       [contact_button, location_button]], resize_keyboard=True)  # добавляем кнопки
    return my_keyboard


# Создаем (объявляем) функцию main, которая соединяется с платформой Telegram
def main():
    # описываем функцию (тело функции)
    # создадим переменную my_bot, с помощью которой будем взаимодействовать с нашим ботом
    my_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)
    my_bot.dispatcher.add_handler(CommandHandler('start', sms))  # обработчик команды start
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Начать'), sms))  # обрабатываем текс кнопки
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Анекдот'), get_anecdote))  # обрабатываем текс кнопки
    my_bot.dispatcher.add_handler(MessageHandler(Filters.contact, get_contact))  # обработчик полученного контакта
    my_bot.dispatcher.add_handler(MessageHandler(Filters.location, get_location))  # обработчик полученной геопозиции
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))  # обработчик текстового сообщения
    my_bot.start_polling()  # проверяет о наличии сообщений с платформы Telegram
    my_bot.idle()  # бот будет работать пока его не остановят


# Вызываем (запускаем) функцию main
main()


