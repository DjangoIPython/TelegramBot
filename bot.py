# Импортируем необходимые компоненты
import logging

from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import Filters

from settings import TG_TOKEN
from settings import TG_API_URL
from handlers import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


# Создаем (объявляем) функцию main, которая соединяется с платформой Telegram
def main():
    # описываем функцию (тело функции)
    # создадим переменную my_bot, с помощью которой будем взаимодействовать с нашим ботом
    my_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)
    logging.info('Start bot')
    my_bot.dispatcher.add_handler(CommandHandler('start', sms))  # обработчик команды start
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Картинка 🏞'), send_meme))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Начать'), sms))  # обрабатываем текс кнопки
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Анекдот'), get_anecdote))  # обрабатываем текс кнопки
    my_bot.dispatcher.add_handler(MessageHandler(Filters.contact, get_contact))  # обработчик полученного контакта
    my_bot.dispatcher.add_handler(MessageHandler(Filters.location, get_location))  # обработчик полученной геопозиции

    my_bot.dispatcher.add_handler(CallbackQueryHandler(inline_button_pressed))

    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Заполнить анкету'), anketa_start)],
                            states={
                                "user_name": [MessageHandler(Filters.text, anketa_get_name)],
                                "user_age": [MessageHandler(Filters.text, anketa_get_age)],
                                "evaluation": [MessageHandler(Filters.regex('1|2|3|4|5'), anketa_get_evaluation)],
                                "comment": [MessageHandler(Filters.regex('Пропустить'), anketa_exit_comment),
                                            MessageHandler(Filters.text, anketa_comment)],
                            },
                            fallbacks=[MessageHandler(
                                Filters.text | Filters.video | Filters.photo | Filters.document, dontknow)]
                            )
    )
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))  # обработчик текстового сообщения
    my_bot.start_polling()  # проверяет о наличии сообщений с платформы Telegram
    my_bot.idle()  # бот будет работать пока его не остановят


if __name__ == "__main__":
    main()

