from pymongo import MongoClient
from settings import MONGO_DB
from settings import MONGODB_LINK

mdb = MongoClient(MONGODB_LINK)[MONGO_DB]  # переменная для работы с базой данных MongoDB


def search_or_save_user(mdb, effective_user, message):
    user = mdb.users.find_one({"user_id": effective_user.id})  # поиск в коллекции users по user.id
    if not user:  # если такого нет, создаем словарь с данными
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "chat_id": message.chat.id
        }
        mdb.users.insert_one(user)  # сохраняем в коллекцию users
    return user


# сохраняем - обновляем результаты анкеты и возвращаем результат
def save_user_anketa(mdb, user, user_data):
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'anketa': {'name': user_data['name'],
                             'age': user_data['age'],
                             'evaluation': user_data['evaluation'],
                             'comment': user_data['comment']
                             }
                  }
         }
    )
    return user


# сохраняем название картинки
def save_picture_name(mdb, picture):
    photo = mdb.photography.find_one({'name': picture})  # поиск картинки по названию файла
    if not photo:  # если такого нет, создаем словарь с данными
        photo = {'name': picture,
                 'file_id': None,
                 'like': 0,
                 'dislike': 0,
                 'user_id': []
                 }
        mdb.photography.insert_one(photo)  # сохраняем словарь в коллекцию photography
    return photo


# сохраняем file_id отправленной картинки
def save_file_id(mdb, picture, msg):
    mdb.photography.update_one(
        {'name': picture},
        {'$set': {'file_id': msg.photo[0].file_id}})


# счетчик like и dislike
def save_like_dislike(mdb, query, data):
    file_id = query.message.photo[0].file_id  # получаем file_id
    photo = mdb.photography.find_one({'file_id': file_id})  # поиск картинки по file_id
    if query.message.chat.id not in photo['user_id']:
        if data == 1:
            new_like = photo['like'] + data
            mdb.photography.update_one(
                {'file_id': file_id},
                {'$set': {'like': new_like}, '$addToSet': {'user_id': query.message.chat.id}})
        else:
            new_dislike = photo['dislike'] - data
            mdb.photography.update_one(
                {'file_id': file_id},
                {'$set': {'dislike': new_dislike}, '$addToSet': {'user_id': query.message.chat.id}})
