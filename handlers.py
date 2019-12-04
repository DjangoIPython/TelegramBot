# Импортируем необходимые компоненты
from bs4 import BeautifulSoup
from glob import glob
from random import choice
import requests

from emoji import emojize
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from mongodb import mdb, search_or_save_user, save_user_anketa, save_picture_name, save_file_id, save_like_dislike
from utility import get_keyboard
from utility import SMILE


# функция sms() будет вызвана пользователем при отправке команды start,
# внутри функции будет описана логика при ее вызове
def sms(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)  # получаем данные из базы данных
    print(user)
    smile = emojize(choice(SMILE), use_aliases=True)  # для ответа добавили emoji
    print('Кто-то отправил команду /start. Что мне делать?')  # вывод сообщения в консоль при отправки команды /start
    bot.message.reply_text('Здравствуйте, {}! \nПоговорите со мной {}!'
                           .format(bot.message.chat.first_name, smile), reply_markup=get_keyboard())  # отправляем ответ


# функция отправляет случайную картинку
def send_meme(bot, update):
    lists = glob('images/*')  # создаем список из названий картинок
    picture = choice(lists)  # берем из списка одну картинку
    image = save_picture_name(mdb, picture)  # получаем из базы данных словарь
    inl_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"👍 {image['like']}", callback_data=1),
        InlineKeyboardButton(f"👎 {image['dislike']}", callback_data=-1)
    ]])
    msg = update.bot.send_photo(
        chat_id=bot.message.chat.id,
        photo=open(picture, 'rb'),
        reply_markup=inl_keyboard)  # отправляем картинку и inline клавиатуру
    save_file_id(mdb, picture, msg)  #


def inline_button_pressed(bot, update):
    # print(bot.callback_query)
    query = bot.callback_query  # данные которые приходят после нажатия кнопки
    data = int(query.data)  # получаем данные нажатой кнопки (1 или -1)
    save_like_dislike(mdb, query, data)  # отправляем в бд
    update.bot.edit_message_caption(
        caption='Спасибо вам за ваш выбор!',
        chat_id=query.message.chat.id,
        message_id=query.message.message_id)  # уберем inline клавиатуру выведем текст


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


def anketa_start(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)  # получаем данные из базы данных
    if 'anketa' in user:
        text = """Ваш предыдущий результат:
        <b>Имя:</b> {name}
        <b>Возраст:</b> {age}
        <b>Оценка:</b> {evaluation}
        <b>Комментарий:</b> {comment}
        
Данные будут обновлены!
        Как вас зовут?
        """.format(**user['anketa'])
        bot.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())  # вопрос и убираем основную клавиатуру
        return "user_name"
    else:
        bot.message.reply_text(
            'Как вас зовут?', reply_markup=ReplyKeyboardRemove())  # вопрос и убираем основную клавиатуру
        return "user_name"  # ключ для определения следующего шага


def anketa_get_name(bot, update):
    update.user_data['name'] = bot.message.text  # временно сохраняем ответ
    bot.message.reply_text("Сколько вам лет?")  # задаем вопрос
    return "user_age"  # ключ для определения следующего шага


def anketa_get_age(bot, update):
    update.user_data['age'] = bot.message.text  # временно сохраняем ответ
    reply_keyboard = [["1", "2", "3", "4", "5"]]  # создаем клавиатуру
    bot.message.reply_text(
        "Оцените статью от 1 до 5",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=True))  # при нажатии клавиатура исчезает
    return "evaluation"  # ключ для определения следующего шага


def anketa_get_evaluation(bot, update):
    update.user_data['evaluation'] = bot.message.text  # временно сохраняем ответ
    reply_keyboard = [["Пропустить"]]  # создаем клавиатуру
    bot.message.reply_text("Напишите отзыв или нажмите кнопку пропустить этот шаг.",
                           reply_markup=ReplyKeyboardMarkup(
                               reply_keyboard, resize_keyboard=True, one_time_keyboard=True))  # клава исчезает
    return "comment"  # ключ для определения следующего шага


def anketa_comment(bot, update):
    update.user_data['comment'] = bot.message.text  # временно сохраняем ответ
    user = search_or_save_user(mdb, bot.effective_user, bot.message)  # получаем данные из базы данных
    anketa = save_user_anketa(mdb, user, update.user_data)  # передаем и получаем результаты анкеты
    print(anketa)
    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Возраст:</b> {age}
    <b>Оценка:</b> {evaluation}
    <b>Комментарий:</b> {comment}
    """.format(**update.user_data)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)  # текстовое сообщение с форматированием HTML
    bot.message.reply_text("Спасибо вам за комментарий!", reply_markup=get_keyboard())  # сообщение и возвр. осн. клаву
    return ConversationHandler.END  # выходим из диалога


def anketa_exit_comment(bot, update):
    update.user_data['comment'] = None
    user = search_or_save_user(mdb, bot.effective_user, bot.message)  # получаем данные из базы данных
    save_user_anketa(mdb, user, update.user_data)  # передаем результаты анкеты
    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Возраст:</b> {age}
    <b>Оценка:</b> {evaluation}""".format(**update.user_data)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)  # текстовое сообщение с форматированием HTML
    bot.message.reply_text("Спасибо!", reply_markup=get_keyboard())  # отправляем сообщение и возвращаем осн. клаву
    return ConversationHandler.END  # выходим из диалога


def dontknow(bot, update):
    bot.message.reply_text("Я вас не понимаю, выберите оценку на клавиатуре!")


